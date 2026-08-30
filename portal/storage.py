"""Django storage backend for a public Supabase Storage bucket."""

import os
import uuid
from pathlib import PurePosixPath
from urllib.error import HTTPError
from urllib.parse import quote
from urllib.request import Request, urlopen

from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import Storage
from django.core.exceptions import ImproperlyConfigured


class SupabaseStorage(Storage):
    """Store uploaded media in Supabase instead of the Render filesystem."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.project_url = os.getenv("SUPABASE_URL", "").rstrip("/")
        self.secret_key = os.getenv("SUPABASE_SECRET_KEY", "")
        self.bucket = os.getenv("SUPABASE_STORAGE_BUCKET", "")
        if not all((self.project_url, self.secret_key, self.bucket)):
            raise ImproperlyConfigured(
                "SUPABASE_URL, SUPABASE_SECRET_KEY, and "
                "SUPABASE_STORAGE_BUCKET must be set for Supabase Storage."
            )

    def _object_url(self, name):
        return f"{self.project_url}/storage/v1/object/{quote(self.bucket, safe='')}/{quote(name, safe='/')}"

    def _request(self, name, method="GET", data=None, content_type=None):
        headers = {
            "apikey": self.secret_key,
        }
        if content_type:
            headers["Content-Type"] = content_type
        request = Request(self._object_url(name), data=data, headers=headers, method=method)
        try:
            with urlopen(request, timeout=60) as response:
                return response.read()
        except HTTPError as error:
            if error.code == 404:
                return None
            detail = error.read().decode("utf-8", errors="replace")
            raise OSError(f"Supabase Storage {method} failed ({error.code}): {detail}") from error

    def get_available_name(self, name, max_length=None):
        path = PurePosixPath(name)
        suffix = f"_{uuid.uuid4().hex}{path.suffix}"
        return str(path.with_name(f"{path.stem}{suffix}"))

    def _save(self, name, content):
        data = content.read()
        self._request(
            name,
            method="POST",
            data=data,
            content_type=getattr(content, "content_type", None) or "application/octet-stream",
        )
        return name

    def _open(self, name, mode="rb"):
        if "r" not in mode:
            raise ValueError("SupabaseStorage only supports reading files through open().")
        data = self._request(name)
        if data is None:
            raise FileNotFoundError(name)
        return ContentFile(data, name=name)

    def exists(self, name):
        return self._request(name, method="HEAD") is not None

    def delete(self, name):
        self._request(name, method="DELETE")

    def url(self, name):
        return (
            f"{self.project_url}/storage/v1/object/public/"
            f"{quote(self.bucket, safe='')}/{quote(name, safe='/')}"
        )
