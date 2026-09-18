"""
MindMesh Frontend - FastAPI Backend API Client

Handles HTTP interactions with the FastAPI backend service routes (`/api/v1/blueprints`),
with configurable API base URL and automatic fallback handling.
"""

import urllib.request
import urllib.parse
import json
from typing import Dict, Any, Tuple, Optional

class APIClient:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip("/")

    def check_health(self) -> Tuple[bool, str]:
        """Check if backend API health endpoint is reachable."""
        url = f"{self.base_url}/health"
        try:
            req = urllib.request.Request(url, method="GET")
            with urllib.request.urlopen(req, timeout=3) as resp:
                if resp.status == 200:
                    return True, "Backend Connected (200 OK)"
                return False, f"Backend returned HTTP {resp.status}"
        except Exception as e:
            # Try checking GET /api/v1/blueprints if /health is not registered
            try:
                alt_url = f"{self.base_url}/api/v1/blueprints"
                alt_req = urllib.request.Request(alt_url, method="GET")
                with urllib.request.urlopen(alt_req, timeout=3) as alt_resp:
                    if alt_resp.status == 200:
                        return True, "Backend Connected (/api/v1/blueprints)"
            except Exception:
                pass
            return False, f"Backend unreachable: {str(e)}"

    def create_blueprint(self, payload: Dict[str, Any], timeout: int = 180) -> Tuple[bool, Dict[str, Any], str]:
        """
        Calls POST /api/v1/blueprints with BlueprintRequest JSON payload.
        Returns: (success: bool, response_dict: dict, error_message: str)
        """
        url = f"{self.base_url}/api/v1/blueprints"
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
        """Calls GET /api/v1/blueprints to list saved blueprint run_ids."""
        url = f"{self.base_url}/api/v1/blueprints"
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
