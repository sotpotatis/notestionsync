# Installation and setup

This document will guide you to setting up your own note syncing with Notion. Its goal is being as complete as possible.

## Step 1: Clone the repository & Install the requirements

Clones the repository:
* `git clone https://github.com/sotpotatis/notestionsync`

Using Linux?
* `sudo apt install python3-testresources`

Installs the requirements:
* `cd notestionsync && pip install -r requirements.txt`

## Step 2: Grab a Notion token

You need a Notion API token for accessing your pages. Go to https://www.notion.so/my-integrations and click on "New Integration".
Add some information and copy the access token that it gives you.

## Step 3: Grab Google Drive credentials

Follow [this guide](https://developers.google.com/drive/api/quickstart/python#enable_the_api) for getting the credentials for Google Drive.

> **Note**: You only have to follow the steps under the *Enable the API* and *Authorize credentials for a desktop application* headings
> to enable the API.

Move the output `credentials.json` file into the directory that you downloaded this project to.

## Step 4: Basic Notion setup

Make sure you understand what this script requires. It requires a database where the pages will be added.
Whether you want to create a new one or not - that's totally up to you.
The database needs at least the following:
1. A page name field of type `Title`
2. A page Google Docs ID field of type `Rich Text`

If you want to implement the "tagging system", which is quite an essential feature about this project, you should also create some tags.
Here: you have total freedom as long as you use the supported type: `Multi-Select`. As an example, I have tags for the subject of my notes and the type (lecture notes or assignment).

## Step 5: Giving access

For the integration to work, this step is very important! Go to the Notion database you want to use, click on the three dots and then "Add connection",
and share the database view with the application you created in the first step. If not, the integration will not work!

<img alt="Screenshot showing where to add the app" src="instruction_screenshots/App addition screenshots.png" width="50%"/>

## Step 6: Retrieving details for the configuration file

We need some details. Let's grab them.

### Notion database ID

Go to the database you want to use together with the tool and extract the ID from this part of the URL:

`https://www.notion.so/<Your Workspace Name>/<ID is here>?<Don't worry about anything after the exclamation mark if any>`

### Tags

If you're going to use tags with the project, you need their ID. The easiest way is to add a new temporary page, apply all tags you need IDs for,
open the page by maximizing it, copy its ID by extracting it from the URL: `https://www.notion.so/<Your-Workspace-Name>/<Page-name>-<Page ID>`, and then retrieve the page using something like cURL:

```
curl --request GET \
  --url https://api.notion.com/v1/pages/<Page ID>/ \
  --header 'Authorization: Bearer <Your Notion Access Token Here>'
  --header 'Notion-Version: 2021-08-16'
```

In the response, you should be able to extract the IDs of all the tags by simply searching for the tag name. In the example below, I was looking for my tag name for the course
`Ledarskap och organisation` (Leadership & organization), so I simply searched the response for it:

![Screenshots showing an example of how to find the tags](instruction_screenshots/Tag%20finding.png)

### Google Drive upload Folder ID

You're going to use folder IDs more if you use the tagging system for categorization to different folders which is documented more below.
However, you need at least one "inbox" folder where you'll upload all your scans for sorting and moving to other folders.
I have named my directory `skanningar`, which is Swedish for "scans". To retrieve the ID of the directory, use the Google Drive website and click on the folder.
The folder ID can now be extracted from the URL:
`https://drive.google.com/drive/u/1/folders/<FOLDER ID>`.

## Step 7: Configuration

Create a new file named `config.toml` by copying the file `config.toml.example`.

### Basic configuration

#### For Notion

Simple and required things first. Fill in the Notion auth token under `auth_token` under the `notion` key.
Fill in the database ID where you want pages to appear that you took note of earlier under `upload_database_id`.
Also fill in the name you gave the field for the Google Drive ID under `google_drive_id_field_name`.
Aaandd, fill in the name of the document name/document title field under `document_name_field_name`

#### For Google Drive

Add the upload folder ID that you noted under `upload_folder_id` under `google_drive`.

### Tagging system configuration

#### Tagging system background
> **Note**
> 
> You may notice that some of the tags in the tag system examples have tag shortcuts that do not seem to correspond to the word
> they are for. For example, you might wonder why I shorted "lecture" as "g"? Simple answer: I'm Swedish. Lecture in Swedish (in the context I'm taking notes in)
> can be translated to `Genomgång`. There is the missing letters! I hope this doesn't confuse you...

