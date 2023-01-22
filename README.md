# NotesTionSync

### (Notion-Notes-Sync)

This project is something I wrote for syncing my digitally scanned notes to [Notion](https://notion.so).
**It adds files from Google Drive to a Notion database with support for automatically sorting notes based of "tags"
set in their filename and configured by you!**

## Background

Since 2022, I have, both unconsciously and consciously, tried to improve my organizational workflow.
This has involved trying various services. Late 2022, I switched from exclusively using my [Rocketbook](https://getrocketbook.com/) for taking notes to also using a book made of regular paper
to make the pages in my [Rocketbook](https://getrocketbook.com/) last longer. A few months later, I also switched from using Obsidian to using Notion for taking notes.
In 2023, I'm trying to migrate to Notion and understand the powerful tool it is and also merge the two note-taking methods together, which is the scope of this project.

**Not interesting in background information? Start reading from here!**

[Rocketbook](https://getrocketbook.com/) has a great tagging & categorization interface, but when using the "traditional" notebook, it doesn't have that.
So I created a project that syncs `.pdf`-files from Google Drive to Notion with a tag system in the filename.
It's very dynamic, so you should be able to integrate it into your workflow too.

## How it works

1. Take notes in a book (or anywhere else) and put then in an "inbox"-type folder in Google Drive. Scan the note (or export it)
as a `.pdf` and upload it to this folder.
2. This script regularly iterates over the "inbox"-folder to find any incoming scans. If it does, it categorizes them based on any tags
and then moves them to other folders you have set up for easier categorization.
3. The script also checks if anyone has moved anything to the other categorization folders that it hasn't seen. This way, you can easily import documents
from other sources directly to Notion. (for example, I use the "inbox"-folder for the scans of my regular notebook: my [Rocketbook](https://getrocketbook.com/) already automatically publishes to the destination folders)
4. There is also a post-read hook technology implemented. What this means is that you can write your own pieces of code that run after all the files have been read.

And that's it!

## Installation

See [Installation and setup.md](Installation and setup.md) for full setup instructions.
Also see the example [script config](config.toml.example) and the example [tags config](tags.json5.example).

## Libraries used

The Notion API client library is written by me to access the functions I needed for this project.

The Google Drives API uses the API client described [here](https://developers.google.com/drive/api/quickstart/python).

## FAQ

### How do I set it up?
See [Installation and setup.md](Installation and setup.md). Honestly! It's a really long file. You'll probably figure out to do stuff.

### What are all these mentions of the "Rocketbook"? What does this project actually do?

This project syncs Google Drive files with Notion and applies tags (database fields set to certain values) 
as well as sorting in Google Drive by moving files to directories that each tag is mapped in. The tags are set up by you
and applies to the filename. The mentions of the Rocketbook is to explain how I use this project.

### Why not upload the files directly to Notion?

1. I use this partly with my Rocketbook where the app automatically has an integration that uploads pages to Google Drive.
2. Notion's API does not, at the time of this writing and at the time of creating this project, support file uploads.
3. I feel like Google Drive feels like a natural place to use as a file storage and Notion as a more of a relationship manager.