"""notion.py
Main Notion API interface."""
from __future__ import annotations

import warnings
from typing import Optional, List, Dict, Union
from .database_fields import NotionDatabaseField
from .fields import Field
from .page_blocks import NotionPageBlock
import requests, time

from utilities import get_logger


class NotionUnexpectedStatusCode(Exception):
    pass

class NotionRequestFailed(Exception):
    pass

class NotionAPIClient:
    def __init__(self, token, notion_api_version="2022-06-28"):
        """Initializes a Notion API client."""
        self.token = token
        self.notion_api_version = notion_api_version
        if self.notion_api_version != "2022-06-28":
            warnings.warn("Using incompatible API version (not 2022-06-28). The API client might not work properly.")
        self.logger = get_logger(__name__)
        self.default_request_kwargs = { # Authorization kwargs that always are in the request
            "headers": {
                "Authorization": f"Bearer {self.token}",
                "Notion-Version": self.notion_api_version
            }
        }

    def send_request(self, request_method, api_method, request_json=None, expected_status_codes:Optional[List[int]]=None):
        """Sends an authenticated request to Notion and returns the response."""
        if expected_status_codes is None:
            expected_status_codes = [200]
        self.logger.debug("Sending request to Notion...")
        request_kwargs = self.default_request_kwargs
        request_kwargs["method"] = request_method
        request_kwargs["url"] = f"https://api.notion.com/v1{api_method}"
        if request_json is not None:
            request_kwargs["json"] = request_json
        self.logger.debug(f"Sending request to Notion at {request_kwargs['url']} with details {request_kwargs}...")
        # Send request
        try:
            response = requests.request(**request_kwargs)
        except Exception as e:
            error_message = f"Notion request failed with error {e}."
            self.logger.critical(error_message)
            raise NotionRequestFailed(error_message)
        if response.status_code not in expected_status_codes:
            if response.status_code == 429: # Detect rate limits
                # According to the documentation, rate limits have a Retry-After header
                # which gives the number of seconds to wait before retrying the request.
                self.logger.debug("Detected rate-limit. Getting wait time...")
                retry_after = float(response.headers["Retry-After"])
                self.logger.warning(f"Rate-limited by Notion. Waiting and retrying request in {retry_after} seconds...")
                time.sleep(retry_after)
                # Retry request after rate limit is finished
                self.logger.info("Retrying request...")
                # Call the function with the original arguments
                self.send_request(request_method, api_method, request_json, expected_status_codes)
            else:
                error_message = f"Unexpected status code received from Notion: {response.status_code}. Content: {response.content}"
                raise Exception(error_message)
        self.logger.info("Data successfully retrieved from Notion.")
        return response

    def get_database(self, database_id:str):
        """Gets a database by its ID."""
        self.logger.info(f"Getting database {database_id} from Notion...")
        response = self.send_request("POST", f"/databases/{database_id}/query")
        self.logger.info("Database data successfully retrieved.")
        return response.json()

    def combine_fields(self, types:dict|list, fields:Dict[str,Field], initial_data:Optional[dict]=None)->dict|list:
        """A utility to add a render of fields (see the Field class that multiple properties (e.g. NotionDatabaseField) derives from) to a dictionary.

        :param types: dict to input and output a dict, list to input and output a dict.

        :param field_list: A dictionary of keys and values, but with fields as the values.

        :param initial_data: If filled out, add some data to the dict by default."""
        if initial_data is None:
            output = {} if types == dict else []
        else:
            output = initial_data
        if types == dict:
            for field_key, field_value in fields.items():
                output[field_key] = field_value.__dict__()
        elif types == list:
            for field in fields:
                output.append(field.__dict__())
        else:
            raise ValueError(f"Unsupported type for field combination ({type(types)} is not dict or list)")
        return output

    def create_page(self, parent:dict, page_properties:Dict[str, NotionDatabaseField], page_children:Optional[List[NotionPageBlock]]=None, icon:Optional[dict]=None, cover:Optional[dict]=None):
        """Function for creating a new page.

        :param parent: The parent of the page. See Notions documentation for more details. The parent might be a page or
        a database.

        :param page_properties: Properties for the new page."""
        self.logger.info(f"Creating a new page with details {page_properties}...")
        # Generate NotionDatabaseField JSON by combining arguments.
        # Add all properties by converting them to dict
        properties = self.combine_fields(dict, page_properties)
        request_json = {
            "parent": parent,
            "properties": properties
        }
        # Add additional parameters if set
        if page_children is not None:
            # Add all NotionPageBlock properties by converting them to dict
            page_children_data = self.combine_fields(list, page_children)
            request_json["children"] = page_children_data
        if icon is not None:
            request_json["icon"] = icon
        if cover is not None:
            request_json["cover"] = cover
        response = self.send_request("POST", "/pages", request_json)
        self.logger.info("Page successfully created.")
        return response.json()

    def update_page(self, page_id:str, new_properties:Optional[List[NotionPageBlock]]=None,
                    archived:Optional[bool]=None, icon:Optional[dict]=None, cover:Optional[dict]=None):
        """Updates a notion page.

        :param page_id: The ID of the page.

        :param things_to_update: The things to update in the page. Note that this is in dict format."""
        self.logger.info(f"Updating Notion page: {page_id}...")
        request_json = {}
        if new_properties is not None:
            #  Combine properties into dict and add them to the request
            request_json["properties"] = self.combine_fields(list, new_properties)
        # Add additional things
        if archived is not None:
            request_json["archived"] = archived
        if icon is not None:
            request_json["icon"] = icon
        if cover is not None:
            request_json["cover"] = cover
        response = self.send_request("PATCH", f"/pages/{page_id}", request_json)
        self.logger.info("Notion page was updated.")