The tagging system is quite an essential part of the syncing process and it is used for categorizing files. With this system,
I can simply add tags to the beginning of an input file's name:
`[tags here] [file name/title here]`
the program picks up these tags and maps them to an output folder. For example, I have the following mapping:
![A graphic showing my mapping for tag to relevant folder](instruction_screenshots/Tag%20system.png)
I have one tag that is for the subject and then an inner tag to mark the type of note. I then have a folder structure on my Google Drive:
* `/schoolwork`
  * `/math`
    * `/assignments`
    * `/lectures`
  * `/physics`
    * `/assignments`
    * `/lectures`
  ...
This really categorizes the notes in a neat way!

#### Setting up the tagging system

To set up the tagging system, you need to figure out the shortcuts you want for all your tags and what folders you want the tags to correspond to.
You should also create some tags in Notion to take full advantage of the tagging system. I have a multi-select with all of my subjects in. There's where you grabbed the IDs
in the first step!

##### Mapping the tags to Notion correctly

In the example `config.toml`, there are the following lines:
```toml
tag_types.subject.name = "Subject"
tag_types.subject.notion_type = "multi_select"
tag_types.note_type.name="Type"
tag_types.note_type.notion_type = "multi_select"
```
These lines demonstrate how you map a tag to Notion. For each tag, you give it an internal ID to use in the script. In the example above, the two IDs
are `subject` and `note_type`. Each added tag ID then has the following settings:
* `name`: The name of the database field/column in Notion to set to a certain value when this tag is found.
* `notion_type`: The type of the field in Notion. Supported values: `"multi_select"`, `"rich_text"`, `"title"`, however the latter is already set by the code and thus
not really supported.

So, to add a mapping to a new tag, just follow this format:
```toml
tag_types.<new tag ID>.name = "<Notion database column name of field to add tag in>"
tag_types.<new tag ID>.notion_type = "<one of the types above>"
```

##### Configuring tag names, values, and output folders

Now, it's time to do the fun tag mapping! The easiest way to explain stuff here is to use an example too.
The `tags.json5.example` is great to help out with that. Make sure to create a new file or copy the example file to `tags.json5`.

The example file includes examples for the mapping described under *Tagging system background* above.

###### Basics

Let's remember the tag format: `tag.subtag.subsubtag.subsubsubtag etc. etc.`. The JSON follows that structure very much.
Each key is mapped to a tag name and includes either subtags, or if there are no subtags, it includes information of where to move
stuff and how to categorize them. In the example, `"ma"` is a tag with subtags, and `"g"` and `"u"` are tags that don't have any subtags.

###### Tag with subtags format

To add a tag that has subtags, you can follow this format:

```json
{
	"<root tag name>": {
		"<subtag 1>": {
			"notion_tags": [...],
			"folder_id": "..."
		},
		"<subtag 2>": {
			"notion_tags": [...],
			"folder_id": "..."
		},
		"fallback": {
			"notion_tags": [...],
			"folder_id": "..."
		}

	}
}
}
```
The `fallback` key is very important and as you may notice in the example, it is present even in the top-level tag. It allows the script to find a place
for documents where the tags could not be detected, or where the full level of subtag recursion is not reached.

###### Subtag format

A subtag may look like this:

