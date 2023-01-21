# NotesTionSync

### (Notion-Note-Sync)

This project is something I wrote for syncing my digitally scanned notes to [Notion](https://notion.so).

## Background

Since 2022, I have, both uncounciously and conciously, tried to improve my organizational workflow.
This have involved trying various services. Late 2022, I switched from exlusively using my Rocketbook for taking notes to also using a book made of regular paper
to make the pages on my Rocketbook last longer. A few months later, I also switched from using Obsidian to using Notion for taking notes.
In 2023, I'm trying to make the two together.

**Not interesting in background information? Start reading from here!**

Rocketbook had a great tagging & categorization interface, but when using the "traditional" notebook, it doesn't have that.
So I created a project that syncs `.pdf`-files from Google Drive to Notion with a tag system in the filename.
It's very dynamic, so you should be able to integrate it into your workflow too.

## How it works

1. Take notes in a book (or anywhere else) and put then in an "inbox"-type folder in Google Drive. Scan the note (or export it)
as a `.pdf` and upload it to this folder.
2. This script regularly iterates over the "inbox"-folder to find any incoming scans. If it does, it categorizes them based on any tags
and then moves them to other folders you have set up for easier categorization.
3. The script also checks if anyone has moved anything to the other categorization folders that it hasn't seen. This way, you can easily import documents
from other sources directly to Notion. (for example, I use the "inbox"-folder for the scans of my regular notebook: my Rocketbook already automatically publishes to the destination folders)
4. There is also a post-read hook technology implemented. What this means is that you can write your own pieces of code that run after all the files have been read.

And that's it!

## Installation

See [Installation and setup.md](Installation and setup.md) for full setup instructions.
Also see the example [script config](config.toml.example) and the example [tags config](tags.json5.example).

## Libraries used

The Notion API client library is written by me to access the functions I needed for this project.

The Google Drives API uses the API client described [here](https://developers.google.com/drive/api/quickstart/python).