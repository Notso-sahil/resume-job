import re
import json
from typing import Optional, Tuple, Dict, Any
from .browser_client import BrowserClient

PORTAL_PATTERNS = {
    "internshala": r"internshala\.com/(internship|job|internships)",
    "linkedin":    r"linkedin\.com/jobs",
    "cuvette":     r"cuvette\.tech",
    "wellfound":   r"wellfound\.com/jobs",
    "greenhouse":  r"boards\.greenhouse\.io",
    "lever":       r"jobs\.lever\.co",
}

TIER_1_KEYWORDS = ["ai engineer", "ml engineer", "machine learning", "genai",
                   "deep learning", "llm", "nlp", "computer vision", "ai researcher", "artificial intelligence"]

TIER_2_KEYWORDS = ["software engineer", "sde", "backend", "full stack", "frontend",
                   "python developer", "cloud", "devops", "data engineer", "developer"]

TIER_3_KEYWORDS = ["sales", "marketing", "hr", "human resource", "graphic design",
                   "content writer", "social media", "recruiter", "accountant"]

class JobScraper:
    def __init__(self, browser: BrowserClient):
        self.browser = browser

    def detect_platform(self, url: str) -> Optional[str]:
        for platform, pattern in PORTAL_PATTERNS.items():
            if re.search(pattern, url, re.IGNORECASE):
                return platform
        return None

    def is_detail_page(self, tab_id: int, url: str, platform: str) -> bool:
        if platform == "internshala":
            return "/internship/detail/" in url or "/job/detail/" in url or "-internship-in-" in url or "-job-in-" in url
        elif platform == "linkedin":
            return "/view/" in url
        return True

    def scrape_detail_page(self, tab_id: int, platform: str) -> Optional[Dict[str, Any]]:
        script = """
        (function() {
            try {
                let title = document.querySelector('h1')?.innerText || document.title;
                let company = '';
                let stipend = '';
                let jd = document.body.innerText;
                
                if (window.location.href.includes('internshala')) {
                    title = document.querySelector('.profile_on_detail_page')?.innerText || title;
                    company = document.querySelector('.company_name a, .company_name')?.innerText || '';
                    stipend = document.querySelector('.stipend')?.innerText || '';
                    let jdEl = document.querySelector('.internship_details, .job_details');
                    if (jdEl) jd = jdEl.innerText;
                } 
                else if (window.location.href.includes('linkedin')) {
                    title = document.querySelector('.job-details-jobs-unified-top-card__job-title h1, .top-card-layout__title')?.innerText || title;
                    company = document.querySelector('.job-details-jobs-unified-top-card__company-name a, .topcard__org-name-link')?.innerText || '';
                    stipend = document.querySelector('.job-details-jobs-unified-top-card__job-insight')?.innerText || '';
                    let jdEl = document.querySelector('.jobs-description__content, .description__text');
                    if (jdEl) jd = jdEl.innerText;
                }
                
                return JSON.stringify({
                    role_title: title ? title.trim() : '',
                    company_name: company ? company.trim() : '',
                    url: window.location.href,
                    stipend_raw: stipend ? stipend.trim() : '',
                    jd_text: jd ? jd.trim() : ''
                });
            } catch (e) {
                return JSON.stringify({error: e.toString()});
            }
        })();
        """
        
        result = self.browser.execute_js(tab_id, script)
        try:
            content = result.get("content", [])
            if content:
                text = content[0].get("text", "")
                if text:
                    # Since our JS returns JSON string, double decode might be needed depending on MCP tool response
                    # Usually text is a string representation of the JS return value.
                    # Since our JS returns a JSON.stringify string, text should be a JSON string.
                    # Sometimes quotes are escaped, let's load it safely
                    if text.startswith("'") and text.endswith("'"):
                        text = text[1:-1]
                    # Parse the outer JSON if the MCP serializes string returns as JSON string
                    try:
                        inner = json.loads(text)
                        if isinstance(inner, str):
                            data = json.loads(inner)
                        else:
                            data = inner
                    except json.JSONDecodeError:
                        data = json.loads(text)
                        
                    if isinstance(data, dict) and 'role_title' in data:
                        return data
        except Exception as e:
            pass
        return None

    def classify_tier(self, role_title: str) -> Tuple[int, int]:
        title_lower = role_title.lower()
        
        for kw in TIER_3_KEYWORDS:
            if kw in title_lower:
                return 3, 0
                
        for kw in TIER_1_KEYWORDS:
            if kw in title_lower:
                return 1, 90
                
        for kw in TIER_2_KEYWORDS:
            if kw in title_lower:
                return 2, 70
                
        return 2, 70
