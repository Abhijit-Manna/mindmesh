"""
MindMesh Frontend - FastAPI Backend API Client

Handles HTTP interactions and real-time SSE streaming with the FastAPI backend service routes
(`http://localhost:8000/api/v1/blueprints`).
"""

import urllib.request
import urllib.parse
import urllib.error
import json
from typing import Dict, Any, Tuple, Optional, Generator


class APIClient:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip("/")

    def check_health(self) -> Tuple[bool, str]:
        """Check if backend API health endpoint is reachable."""
        endpoints = ["/health", "/api/v1/health", "/api/v1/blueprints/list"]
        for endpoint in endpoints:
            url = f"{self.base_url}{endpoint}"
            try:
                req = urllib.request.Request(url, method="GET")
                with urllib.request.urlopen(req, timeout=3) as resp:
                    if resp.status in (200, 201):
                        return True, "Backend Connected (200 OK)"
            except Exception:
                continue
        return False, "Backend unreachable"

    def stream_blueprint(self, payload: Dict[str, Any], timeout: int = 300) -> Generator[Dict[str, Any], None, None]:
        """
        Connects to POST /api/v1/blueprints/stream via Server-Sent Events (SSE).
        Yields parsed JSON event objects in real-time as each agent executes.
        """
        url = f"{self.base_url}/api/v1/blueprints/stream"
        json_bytes = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=json_bytes,
            headers={
                "Content-Type": "application/json",
                "Accept": "text/event-stream"
            },
            method="POST"
        )

        try:
            with urllib.request.urlopen(req, timeout=timeout) as response:
                buffer = ""
                for raw_line in response:
                    line = raw_line.decode("utf-8")
                    if not line:
                        continue
                    
                    line_str = line.strip()
                    if line_str.startswith("data: "):
                        data_payload = line_str[6:].strip()
                        try:
                            event_data = json.loads(data_payload)
                            yield event_data
                        except json.JSONDecodeError:
                            continue
        except urllib.error.HTTPError as e:
            try:
                err_text = e.read().decode("utf-8")
                err_json = json.loads(err_text)
                detail = err_json.get("detail", str(e))
            except Exception:
                detail = str(e)
            yield {
                "event": "error",
                "error": f"HTTP {e.code}: {detail}",
                "message": f"Server error: {detail}"
            }
        except Exception as e:
            yield {
                "event": "error",
                "error": str(e),
                "message": f"Connection failed: {str(e)}"
            }

    def create_blueprint(self, payload: Dict[str, Any], timeout: int = 240) -> Tuple[bool, Dict[str, Any], str]:
        """
        Calls POST /api/v1/blueprints/generate with BlueprintRequest JSON payload.
        Returns: (success: bool, response_dict: dict, error_message: str)
        """
        url = f"{self.base_url}/api/v1/blueprints/generate"
        try:
            json_bytes = json.dumps(payload).encode("utf-8")
            req = urllib.request.Request(
                url,
                data=json_bytes,
                headers={"Content-Type": "application/json", "Accept": "application/json"},
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                resp_text = resp.read().decode("utf-8")
                data = json.loads(resp_text)
                return True, data, ""
        except urllib.error.HTTPError as e:
            try:
                err_body = e.read().decode("utf-8")
                err_json = json.loads(err_body)
                msg = err_json.get("detail") or err_json.get("message") or str(e)
            except Exception:
                msg = f"HTTP {e.code}: {e.reason}"
            return False, {}, msg
        except Exception as e:
            return False, {}, f"Connection failed: {str(e)}"

    def list_blueprints(self) -> Tuple[bool, Dict[str, Any], str]:
        """Calls GET /api/v1/blueprints/list to list saved blueprint run_ids."""
        url = f"{self.base_url}/api/v1/blueprints/list"
        try:
            req = urllib.request.Request(url, headers={"Accept": "application/json"}, method="GET")
            with urllib.request.urlopen(req, timeout=5) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                return True, data, ""
        except Exception as e:
            return False, {"total": 0, "run_ids": []}, str(e)

    def get_blueprint(self, run_id: str) -> Tuple[bool, Dict[str, Any], str]:
        """Calls GET /api/v1/blueprints/{run_id}."""
        url = f"{self.base_url}/api/v1/blueprints/{urllib.parse.quote(run_id)}"
        try:
            req = urllib.request.Request(url, headers={"Accept": "application/json"}, method="GET")
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                return True, data, ""
        except Exception as e:
            return False, {}, str(e)

    def delete_blueprint(self, run_id: str) -> Tuple[bool, Dict[str, Any], str]:
        """Calls DELETE /api/v1/blueprints/{run_id}."""
        url = f"{self.base_url}/api/v1/blueprints/{urllib.parse.quote(run_id)}"
        try:
            req = urllib.request.Request(url, headers={"Accept": "application/json"}, method="DELETE")
            with urllib.request.urlopen(req, timeout=5) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                return True, data, ""
        except Exception as e:
            return False, {}, str(e)

