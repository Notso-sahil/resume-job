import pytest
from unittest.mock import MagicMock, patch
from finder.form_filler import FormFiller
from finder.browser_client import BrowserClient
from finder.state_tracker import StateTracker

@pytest.fixture
def mock_browser():
    return MagicMock(spec=BrowserClient)

@pytest.fixture
def mock_tracker():
    tracker = MagicMock(spec=StateTracker)
    tracker.get_job.return_value = {
        "job_id": "123",
        "company": "Test Co",
        "resume_path": "/tmp/resume.pdf"
    }
    return tracker

@pytest.fixture
def filler(mock_browser, mock_tracker, tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("CANDIDATE_NAME=John Doe\nCANDIDATE_EMAIL=john@doe.com\n", encoding="utf-8")
    return FormFiller(mock_browser, mock_tracker, str(env_file))

def test_load_candidate_profile(filler):
    profile = filler.load_candidate_profile()
    assert profile["name"] == "John Doe"
    assert profile["email"] == "john@doe.com"

@patch('os.path.exists')
def test_fill_application(mock_exists, filler, mock_browser, mock_tracker):
    mock_exists.return_value = True
    
    result = filler.fill_application("123", 1)
    
    assert result is True
    # Ensure JS was executed
    mock_browser.execute_js.assert_called_once()
    
    # Ensure file upload was called
    mock_browser.upload_file.assert_called_once_with(1, 'input[type="file"]', '/tmp/resume.pdf')
    
    # Ensure status was updated
    mock_tracker.update_status.assert_called_once_with("123", "FORM_FILLED")

def test_security_constraint_no_submit_clicks():
    import ast
    from pathlib import Path
    
    # Read the source code of FormFiller
    source_path = Path(__file__).parent.parent / "form_filler.py"
    with open(source_path, "r", encoding="utf-8") as f:
        source_code = f.read()
        
    # Enforce constraint via AST parsing
    tree = ast.parse(source_code)
    
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Attribute):
                if node.func.attr == "click":
                    pytest.fail("Security Violation: Found click() call in FormFiller. Agent must NEVER autonomously submit forms.")
