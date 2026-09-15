import pytest
from unittest.mock import patch, MagicMock
import requests
from finder.browser_client import BrowserClient, BrowseAIConnectionError

@pytest.fixture
def client():
    return BrowserClient(port=12307)

@patch('requests.get')
def test_health_check_success(mock_get, client):
    mock_get.return_value.status_code = 200
    assert client.health_check() is True

@patch('requests.get')
def test_health_check_failure(mock_get, client):
    mock_get.side_effect = requests.ConnectionError("Connection refused")
    assert client.health_check() is False

@patch('finder.browser_client.BrowserClient.health_check')
def test_call_tool_connection_error(mock_health, client):
    mock_health.return_value = False
    with pytest.raises(BrowseAIConnectionError):
        client._call_tool("test_tool", {})

@patch('finder.browser_client.BrowserClient.health_check')
@patch('requests.post')
def test_call_tool_success(mock_post, mock_health, client):
    mock_health.return_value = True
    
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "jsonrpc": "2.0",
        "id": 1,
        "result": {"content": [{"type": "text", "text": '{"success": true}'}]}
    }
    mock_post.return_value = mock_response
    
    result = client._call_tool("get_windows_and_tabs", {})
    assert "content" in result
    assert result["content"][0]["text"] == '{"success": true}'

@patch('finder.browser_client.BrowserClient._call_tool')
def test_get_open_tabs(mock_call_tool, client):
    mock_call_tool.return_value = {
        "content": [{"type": "text", "text": '[{"tabId": 1, "url": "https://example.com"}]'}]
    }
    tabs = client.get_open_tabs()
    assert len(tabs) == 1
    assert tabs[0]["tabId"] == 1

@patch('finder.browser_client.BrowserClient._call_tool')
def test_execute_js(mock_call_tool, client):
    mock_call_tool.return_value = {"content": [{"text": "result"}]}
    res = client.execute_js(1, "console.log('hi')")
    mock_call_tool.assert_called_with("chrome_javascript", {"tabId": 1, "script": "console.log('hi')"})

@patch('finder.browser_client.BrowserClient._call_tool')
def test_navigate(mock_call_tool, client):
    client.navigate(1, "https://example.com")
    mock_call_tool.assert_called_with("chrome_navigate", {"tabId": 1, "url": "https://example.com"})

@patch('finder.browser_client.BrowserClient._call_tool')
def test_screenshot(mock_call_tool, client):
    mock_call_tool.return_value = {"content": [{"text": "base64_data"}]}
    res = client.screenshot(1)
    assert res == "base64_data"
    mock_call_tool.assert_called_with("chrome_screenshot", {"tabId": 1})
