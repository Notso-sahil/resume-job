import pytest
from unittest.mock import MagicMock
from finder.job_scraper import JobScraper
from finder.browser_client import BrowserClient

@pytest.fixture
def mock_browser():
    return MagicMock(spec=BrowserClient)

@pytest.fixture
def scraper(mock_browser):
    return JobScraper(mock_browser)

def test_detect_platform(scraper):
    assert scraper.detect_platform("https://internshala.com/internship/detail/123") == "internshala"
    assert scraper.detect_platform("https://linkedin.com/jobs/view/123") == "linkedin"
    assert scraper.detect_platform("https://cuvette.tech/jobs") == "cuvette"
    assert scraper.detect_platform("https://unknown.com/jobs") is None

def test_classify_tier(scraper):
    assert scraper.classify_tier("Senior AI Engineer") == (1, 90)
    assert scraper.classify_tier("Machine Learning Intern") == (1, 90)
    assert scraper.classify_tier("Backend Developer") == (2, 70)
    assert scraper.classify_tier("Graphic Designer") == (3, 0)
    assert scraper.classify_tier("Unknown Technical Role") == (2, 70)

def test_scrape_detail_page_success(scraper, mock_browser):
    # Mocking the MCP return structure from execute_js
    mock_browser.execute_js.return_value = {
        "content": [{"text": '{"role_title": "SWE", "company_name": "Google", "url": "url", "stipend_raw": "20k", "jd_text": "description"}'}]
    }
    
    result = scraper.scrape_detail_page(1, "internshala")
    assert result is not None
    assert result["role_title"] == "SWE"
    assert result["company_name"] == "Google"

def test_scrape_detail_page_failure(scraper, mock_browser):
    mock_browser.execute_js.return_value = {"content": [{"text": "invalid json"}]}
    result = scraper.scrape_detail_page(1, "internshala")
    assert result is None
