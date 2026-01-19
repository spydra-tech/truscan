"""Interface for uploading findings to remote endpoints."""

from abc import ABC, abstractmethod
from typing import Optional

from ..models import ScanResult


class Uploader(ABC):
    """Abstract base class for uploading scan results."""

    @abstractmethod
    def upload(self, result: ScanResult, api_key: Optional[str] = None) -> bool:
        """
        Upload scan results to remote endpoint.

        Args:
            result: Scan result to upload
            api_key: Optional API key for authentication

        Returns:
            True if upload successful, False otherwise
        """
        pass


class StubUploader(Uploader):
    """Stub implementation that does not actually upload."""

    def __init__(self, endpoint: Optional[str] = None):
        """
        Initialize stub uploader.

        Args:
            endpoint: Optional endpoint URL (not used in stub)
        """
        self.endpoint = endpoint

    def upload(self, result: ScanResult, api_key: Optional[str] = None) -> bool:
        """
        Stub upload - just logs that it would upload.

        Args:
            result: Scan result to upload
            api_key: Optional API key (not used in stub)

        Returns:
            True (simulated success)
        """
        if self.endpoint:
            print(f"[Stub] Would upload {len(result.findings)} findings to {self.endpoint}")
        else:
            print(f"[Stub] Would upload {len(result.findings)} findings (no endpoint configured)")
        return True
