"""
drive_uploader.py

Uploads a finished image to a Google Drive folder using a service
account.

SETTINGS (change here if needed):
- SCOPES: Google Drive API access scope (upload-only, kept minimal)

REQUIRED ENVIRONMENT VARIABLES (set as GitHub Secrets):
- GDRIVE_SERVICE_ACCOUNT_JSON : the full service-account JSON key, as a string
- DRIVE_FOLDER_ID             : the ID of the destination Drive folder
"""

import os
import json
import tempfile

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

SCOPES = ["https://www.googleapis.com/auth/drive.file"]


def upload_to_drive(file_path, file_name):
    creds_json = json.loads(os.environ["GDRIVE_SERVICE_ACCOUNT_JSON"])
    folder_id = os.environ["DRIVE_FOLDER_ID"]

    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as tmp:
        json.dump(creds_json, tmp)
        tmp_path = tmp.name

    credentials = service_account.Credentials.from_service_account_file(tmp_path, scopes=SCOPES)
    service = build("drive", "v3", credentials=credentials)

    file_metadata = {"name": file_name, "parents": [folder_id]}
    media = MediaFileUpload(file_path, mimetype="image/png")

    uploaded_file = service.files().create(
        body=file_metadata, media_body=media, fields="id"
    ).execute()

    os.remove(tmp_path)
    return uploaded_file.get("id")
