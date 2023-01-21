# Post-syncing actions

For me, I wanted to create a notification when my files were synced with Notion.
So, I created a universal post-sync hook format which runs customizable code actions after a sync was completed.

To add your own, see the example [discord](discord/post_sync_action.py) post sync action and the [registering of post-syncs](__init__.py).
Also see the [available parameters on each post-sync](__init__.py).