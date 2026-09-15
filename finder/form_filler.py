import json
import os
from pathlib import Path
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

    def fill_application(self, job_id: str, tab_id: int) -> bool:
        job = self.tracker.get_job(job_id)
        if not job:
            return False
            
        profile = self.load_candidate_profile()
        resume_path = job.get("resume_path")
        
        # We inject a JS script to heuristic fill standard fields
        # MANDATORY SECURITY RULE: This script NEVER calls click() on submit buttons.
        js_filler = f"""
        (function() {{
            const profile = {json.dumps(profile)};
            
            // Basic heuristic matching for common form fields
            const inputs = document.querySelectorAll('input, textarea');
            for (let input of inputs) {{
                let name = (input.name || input.id || input.placeholder || '').toLowerCase();
                
                if (!name) continue;
                
                if (name.includes('name') && profile.name && !name.includes('company')) {{
                    input.value = profile.name;
                }} else if (name.includes('email') && profile.email) {{
                    input.value = profile.email;
                }} else if (name.includes('phone') || name.includes('mobile')) {{
                    if (profile.phone) input.value = profile.phone;
                }} else if (name.includes('linkedin') && profile.linkedin) {{
                    input.value = profile.linkedin;
                }} else if (name.includes('github') && profile.github) {{
                    input.value = profile.github;
                }} else if (name.includes('college') || name.includes('university')) {{
                    if (profile.college) input.value = profile.college;
                }} else if (name.includes('degree') && profile.degree) {{
                    input.value = profile.degree;
                }}
                
                // Dispatch input event to trigger any React/framework state updates
                input.dispatchEvent(new Event('input', {{ bubbles: true }}));
                input.dispatchEvent(new Event('change', {{ bubbles: true }}));
            }}
            return true;
        }})();
        """
        
        self.browser.execute_js(tab_id, js_filler)
        
        # If there's a file upload for resume
        if resume_path and os.path.exists(resume_path):
            # We attempt to find the file input
            self.browser.upload_file(tab_id, 'input[type="file"]', resume_path)
            
        # Update state to indicate form is filled and waiting for human review
        self.tracker.update_status(job_id, "FORM_FILLED")
        return True
