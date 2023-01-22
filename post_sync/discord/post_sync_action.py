"""post_sync_action.py
Runs the Discord post_sync_action, which calls a webhook URL."""
import requests

from ..post_sync import PostSync, PostSyncException

class DiscordPostSync(PostSync):
    # Defaults
    POST_SYNC_MODULE_NAME = "discord"
    DEFAULT_EMBED_COLOR = 28679 # Hex color #007007, a deep green.
    DEFAULT_EMBED_TITLE = "✅Synced with Notion"
    DEFAULT_EMBED_MESSAGE_FORMAT = """I found a new file on Google Drive, `{title}`, that was automatically added to Notion.
    **File links:** [Google Drive]({drive_link}) | [Notion]({notion_link})"""
    def __init__(self, **kwargs):
        """Intializes the DiscordPostSync module. Pass file information to me as kwargs!"""
        super().__init__(sync_module_name=DiscordPostSync.POST_SYNC_MODULE_NAME,
                         requires_config=True,
                         required_config_attributes=[
                             "webhook_url"
                         ],
                         **kwargs)

    def format_embed_message(self, format:str, variables:dict)->str:
        """Formats the embed message using the dynamic parameters that it supports.

        :param format: The message format of the embed message.

        :param variables: The variables to include in the formatting. Normally, this would be the self variables
        of the DiscordPostSync object."""
        format_parameters = {
            "title": variables["file_title"],
            "drive_id": variables["file_google_drive_id"],
            "drive_link": variables["file_google_drive_link"],
            "notion_link": variables["notion_new_page_link"]
        }
        # Find all replacements
        format_kwargs = {} # Parameters to pass to the format function
        for format_parameter, replace_with in format_parameters.items():
            format_parameter_text = f"{format_parameter}"
            if format_parameter_text in format:
                format_kwargs[format_parameter] = replace_with
        # ...and apply them
        return format.format(**format_kwargs)

    def run(self) ->None:
        """Runs the Discord post-sync."""
        self.logger.info("Running Discord Post-sync...")
        webhook_url = self.module_config["webhook_url"]
        embed_color = self.module_config.get("embed_color", DiscordPostSync.DEFAULT_EMBED_COLOR)
        embed_title = self.module_config.get("embed_title", DiscordPostSync.DEFAULT_EMBED_TITLE)
        embed_message_format = self.module_config.get("embed_message_format", DiscordPostSync.DEFAULT_EMBED_MESSAGE_FORMAT)
        embed_message = self.format_embed_message(embed_message_format, self.__dict__) # Format the embed message
        # Generate the embed
        embed_to_send = {
            "title": embed_title,
            "color": embed_color,
            "description": embed_message
        }
        # ... and the request body
        request_body = {
            "embeds": [embed_to_send]
        }
        self.logger.info("Sending request to Discord...")
        self.logger.debug(f"Request info: URL: {webhook_url}, body: {request_body}")
        request = requests.post(webhook_url, json=request_body)
        # Check if request failed
        if request.status_code in [200, 204]:
            self.logger.info("Request sent to Discord.")
        else:
            raise PostSyncException(f"Unexpected status code returned from Discord: {request.status_code}. Response content: {request.content}")
        self.logger.info("Discord webhook finished running.")