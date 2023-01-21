from .post_sync import PostSync
from .discord.post_sync_action import DiscordPostSync
from typing import Dict
# Define post-sync actions below
POST_SYNC_ACTIONS:Dict[str,PostSync] = {
    "discord": DiscordPostSync
}