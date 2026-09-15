import pytest
from unittest.mock import patch, MagicMock
import os
from pathlib import Path
from finder.resume_integrator import ResumeIntegrator, ResumeBuilderError
from finder.state_tracker import StateTracker

@pytest.fixture
def mock_tracker():
    tracker = MagicMock(spec=StateTracker)
    tracker.get_job.return_value = {
        "job_id": "123",
        "company": "Test Co!",
        "role_title": "SWE",
        "jd_text": "Need Python and AWS"
    }
    return tracker

@pytest.fixture
def integrator(tmp_path, mock_tracker):
    return ResumeIntegrator(str(tmp_path), mock_tracker)

def test_slugify(integrator):
    assert integrator._slugify("Hello World!") == "hello_world"
    assert integrator._slugify("Test Co & Sons") == "test_co_sons"

def test_build_job_config(integrator, mock_tracker):
    job = mock_tracker.get_job("123")
    config = integrator._build_job_config(job)
    assert config["company_name"] == "Test Co!"
    assert "Python" in config["primary_languages"]
    assert len(config["target_keywords"]) >= 15

@patch('subprocess.run')
@patch('time.time')
@patch('time.sleep')
def test_generate_resume_success(mock_sleep, mock_time, mock_run, integrator, mock_tracker, tmp_path):
    mock_run.return_value = MagicMock(returncode=0)
    mock_time.side_effect = [0, 1] 
    
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    pdf_path = output_dir / "test_co_resume.pdf"
    pdf_path.touch()
    
    result_path = integrator.generate_resume("123")
    assert result_path == str(pdf_path.resolve())
    mock_tracker.update_status.assert_called_with("123", "TAILORED", result_path)

@patch('subprocess.run')
def test_generate_resume_subprocess_fail(mock_run, integrator, mock_tracker):
    mock_run.return_value = MagicMock(returncode=1, stderr="Error", stdout="")
    with pytest.raises(ResumeBuilderError, match="Resume builder failed"):
        integrator.generate_resume("123")

@patch('subprocess.run')
@patch('time.time')
@patch('time.sleep')
def test_generate_resume_timeout(mock_sleep, mock_time, mock_run, integrator, mock_tracker):
    mock_run.return_value = MagicMock(returncode=0)
    mock_time.side_effect = [0, 121]
    
    with pytest.raises(ResumeBuilderError, match="PDF not found after 120 seconds timeout"):
        integrator.generate_resume("123")
