"""main.py
Runs the syncing code."""
import io
import os.path
import tempfile
from utilities import WORKING_DIR, TEMPORARY_FILES_DIR, get_logger, get_config, get_tags, get_seen_files, update_seen_files
from notion_api.notion import NotionAPIClient
from notion_api.database_fields import NotionTitleDatabaseField, NotionMultiSelectDatabaseField, NotionRichTextDatabaseField, DATABASE_FIELDS as NOTION_DATABASE_FIELD_CLASSES
from notion_api.page_blocks import NotionPageEmbedBlock, NotionPageHeading2Block, NotionPageQuoteBlock, NotionPageURLBlock, NotionPageParagraphBlock
from google_drive.authorization import DriveAPIHandler
from tag_detector import TagDetector
from googleapiclient.http import MediaIoBaseDownload
from typing import Optional, Tuple, List
from post_sync import POST_SYNC_ACTIONS

import logging
# Get a logger
logger = get_logger(__name__)
# Get the config
CONFIG = get_config()
NOTION_CONFIG = CONFIG["notion"]
NOTION_AUTH_TOKEN = NOTION_CONFIG["auth_token"]
NOTION_DATABASE_ID = NOTION_CONFIG["upload_database_id"]
NOTION_DOCUMENT_NAME_FIELD_NAME = NOTION_CONFIG["document_name_field_name"]
NOTION_GOOGLE_DRIVE_ID_FIELD_NAME = NOTION_CONFIG["google_drive_id_field_name"]
# Load ptional Notion settings
NOTION_NEW_PAGE_ICON = NOTION_CONFIG.get("new_page_icon", None) # (icon is optional)
NOTION_NEW_PAGE_INFORMATION_BANNER = NOTION_CONFIG.get("include_information_banner", True) # (optional setting)
NOTION_NEW_PAGE_EMBED_DOCUMENT_INLINE = NOTION_CONFIG.get("embed_document_inline", True) # (optional setting)
NOTION_TAG_TYPES = NOTION_CONFIG["tag_types"]
GOOGLE_DRIVE_CONFIG = CONFIG["google_drive"]
GOOGLE_DRIVE_UPLOAD_FOLDER_ID = GOOGLE_DRIVE_CONFIG["upload_folder_id"]

# Clean up any temporary paths
temporary_files_removed = 0
for temporary_path in os.listdir(TEMPORARY_FILES_DIR):
    os.remove(os.path.join(TEMPORARY_FILES_DIR, temporary_path))
    temporary_files_removed+=1

if temporary_files_removed > 0:
    logger.info(f"Found {temporary_files_removed} temporary files to remove.")
else:
    logger.debug("No temporary files to remove.")

# Create API clients
notion = NotionAPIClient(NOTION_AUTH_TOKEN)
drive = DriveAPIHandler()
drive.authorize() # Ensure authorization

# Create a tag detector
tag_detector = TagDetector(get_tags())
logger.info("API clients created, all token stuff retrieved! ✨")

# List files in the Google Drive directory
files = drive.list_all_files_in_directory(GOOGLE_DRIVE_UPLOAD_FOLDER_ID)
number_of_files = len(files)
logger.info("Received {} {} to process...".format(
    number_of_files,
    'file' if number_of_files == 1 else 'files'
))