````json
{
	"<subtag 1>": {
		"notion_tags": [{
				"type": "<internal tag 1 ID>",
				"value": "<Value in Notion to set tag to>"
			},
			{
				"type": "<internal tag 2 ID>",
				"value": "<Value in Notion to set tag to>"
			},
		],
		"folder_id": "<Google Drive folder ID to move documents to>"
	}
}
````

The `"notion_tags"` list features a list of fields in Notion to set. Above, you gave each tag an *internal ID* in the configuration and mapped it to a Notion type.
In the `"type"` field, you enter that *internal ID* (for example `subject` or `note_type` if you're referring to the example documentation), and in `value`, you enter a value
for the field to be set to when the tag is detected in a document name. For `multi_select` fields, this would be an ID that you have grabbed from the Notion API above as part of the preparation steps.
For `rich_text` fields, this would be the text that you want to set the field to.

And voilà! That should be it for the configuration of tags!

### Post-sync configuration

I implemented a "post-sync hook" system that runs Python code after all pages have been synced. It should be [quite straightforward](post_sync/README.md) to implement your own post-sync modules.
There is also one module supported, which is called `discord` and it does what you might have guessed: sends messages to a Discord channel to notify when a new document has been uploaded.

#### Basic configuration

Under the `post_sync` configuration option, you can enable or disable the sync by changing the boolean value of `enabled` to either `true` or `false`.
There is also a list of what modules you want to enable, `enabled_modules`, that you have to add the module name to.
Currently supported modules:
* `discord` - Sends information to a Discord channel for each file that has been uploaded.

> **🌟 PR:s welcome**: Feel free to add your own post-sync module via pull request.

#### Module-specific configuration

##### Discord

###### Required configuration

* Set `discord.webhook_url` in the post-sync settings to the webhook URL of the Discord webhook that should be called to send information about files.

###### Optional configuration

> **Note**
> 
> The options below have default settings in case you do not want to customize them.

* Set `discord.embed_title` in the post-sync settings to add a custom title for each message.

* Set `discord.embed_message` in the post-sync settings to have the message follow a custom message format. The format allows for the following parameters to dynamically format
the message:
  * `title`: The name of the file.
  * `drive_id`: The ID of the file in Google Drive.
  * `drive_link`: A link to the file in Google Drive
  * `notion_link`: A link to the file in Notion.

* Set `discord.embed_color` in the post-sync settings to a *decimal format* color to customize the embed color (the bar to the left of it).

## Step 8: Using Linux? Automate the task easily

I have the background check of syncing files run every 15 minutes to check for new files, so I use a tool called `systemd` to keep track of it.


(In the base directory of the code)
* Copy the script for running the task:
`sudo cp systemd/run_notestion_sync.sh /usr/local/bin/run_notestion_sync.sh`
* Edit the file and make sure that the paths to the directory where you have installed NotesTionSync is right:
`sudo nano /usr/local/bin/run_notestion_sync.sh`
* Ensure executable permissions:
`sudo chmod +x /usr/local/bin/run_notestion_sync.sh`
* Copy service files:
`sudo cp systemd/run_notestion_sync.service /etc/systemd/system/run_notestion_sync.service`

* `sudo cp systemd/run_notestion_sync.timer /etc/systemd/system/run_notestion_sync.timer`
Optional step: Edit how often the sync runs (default is once every 15 minutes):
* `sudo nano /etc/systemd/system/run_notestion_sync.timer` and change the `OnCalendar=` entry

Run the timer, which defaults to once every 15 minutes:
* `sudo systemctl start run_notestion_sync.timer`



## Step 9: A note for the first run

The first running will sync all files you have in the configured Google Drive directories with your Notion database. Aka, if you have a lot of files, this initial sync
will take quite some time. Future syncs will be faster!

## Step 10: Complete!

You should now be able to enjoy a perfectly synced Google Drive to Notion with file tags support! If you encounter any problems, feel free to open an [issue](https://github.com/sotpotatis/notestionsync/issues).
If you implemented anything cool for your own workflow, consider creating a [pull request](https://github.com/sotpotatis/notestionsync/pulls).