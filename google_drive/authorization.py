"""authorization.py
This file ensures that the Google Drive API is correctly authenticated.
If it isn't, it starts a live server."""
from utilities import get_logger, get_config, WORKING_DIR
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build, Resource
from googleapiclient.errors import HttpError
import os.path
logger = get_logger(__name__)
# Load parameters from config file
GOOGLE_DRIVE_CONFIG = get_config()["google_drive"]
GOOGLE_SCOPES = GOOGLE_DRIVE_CONFIG["scopes"]
CREDENTIALS_FILE = os.path.join(WORKING_DIR, GOOGLE_DRIVE_CONFIG["credentials_file"])
TOKEN_FILE = os.path.join(WORKING_DIR, GOOGLE_DRIVE_CONFIG["token_file"])

class DriveAPIHandler():
    def __init__(self):
        self.api_client = self.credentials = self.token = None
    def authorize(self) -> Resource:
        """Main function for ensuring that the user is authenticated with Google Drive.
        If not, it handles the authentication."""
        # Check if files exist
        if not os.path.exists(TOKEN_FILE):
            logger.info("Token file does not exist. Starting configuration flow...")
            # Start the configuration flow
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, GOOGLE_SCOPES)
            self.credentials = flow.run_local_server(port=80)
            logger.info("Configuration flow completed. Saving...")
            with open(TOKEN_FILE, "w") as token_file:
                token_file.write(self.credentials.to_json())
        else:
            logger.info("Credentials exist!")
        # Load credentials from file
        self.credentials = Credentials.from_authorized_user_file(TOKEN_FILE, GOOGLE_SCOPES)
        # Check if they need to be refreshed
        if not self.credentials.valid:
            # If they expired, validate that we have a refresh token.
            if self.credentials.expired and self.credentials.refresh_token:
                logger.info("Refreshing credentials...")
                self.credentials.refresh(Request())
                logger.info("Credentials refreshed.")
            else: # (This is not expeted)
                logger.critical(f"Missing refresh token for expired credentials. Try deleting the file {TOKEN_FILE} and trying again.")
        else:
            logger.info("Credentials OK: No need to re-retrieve anything.")
        logger.info("Returning API client...")
        self.api_client = build("drive", "v3", credentials=self.credentials) # Create client from scopes
        return self.api_client

    def list_all_files_in_directory(self, directory_id, fields="nextPageToken, files(id, name,mimeType)", next_page_token=None, previous_files=[]):
        list_files_kwargs = {
            "pageSize": 100,
            "fields": fields,
            "q": f"'{directory_id}' in parents"
        }
        if next_page_token is not None:
            list_files_kwargs["pageToken"] = next_page_token
        if previous_files is None:
            previous_files = []
        response = self.api_client.files().list(**list_files_kwargs).execute()
        # Check for response
        if "files" in response:
            previous_files.extend(response["files"])
            if "nextPageToken" in response: # Multiple files: apply recursion
                return self.list_all_files_in_directory(
                    directory_id,
                    fields=fields,
                    next_page_token=response["nextPageToken"],
                    previous_files=previous_files
                )
            return previous_files
        return []

