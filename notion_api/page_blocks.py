"""page_blocks.py
Contains some definitions for Notion page blocks.
Only includes the ones that I am using."""
from .fields import Field


class NotionPageBlock(Field):
    def __init__(self, field_type: str, main_parameter: str):
        """Defines a page block on Notion.

        :param field_type: The type of the block.

        :param main_parameter: The main text parameter/value in the page block.
        This varies from field to field and is preset to avoid any configuration hassles."""
        self.field_type = field_type
        self.main_parameter = main_parameter
        super().__init__(field_type, main_parameter)

    def __dict__(self) -> dict:
        # Override me!
        return {}


class NotionPageEmbedBlock(NotionPageBlock):
    """Class for a Notion embed block."""

    def __init__(self, main_parameter: str):
        """Initializes a page embed block.

        :param main_parameter: The main text parameter/value in the database field.
        This varies from field to field and is preset to avoid any configuration hassles."""
        super().__init__("embed", main_parameter)

    def __dict__(self) -> dict:
        return {
            "type": "embed",
            "embed": {
                "url": self.main_parameter
            }
        }

class NotionPageQuoteBlock(NotionPageBlock):
    """Class for a Notion quote block."""

    def __init__(self, main_parameter: str):
        """Initializes a page quote block.

        :param main_parameter: The main text parameter/value in the database field.
        This varies from field to field and is preset to avoid any configuration hassles."""
        super().__init__("quote", main_parameter)

    def __dict__(self) -> dict:
        return {
            "type": "quote",
            "quote":
                {"rich_text":
                    [
                        {
                            "type": "text",
                            "text": {
                        "content": self.main_parameter
                    }
                        }]
                }
        }

class NotionPageHeadingBlock(NotionPageBlock):
    """Class for a Notion heading block."""

    def __init__(self, heading_level:int, main_parameter: str):
        """Initializes a page heading block.

        :param heading_level: The heading level of the page.

        :param main_parameter: The main text parameter/value in the database field.
        This varies from field to field and is preset to avoid any configuration hassles."""
        self.heading_level = heading_level
        self.heading_type_name = f"heading_{self.heading_level}"
        super().__init__(self.heading_type_name, main_parameter)

    def __dict__(self) -> dict:
        return {
            "type": self.heading_type_name,
            self.heading_type_name:
                [
                    {
                        "type": "text",
                        "content": self.main_parameter
                    }
                ]
        }

class NotionPageHeading3Block(NotionPageHeadingBlock):
    def __init__(self, *args, **kwargs):
        super().__init__(3, *args, **kwargs)


class NotionPageHeading2Block(NotionPageHeadingBlock):
    def __init__(self, *args, **kwargs):
        super().__init__(2, *args, **kwargs)


class NotionPageHeading1Block(NotionPageHeadingBlock):
    def __init__(self, *args, **kwargs):
        super().__init__(1, *args, **kwargs)

class NotionPageURLBlock(NotionPageBlock):
    """Creates a "URL" block that is not an embed but an in-text link."""
    def __init__(self, main_parameter: str):
        """Initializes a page heading block.


        :param main_parameter: The main text parameter/value in the database field.
        This varies from field to field and is preset to avoid any configuration hassles."""
        super().__init__("url", main_parameter)

    def __dict__(self) -> dict:
        return {
			"type": "paragraph",
			"paragraph": {
				"rich_text": [
					{
					"type": "text",
					"text": {
						"content": self.main_parameter,
						"link": {
							"url": self.main_parameter
						}
					}
				}
				]
			}}

class NotionPageParagraphBlock(NotionPageBlock):
    """Creates a paragraph block. Use the NotionPageURLBlock for embedding URLs."""
    def __init__(self, main_parameter: str):
        """Initializes a page heading block.


        :param main_parameter: The main text parameter/value in the database field.
        This varies from field to field and is preset to avoid any configuration hassles."""
        super().__init__("url", main_parameter)

    def __dict__(self) -> dict:
        return {
			"type": "paragraph",
			"paragraph": {
				"rich_text": [
					{
					"type": "text",
					"text": {
						"content": self.main_parameter
					}
				}
				]
			}}
