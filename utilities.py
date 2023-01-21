"""utilities.py
Some utility functions and classes."""
import os, toml, logging, json5
from logging import Formatter, LogRecord, DEBUG, INFO, WARNING, ERROR, CRITICAL, getLogger, StreamHandler, basicConfig
from typing import List

from colorama import Fore, Style

# paths
WORKING_DIR = os.getcwd()
CONFIGURATION_FILEPATH = os.path.join(WORKING_DIR, "config.toml")
TAGS_FILEPATH = os.path.join(WORKING_DIR, "tags.json5")
SEEN_FILES_FILEPATH = os.path.join(WORKING_DIR, ".notion_drive_sync_seen")
TEMPORARY_FILES_DIR = os.path.join(WORKING_DIR, "temporary_files")
def get_config()->dict:
    """Gets the configuration and returns it."""
    return toml.loads(open(CONFIGURATION_FILEPATH, encoding="UTF-8").read())

def get_tags()->dict:
    """Gets the content of the tag file.

    :returns Content of the tag configuration file loadedas a dictionary."""
    return json5.loads(open(TAGS_FILEPATH, encoding="UTF-8").read())

def get_seen_files()->List[str]:
    """Gets the content of the seen files filepath."""
    return open(SEEN_FILES_FILEPATH, encoding="UTF-8").read().splitlines()

def update_seen_files(file_paths_to_add:List[str])->None:
    """Updates which files that have been seen."""
    # Add the lines to the file.
    with open(SEEN_FILES_FILEPATH, "w", encoding="UTF-8") as seen_files_file:
        seen_files_file.write("\n".join(file_paths_to_add))


#  A logger with color output
class ColorFormatter(Formatter):
    """A formatter for logging files that prints out different colors
    and nerdfont-compatible text depending on the status."""
    COLORS = {
        DEBUG: Fore.LIGHTBLACK_EX,
        INFO: Fore.BLUE,
        WARNING: Fore.YELLOW,
        ERROR: Fore.LIGHTRED_EX,
        CRITICAL: Fore.RED
    }
    ICONS = {
        DEBUG: "",
        INFO: "",
        WARNING: "",
        ERROR: "",
        CRITICAL: ""
    }
    LOG_FORMAT = f"{Fore.BLACK}%(asctime)s{Style.RESET_ALL}$COLOR[$ICON%(levelname)s]{Style.RESET_ALL} {Fore.BLACK}%(message)s{Style.RESET_ALL}"

    def __init__(self):
        super().__init__()

    def format(self, record: LogRecord) -> str:
        # Get which color to use
        color_to_use = ColorFormatter.COLORS[record.levelno]
        icon_to_use = ColorFormatter.ICONS[record.levelno]
        # Create the formatter
        format = ColorFormatter.LOG_FORMAT.replace("$COLOR", color_to_use).replace("$ICON", icon_to_use)
        formatter = Formatter(format)
        return formatter.format(record)

def get_logger(name:str)->logging.Logger:
    """Gets and returns a logger for the current file.
    Includes adding the color formatted logging handler."""
    logger = getLogger(name)
    stream_handler = StreamHandler()
    # Set log level
    logger.setLevel(DEBUG)
    stream_handler.setLevel(DEBUG)
    stream_handler.setFormatter(ColorFormatter()) # Create formatter
    logger.addHandler(stream_handler) # Add handler for color
    return logger


logger = get_logger(__name__)

if not os.path.exists(TEMPORARY_FILES_DIR):
    logger.info("Creating directory for temporary files...")
    os.mkdir(TEMPORARY_FILES_DIR)
    logger.info("Directory for temporary files created.")

if not os.path.exists(SEEN_FILES_FILEPATH):
    logger.info("Creating file for tracking seen files...")
    update_seen_files([])
    logger.info("File for seen files created.")