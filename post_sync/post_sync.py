"""post_sync.py
Defines an example class for creating post syncs."""
from typing import List, Optional
from utilities import get_logger, get_config

# Create exception to identify errors in post-syncs
class PostSyncException(Exception):
    pass

class PostSync:
    def __init__(self, sync_module_name:str, requires_config:bool, required_config_attributes:Optional[List[str]], file_google_drive_id:str, file_title:str, file_temporary_path:str, file_google_drive_link:str, notion_new_page_link:str, notion_tags:List[dict])->None:
        """Initializes a PostSync object.

        :param sync_module_name: The name of the sync module. Should be set by the child class calling this.

        :param requires_config: If True, the module that derives this function requires a config for the module to be set.
        If it is missing, an exception will be raised.

        :param required_config_attributes: If set, a list of config keys required by the module config.

        :param file_google_drive_id: The Google Drive ID of the file.

        :param file_title: The title of the file without tags.

        :param file_temporary_path: The temporary path for the file.

        :param file_google_drive_link: A link to the file on Google Drive.

        :param notion_new_page_link: A link to the new page created on Notion.

        :param notion_tags: Applied notion tags for the file."""
        self.module_name = sync_module_name
        self.file_google_drive_id = file_google_drive_id
        self.file_title = file_title
        self.file_temporary_path = file_temporary_path
        self.file_google_drive_link = file_google_drive_link
        self.notion_new_page_link = notion_new_page_link
        self.notion_tags = notion_tags
        self.logger = get_logger(__name__)
        # Load post sync config if any.
        self.full_config = get_config()
        self.module_config = self.full_config["post_sync"][self.module_name] if self.module_name in self.full_config["post_sync"] else None
        # Check if config is missing and if it is required
        if self.module_config is None and requires_config:
            raise KeyError(f"The post-sync module {self.module_name} requires a configuration.")
        # If the config exists, but required attributes are missing, raise an error.
        elif requires_config and required_config_attributes:
            if not all([config_attribute in self.module_config for config_attribute in required_config_attributes]):
                raise KeyError(f"Missing configuration keys for the post-sync module {self.module_name}. Required keys are {required_config_attributes}.")

    def run(self)->None:
        """Runs the post sync action. Override me!"""
        # Do things here