def get_file_details(file_object:dict, apply_tags:Optional[List[dict]]=None)->Tuple[str,str,str,str,List[str]]:
    """Retrieves all the file details that we need for linking the file.
    Also downloads the file to a temporary file path.

    :param file_object: Data for the file as a response dict returned by the Google API.

    :param apply_tags: If set, a list of tags to apply to the file regardless.

    :returns A tuple consisting of: The file ID, the target drive directory, the file title, a temporary path where the file
    is accessible, and the Notion tags for it."""
    # Get data for the file
    filename = file_object["name"]
    file_id = file_object["id"]
    file_extension = os.path.splitext(filename)[1]
    logger.info(f"Processing file {file_id} ({filename})...")
    # Get which directory to put it in
    target_google_drive_directory, notion_tags, file_title = tag_detector.get_drive_folder_from_filename(filename, apply_tags)
    logger.info(
        f"Found directory and tags for file {filename} ({file_id}): {target_google_drive_directory} and {notion_tags}.")
    # Download file
    # Even though Notion doesn't support it, the implementation of post-checks (see README.md)
    # hands over the temporary file so Notion can do stuff with it.
    # Create temporary path in temporary files directory for downloading
    temporary_path = tempfile.mktemp(suffix=file_extension, dir=TEMPORARY_FILES_DIR)
    # Prepare file for writing
    file = open(temporary_path, "wb")
    # Start downloading the file
    file_download = drive.api_client.files().get_media(fileId=file_id)
    downloader = MediaIoBaseDownload(file, file_download)
    done = False
    while not done:
        status, done = downloader.next_chunk()
        logger.info(f"Downloading file {file_id}... {round(status.progress() * 100, 2)}/100%")
    logger.info(f"File {file_id} downloaded to {temporary_path}.")
    return file_id, target_google_drive_directory, file_title, temporary_path, notion_tags

def link_file_to_notion(google_drive_file_id, file_title, notion_tags)->Tuple[str,str]:
    """Links a Google Drive file in Notion by creating a Notion page.

    :param google_drive_file_id: The file ID on Google Drive.

    :param file_title: The file title on Google Drive.

    :param notion_tags: A list of Notion tags to add."""
    file_link = f"https://drive.google.com/file/d/{google_drive_file_id}/view"
    logger.info(f"Google Drive link for {file_title} is {file_link}.")
    logger.info(f"Starting linking for {file_link} with Notion...")
    # Create a new page for the file
    new_page_parent = {"database_id": NOTION_DATABASE_ID}
    # Parse tags to create in Notion
    new_page_properties = {NOTION_DOCUMENT_NAME_FIELD_NAME: NotionTitleDatabaseField(file_title),
                           NOTION_GOOGLE_DRIVE_ID_FIELD_NAME: NotionRichTextDatabaseField(file_id)}  # Add what we already have
    for tag in notion_tags:
        # Get details for the tag
        tag_data = NOTION_TAG_TYPES[tag["type"]]
        # Get Notion type for the tag
        database_field_type = tag_data["notion_type"]
        # Create a database field with the details filed out
        database_field = NOTION_DATABASE_FIELD_CLASSES[database_field_type](tag["value"])
        new_page_properties[tag_data["name"]] = database_field
    logger.debug(f"Properties for new page are: {new_page_properties}.")
    logger.info("Creating new page on Notion...")
    # Generate page children
    page_children = []
    # Add banner saying this page is auto-generated if set
    if NOTION_NEW_PAGE_INFORMATION_BANNER:
        page_children.append(
            NotionPageQuoteBlock(
                "🤖 This page was automatically created by NotesTionSync."
            )
        )
    page_children.append(NotionPageParagraphBlock("You can find the file at the link below:"))
    # Add document information: a link to the file in the new page
    if NOTION_NEW_PAGE_EMBED_DOCUMENT_INLINE:
        page_children.append(
            NotionPageURLBlock(file_link)
        )
    else:
        page_children.append(
            NotionPageEmbedBlock(file_link)
        )
    new_page = notion.create_page(
        new_page_parent,
        new_page_properties,
        page_children=page_children, # Add everything to fill out the page with
        icon=NOTION_NEW_PAGE_ICON
    )
    notion_link = new_page["url"]
    logger.info(f"New Notion page created at: {notion_link}.")
    return file_link, notion_link

