"""tag_detector.py
For categorizing my scans on the fly, I came up with a tag system.
This tag system is a string at the beginning of the file name with dots in it.
The dots have multiple recursion levels, for example, I could say:
ma. --> okay, it has something to do with maths
    u. --> okay, it is assignment work
    g. --> okay, it is lecture notes
tag_detector creates a detector for this."""
from utilities import get_logger
from typing import Optional, Tuple, List
import os

class TagDetector:
    def __init__(self, tag_mappings:dict):
        """Initializes the tag detector.

        :param tag_mappings: A configuration file which is a dictionary supporting multiple recursion levels."""
        self.tag_mappings = tag_mappings
        self.logger = get_logger(__name__)

    def get_tags(self, string:str, current_recursion_level:Optional[dict]=None)->Optional[dict]:
        """Gets the Google Drive folder for the tag in a string formatted according to the tag format (XX.YY.ZZ).

        :param string: The string to analyze

        :param current_recursion_level: The current dictionary in the tag_mappings that we are at. Leave blank to use the top level.

        :returns The found tag data if tags are found, otherwise returns None."""
        self.logger.debug(f"Getting tags in string {string} with recursion level {current_recursion_level}...")
        # Split string to find more tag levels
        tag_levels = string.split(".")
        self.logger.debug(f"Found tag levels: {tag_levels}")
        # The variable current_recursion_level defines where in the tags we are.
        # If it hasn't been set, we should be at the top level.
        if current_recursion_level is None:
            current_recursion_level = self.tag_mappings
        # If any tags were found
        if len(tag_levels) > 0:
            if tag_levels[0] not in current_recursion_level:
                self.logger.debug(f"Ignoring unparseable tag {tag_levels}. The filename probably does not include any tags.")
                return
            current_recursion_level = current_recursion_level[tag_levels[0]] # Go into the tag mapping
            if len(tag_levels) > 1: # Check if there are more depths of tag level to process
                self.logger.debug("More subtags to process. Handling...")
                return self.get_tags(".".join(tag_levels[1:]), current_recursion_level)
        else:
            self.logger.warning("Found no tag levels! This is probably because the input is missing them.")
            return
        # When we are done processing, there are two options:
        # 1. We have a root tag, but we have multiple subtags. We therefore return the fallback for the root tag
        # 2. We are at the maximum recursion level/maximum depth level in the in configuration dict,
        # and can return the folder ID and tags directly
        self.logger.debug("Done processing tag levels.")
        if "folder_id" not in current_recursion_level: # Detect and handle scenario 1
            return current_recursion_level["fallback"]
        else: # Detect and handle scenario 2
            return current_recursion_level

    def get_drive_folder_from_filename(self, filename:str, apply_tags:Optional[List[dict]]=None)->Tuple[str,List[str],str]:
        """Extracts the drive folder from a specific file name based on its tags.

        :param filename: The name of the uploaded file.

        :param apply_tags: If set, a list of tags to apply to the file regardless.

        :returns A tuple with three entries: the folder to put the file in. Will return the fallback folder if no tags
        were found, any Notion tags to apply, and the filename without tags."""
        # Search for tags in the file. We require at least a space.
        filename_split = os.path.splitext(filename)[0].split(" ")

        fallback = self.tag_mappings["fallback"]
        # Start parsing
        if len(filename_split) < 2:  # No spaces --> No tags --> Use fallback
            self.logger.warning(f"Found no tags in filename: {filename}.")
            found_tag = None
        else:
            tags = filename_split[0]  # Tags should be the first in a file
            # Check the tags
            found_tag = self.get_tags(tags)
        if found_tag is None:
            self.logger.warning("Tags were not found for a file, so its fallback directory will be used.")
            filename_without_tags = filename
            found_tag = fallback
        else:
            # Automatically remove the tags from the filename
            filename_without_tags = " ".join(filename_split[1:])
        # See if any tags are set to always be applied
        if apply_tags is not None:
            found_tag_notion_tags = apply_tags
        else:
            found_tag_notion_tags = []
        found_tag_notion_tags.extend(found_tag["notion_tags"])
        # Remove any duplicates from the list
        new_found_tag_notion_tags = []
        for tag in found_tag_notion_tags:
            if tag not in new_found_tag_notion_tags:
                new_found_tag_notion_tags.append(tag)
        found_tag_notion_tags = new_found_tag_notion_tags
        found_tag_drive_folder = found_tag["folder_id"]
        self.logger.info(f"Found target folder: {found_tag_drive_folder}, Notion tags {found_tag_notion_tags} for filename {filename}.")
        return found_tag_drive_folder, found_tag_notion_tags, filename_without_tags
