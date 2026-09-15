import os
import pytest
from finder.state_tracker import StateTracker

@pytest.fixture
def db_path(tmp_path):
    db_file = tmp_path / "test_applications.db"
    yield str(db_file)
    if db_file.exists():
        os.remove(db_file)

@pytest.fixture
def tracker(db_path):
    return StateTracker(db_path)

def test_add_and_get_job(tracker):
    job = {
        'company': 'Google',
        'role_title': 'AI Engineer',
        'url': 'https://google.com/jobs/1',
        'platform': 'linkedin',
        'tier': 1,
        'tier_score': 90,
        'stipend_min': 50000,
        'stipend_raw': '50k INR/mo',
        'jd_text': 'Looking for an AI engineer'
    }
    job_id = tracker.add_job(job)
    assert job_id is not None
    
    retrieved = tracker.get_job(job_id)
    assert retrieved is not None
    assert retrieved['company'] == 'Google'
    assert retrieved['status'] == 'DISCOVERED'

def test_duplicate_job(tracker):
    job = {
        'company': 'Google',
        'role_title': 'AI Engineer',
        'url': 'https://google.com/jobs/1',
        'platform': 'linkedin',
        'tier': 1,
        'tier_score': 90,
        'stipend_min': 50000
    }
    job_id1 = tracker.add_job(job)
    job_id2 = tracker.add_job(job)
    
    assert job_id1 == job_id2
    assert tracker.is_duplicate(job_id1) is True

def test_update_status(tracker):
    job = {
        'company': 'DeepMind',
        'role_title': 'Researcher',
        'url': 'https://deepmind.com/jobs/1',
        'platform': 'internshala',
        'tier': 1,
        'tier_score': 90,
        'stipend_min': 80000
    }
    job_id = tracker.add_job(job)
    
    tracker.update_status(job_id, 'TAILORED', resume_path='/tmp/resume.pdf')
    updated = tracker.get_job(job_id)
    assert updated['status'] == 'TAILORED'
    assert updated['resume_path'] == '/tmp/resume.pdf'
    assert updated['applied_at'] is None
    
    tracker.update_status(job_id, 'FORM_FILLED')
    final = tracker.get_job(job_id)
    assert final['status'] == 'FORM_FILLED'
    assert final['applied_at'] is not None

def test_daily_count(tracker):
    job1 = {
        'company': 'A', 'role_title': 'A', 'url': 'A', 'platform': 'linkedin',
        'tier': 1, 'tier_score': 90, 'stipend_min': 50000
    }
    job2 = {
        'company': 'B', 'role_title': 'B', 'url': 'B', 'platform': 'linkedin',
        'tier': 1, 'tier_score': 90, 'stipend_min': 50000
    }
    
    id1 = tracker.add_job(job1)
    id2 = tracker.add_job(job2)
    
    assert tracker.get_daily_count() == 0
    
    tracker.update_status(id1, 'FORM_FILLED')
    assert tracker.get_daily_count() == 1
    
    tracker.update_status(id2, 'SUBMITTED')
    assert tracker.get_daily_count() == 2