seen_files = initially_seen_files = get_seen_files()
seen_files_data:List[dict] = []
for file in files:
    file_id, target_google_drive_directory, file_title, file_temporary_path, notion_tags = get_file_details(file)
    # Move file to the directory it should be moved to
    logger.info("Moving file...")
    moving_response = drive.api_client.files().update(fileId=file_id, addParents=target_google_drive_directory, removeParents=GOOGLE_DRIVE_UPLOAD_FOLDER_ID).execute()
    logger.debug(f"The file was moved with response {moving_response}")
    # Now, link the file to Notion
    file_link, notion_link = link_file_to_notion(file_id, file_title, notion_tags)
    seen_files.append(file_id)
    update_seen_files(seen_files) # Update seen files
    seen_files_data.append({
        "file_google_drive_id": file_id,
        "file_title": file_title,
        "file_temporary_path": file_temporary_path,
        "file_google_drive_link": file_link,
        "notion_new_page_link": notion_link,
        "notion_tags": notion_tags
    })

# Next, we do a reverse check. It's a chance someone moved documents directly
# to the folders instead to the "incoming scan" folders.
# Therefore, we scan all the files in the folders that the script is configured
# to move files to and if we discover anything new, we add it to Notion.
def get_reverse_check_folder_ids(tags:dict):
    """Reverses the mapping file (tags.json5) for the reverse check (see above).

    :returns A mapping of folder IDs the tags belonging to that move folder ID."""
    folder_ids_to_tags = {}
    for tag_id, tag_data in tags.items():
        # Detect tag type: has subtags or not subtags.
        if "folder_id" in tag_data:
            folder_ids_to_tags[tag_data["folder_id"]] = tag_data["notion_tags"]
        else: # Recursively apply the function
            folder_ids_to_tags.update(get_reverse_check_folder_ids(tag_data))
    return folder_ids_to_tags

# Perform the actual reverse check
reverse_check_folder_ids = get_reverse_check_folder_ids(tag_detector.tag_mappings)
logger.debug(f"Reverse-checking the following folders: {reverse_check_folder_ids.keys()}")
for folder_id, folder_tags in reverse_check_folder_ids.items():
    logger.info(f"Reverse-checking folder {folder_id}...")
    # List the directory
    for folder_subfile in drive.list_all_files_in_directory(folder_id):
        # Only process .pdf files
        if folder_subfile["mimeType"] != "application/pdf":
            logger.debug(f"Ignoring file {folder_subfile['name']} (is not PDF)")
            continue
        elif folder_subfile["id"] in seen_files:
            logger.debug(f"Ignoring file {folder_subfile['id']} (is already seen)")
            continue
        file_id, target_google_drive_directory, file_title, file_temporary_path, notion_tags = get_file_details(folder_subfile,
                                                                                               folder_tags)
        logger.info(f"Found a non-seen file: {file_id}. Linking to Notion...")
        file_link, notion_link = link_file_to_notion(file_id, file_title, notion_tags)
        logger.info("Unseen file linked to Notion.")
        seen_files.append(file_id)
        seen_files_data.append({
            "file_google_drive_id": file_id,
            "file_title": file_title,
            "file_temporary_path": file_temporary_path,
            "file_google_drive_link": file_link,
            "notion_new_page_link": notion_link,
            "notion_tags": notion_tags
        })
        update_seen_files(seen_files) # Update seen files
logger.info("Notion sync completed. Running post-sync if enabled...")
POST_SYNC_CONFIG = CONFIG["post_sync"] if "post_sync" in CONFIG else None
if POST_SYNC_CONFIG is not None and POST_SYNC_CONFIG["enabled"]:
    logger.info("Running post-sync...")
    # Get all the enabled post-sync modules
    POST_SYNC_MODULES = POST_SYNC_CONFIG["enabled_modules"]
    for enabled_post_sync_module in POST_SYNC_MODULES: # For every enabled module
        if enabled_post_sync_module not in POST_SYNC_MODULES: # Validate module name
            logging.critical(f"The post sync module {enabled_post_sync_module} is not supported. Supported modules are: {POST_SYNC_MODULES}.")
        for seen_file in seen_files_data: # For every updated file
            post_sync_object = POST_SYNC_ACTIONS[enabled_post_sync_module](**seen_file)
            post_sync_object.run()
            logger.debug(f"Post-sync for file {seen_file['file_title']} completed.")
    logger.info("Post-sync completed.")
else:
    logger.info("No post-sync to be ran. Program completed.")