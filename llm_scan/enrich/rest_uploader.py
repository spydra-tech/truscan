"""REST API uploader for sending scan results to a remote server."""

import json
import logging
from typing import Optional

import requests

from ..models import ScanResult

logger = logging.getLogger(__name__)


class RESTUploader:
    """Uploader that sends scan results to a REST API endpoint."""

    def __init__(
        self,
        endpoint: str,
        api_key: Optional[str] = None,
        application_id: Optional[str] = None,
    ):
        """
        Initialize REST API uploader.

        Args:
            endpoint: API endpoint URL (e.g., "https://api.example.com/v1/scans")
            api_key: API key for authentication
            application_id: Application ID to associate with the scan
        """
        self.endpoint = endpoint
        self.api_key = api_key
        self.application_id = application_id

    def upload(self, result: ScanResult, api_key: Optional[str] = None) -> bool:
        """
        Upload scan results to REST API endpoint.

        Args:
            result: Scan result to upload
            api_key: Optional API key (overrides instance api_key if provided)

        Returns:
            True if upload successful, False otherwise
        """
        # Use provided api_key or fall back to instance api_key
        effective_api_key = api_key or self.api_key

        if not effective_api_key:
            logger.warning("No API key provided for upload")
            return False

        if not self.application_id:
            logger.warning("No application_id provided for upload")
            return False

        try:
            # Prepare payload
            payload = {
                "application_id": self.application_id,
                "findings": [f.to_dict() for f in result.findings],
                "scanned_files": result.scanned_files,
                "rules_loaded": result.rules_loaded,
                "scan_duration_seconds": result.scan_duration_seconds,
                "metadata": result.metadata,
            }

            # Prepare headers
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {effective_api_key}",
            }

            logger.info(f"Uploading {len(result.findings)} findings to {self.endpoint}")
            logger.debug(f"Payload size: {len(json.dumps(payload))} bytes")

            # Send POST request
            response = requests.post(
                self.endpoint,
                json=payload,
                headers=headers,
                timeout=30,  # 30 second timeout
            )

            # Check response
            if response.status_code == 200 or response.status_code == 201:
                logger.info(f"✓ Successfully uploaded results (status: {response.status_code})")
                return True
            else:
                logger.error(
                    f"Upload failed with status {response.status_code}: {response.text}"
                )
                return False

        except requests.exceptions.Timeout:
            logger.error("Upload request timed out")
            return False
        except requests.exceptions.ConnectionError as e:
            logger.error(f"Connection error during upload: {e}")
            return False
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error during upload: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error during upload: {e}", exc_info=True)
            return False
