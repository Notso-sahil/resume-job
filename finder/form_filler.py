import json
import os
import re
from pathlib import Path
from typing import Any, Dict
from finder.browser_client import BrowserClient
from finder.state_tracker import StateTracker


class FormFiller:
    def __init__(self, browser: BrowserClient, tracker: StateTracker, env_file: str = ".env"):
        self.browser = browser
        self.tracker = tracker
        self.env_file = Path(env_file)

    def load_candidate_profile(self) -> dict:
        profile = {}
        if self.env_file.exists():
            with open(self.env_file, "r", encoding="utf-8") as f:
                for line in f:
                    if "=" in line and not line.startswith("#"):
                        key, val = line.strip().split("=", 1)
                        if key.startswith("CANDIDATE_"):
                            profile[key.replace("CANDIDATE_", "").lower()] = val.strip()
        return profile

    # ------------------------------------------------------------------
    # Pre-fill sanitization
    # ------------------------------------------------------------------

    @staticmethod
    def _sanitize_phone(raw_phone: str) -> Dict[str, str]:
        """
        Split a free-form phone number (e.g. "+91 98765 43210") into a
        digits-only form for fields that reject anything else, and a
        human-readable display form for fields that accept full formatting.
        """
        digits = re.sub(r"\D", "", raw_phone or "")
        if not digits:
            return {"phone_raw": "", "phone_display": ""}

        if digits.startswith("91") and len(digits) == 12:
            country_code, national = "91", digits[2:]
        elif digits.startswith("1") and len(digits) == 11:
            country_code, national = "1", digits[1:]
        else:
            country_code, national = "", digits

        phone_raw = digits

        if country_code == "91" and len(national) == 10:
            phone_display = f"+91 {national[:5]} {national[5:]}"
        elif country_code == "1" and len(national) == 10:
            phone_display = f"+1 ({national[:3]}) {national[3:6]}-{national[6:]}"
        else:
            phone_display = f"+{digits}"

        return {"phone_raw": phone_raw, "phone_display": phone_display}

    def _sanitize_profile(self, profile: dict) -> dict:
        """Normalize raw .env-sourced profile values before they're injected into a page."""
        sanitized = dict(profile)

        if sanitized.get("name"):
            sanitized["name"] = " ".join(sanitized["name"].split()).title()

        if sanitized.get("email"):
            sanitized["email"] = sanitized["email"].strip().lower()

        if sanitized.get("phone"):
            sanitized.update(self._sanitize_phone(sanitized["phone"]))
        else:
            sanitized.setdefault("phone_raw", "")
            sanitized.setdefault("phone_display", "")

        return sanitized

    # ------------------------------------------------------------------
    # Field-matching JS
    # ------------------------------------------------------------------

    @staticmethod
    def _build_field_script(profile: dict, dry_run: bool) -> str:
        """
        Build the in-page JS that matches profile fields to form inputs.
        Injects setNativeValue to bypass React/Vue Virtual DOM setters.
        """
        return f"""
        (function() {{
            const profile = {json.dumps(profile)};
            const dryRun = {json.dumps(dry_run)};
            const filled = {{}};

            function setNativeValue(el, value) {{
                const proto = el.tagName === 'TEXTAREA'
                    ? window.HTMLTextAreaElement.prototype
                    : window.HTMLInputElement.prototype;
                const setter = Object.getOwnPropertyDescriptor(proto, 'value').set;
                setter.call(el, value);
                el.dispatchEvent(new Event('input', {{ bubbles: true }}));
                el.dispatchEvent(new Event('change', {{ bubbles: true }}));
            }}

            function fieldSignature(el) {{
                return [
                    el.name,
                    el.id,
                    el.placeholder,
                    el.getAttribute('aria-label'),
                    el.getAttribute('data-testid'),
                ].filter(Boolean).join(' ').toLowerCase();
            }}

            function fieldLabel(el) {{
                return el.name || el.id || el.placeholder ||
                    el.getAttribute('aria-label') || el.getAttribute('data-testid') ||
                    (el.type || 'field');
            }}

            function matchValue(el, sig) {{
                if (sig.includes('name') && !sig.includes('company') && !sig.includes('username')
                    && !sig.includes('file') && profile.name) {{
                    return profile.name;
                }}
                if (sig.includes('email') && profile.email) {{
                    return profile.email;
                }}
                if (sig.includes('phone') || sig.includes('mobile') || sig.includes('tel')) {{
                    if (!profile.phone_display && !profile.phone_raw) return null;
                    const pattern = el.getAttribute('pattern') || '';
                    const maxLength = el.maxLength;
                    const isDigitsOnly = pattern.includes('0-9') ||
                        (el.type === 'tel' && maxLength > 0 && maxLength <= 10);
                    return isDigitsOnly
                        ? (profile.phone_raw || profile.phone_display)
                        : (profile.phone_display || profile.phone_raw);
                }}
                if (sig.includes('linkedin') && profile.linkedin) return profile.linkedin;
                if (sig.includes('github') && profile.github) return profile.github;
                if ((sig.includes('college') || sig.includes('university')) && profile.college) {{
                    return profile.college;
                }}
                if (sig.includes('degree') && profile.degree) return profile.degree;
                return null;
            }}

            const candidates = document.querySelectorAll('input, textarea');
            for (const el of candidates) {{
                if (['file', 'hidden', 'submit', 'button', 'checkbox', 'radio'].includes(el.type)) {{
                    continue;
                }}
                const sig = fieldSignature(el);
                if (!sig) continue;

                const value = matchValue(el, sig);
                if (value === null || value === undefined || value === '') continue;

                filled[fieldLabel(el)] = value;
                if (!dryRun) {{
                    setNativeValue(el, value);
                }}
            }}

            const submitEl = document.querySelector('button[type="submit"], input[type="submit"]');
            if (submitEl) {{
                filled.__submit_selector = submitEl.id
                    ? '#' + CSS.escape(submitEl.id)
                    : (submitEl.name
                        ? submitEl.tagName.toLowerCase() + '[name="' + submitEl.name + '"]'
                        : 'button[type="submit"], input[type="submit"]');
            }}

            return filled;
        }})();
        """

    @staticmethod
    def _parse_js_result(result: Any) -> Dict[str, str]:
        try:
            content = result.get("content", [])
            if content:
                text = content[0].get("text", "")
                if text:
                    parsed = json.loads(text)
                    if isinstance(parsed, dict):
                        return parsed
        except (AttributeError, KeyError, IndexError, TypeError, json.JSONDecodeError):
            pass
        return {}

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def fill_application(self, job_id: str, tab_id: int) -> bool:
        job = self.tracker.get_job(job_id)
        if not job:
            return False

        profile = self._sanitize_profile(self.load_candidate_profile())
        resume_path = job.get("resume_path")

        fill_script = self._build_field_script(profile, dry_run=False)
        fill_result = self.browser.execute_js(tab_id, fill_script)
        fill_preview = self._parse_js_result(fill_result)

        if resume_path:
            fill_preview["Resume"] = os.path.basename(resume_path)

        self.tracker.update_fill_preview(job_id, fill_preview)

        if resume_path and os.path.exists(resume_path):
            self.browser.upload_file(tab_id, 'input[type="file"]', resume_path)

        self.tracker.update_status(job_id, "PENDING_CONFIRM")
        return True
