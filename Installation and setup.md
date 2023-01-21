> **Please note:** This documentation is a work in progress.
> It will be completed within the following days as of this writing.

# Installation and setup

This document will guide you to setting up your own note syncing with Notion. Its goal is being as complete as possible.

## Step 1: Clone the repository & Install the requirements

Clones the repository:
* `git clone https://github.com/sotpotatis/notestionsync`

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

Make sure you understand what this scripts require. It requires a database where the pages will be added.
Whether you want to create a new one or not - that's totally up to you.
The database needs at least the following:
1. A page name field of type `Title`
2. A page Google Docs ID field of type `Rich Text`

If you want to implement the "tagging system", which is quite an essential feature about this project, you should also create some tags.
Here: you have total freedom as long as you use the supported type: `Multi-Select`. As an example, I have tags for the subject of my notes and the type (lecture notes or assignment).

## Step 5: Giving access

For the integration to work, this step is very important! Go to the Notion database you want to use, and make sure to click on "Share"
and share the database view with the application you created in the first step. If not, the integration will not work!

## Step 6: Retrieving details for the configuration file

We need some details. Let's grab them.

### Notion database ID

Go to the database you want to use together with the tool and extract the ID from this part of the URL:

`https://www.notion.so/<Your Workspace Name>/<ID is here>?<Don't worry about anything after the exclamation mark if any>`

### Tags

If you're going to use tags with the project, you need their ID. The easiest way is to add a new temporary page, apply all tags you need IDs for,
open the page by maximizing it, copy its ID by extracting it from the URL: `https://www.notion.so/<Your-Workspace-Name>/<Page-name>-ee18b8779ae54f358b09221d6665ee15`, and then retrieve the page using something like cURL:

```
curl --request GET \
  --url https://api.notion.com/v1/pages/<Page ID>/ \
  --header 'Authorization: Bearer <Your Notion Access Token Here>' \
  --header 'Content-Type: text/plain' \
  --header 'Notion-Version: 2021-08-16' \
```
In the response, you should be able to extract the IDs of all the tags.

## Step 7: Configuration

Create a new file named `config.toml` by copying the file `config.toml.example`.

### Basic configuration

Fill in the Notion auth token under

