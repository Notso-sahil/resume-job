import requests
import json
import uuid

class BrowseAIConnectionError(Exception):
    pass

class BrowserClient:
    def __init__(self, port: int = 12307):
        self.port = port
        self.base_url = f"http://127.0.0.1:{port}"
        self._session_id = None

    def health_check(self) -> bool:
        try:
            r = requests.get(f"{self.base_url}/ping", timeout=2)
            if r.status_code == 200:
                return True
        except requests.RequestException:
            pass
        try:
            r = requests.get(f"{self.base_url}/mcp", timeout=2)
            return True
        except requests.RequestException:
            return False

    def _initialize_session(self) -> str:
        payload = {
            "jsonrpc": "2.0",
            "id": 0,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "finder", "version": "1.0.0"}
            }
        }
        r = requests.post(f"{self.base_url}/mcp", json=payload, timeout=10)
        session_id = r.headers.get("mcp-session-id") or str(uuid.uuid4())
        notif = {"jsonrpc": "2.0", "method": "notifications/initialized", "params": {}}
        requests.post(f"{self.base_url}/mcp", json=notif, headers={"mcp-session-id": session_id}, timeout=5)
        return session_id

    def _get_session(self) -> str:
        if not self._session_id:
            self._session_id = self._initialize_session()
        return self._session_id

    def _call_tool(self, tool_name: str, args: dict) -> dict:
        if not self.health_check():
            raise BrowseAIConnectionError(f"Cannot connect to BrowseAI on port {self.port}")
        try:
            session_id = self._get_session()
        except Exception as e:
            raise BrowseAIConnectionError(f"MCP session init failed: {e}")
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {"name": tool_name, "arguments": args}
        }
        try:
            response = requests.post(f"{self.base_url}/mcp", json=payload, headers={"mcp-session-id": session_id}, timeout=30)
            if response.status_code == 400:
                self._session_id = None
                session_id = self._get_session()
                response = requests.post(f"{self.base_url}/mcp", json=payload, headers={"mcp-session-id": session_id}, timeout=30)
            response.raise_for_status()
            data = response.json()
            if isinstance(data, dict) and "error" in data:
                raise Exception(data["error"])
            return data.get("result", {})
        except requests.RequestException as e:
            raise BrowseAIConnectionError(f"BrowseAI communication failed: {e}")

    def get_open_tabs(self) -> list:
        res = self._call_tool("get_windows_and_tabs", {})
        try:
            content = res.get("content", [])
            if content:
                text = content[0].get("text", "")
                if text:
                    return json.loads(text)
        except (json.JSONDecodeError, KeyError, IndexError):
            pass
        return []

    def execute_js(self, tab_id: int, script: str) -> any:
        return self._call_tool("chrome_javascript", {"tabId": tab_id, "script": script})

    def navigate(self, tab_id: int, url: str):
        self._call_tool("chrome_navigate", {"tabId": tab_id, "url": url})

    def get_page_text(self, tab_id: int) -> str:
        res = self._call_tool("chrome_get_web_content", {"tabId": tab_id})
        try:
            return res.get("content", [])[0]["text"]
        except (KeyError, IndexError):
            return ""

    def fill_field(self, tab_id: int, selector: str, value: str):
        self._call_tool("chrome_fill_or_select", {"tabId": tab_id, "selector": selector, "value": value})

    def upload_file(self, tab_id: int, selector: str, path: str):
        self._call_tool("chrome_upload_file", {"tabId": tab_id, "selector": selector, "filePath": path})

    def screenshot(self, tab_id: int) -> str:
        res = self._call_tool("chrome_screenshot", {"tabId": tab_id})
        try:
            return res.get("content", [])[0]["text"]
        except (KeyError, IndexError):
            return ""

    def click(self, tab_id: int, selector: str):
        self._call_tool("chrome_click_element", {"tabId": tab_id, "selector": selector})
