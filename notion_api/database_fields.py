"""database_fields.py
Defines some Notion database fields."""
from .fields import Field


class NotionDatabaseField(Field):
    def __init__(self, field_type:str, main_parameter:str):
        """Defines a database field on Notion.
        
        :param field_type: The type of the block.
        
        :param main_parameter: The main text parameter/value in the database field.
        This varies from field to field and is preset to avoid any configuration hassles."""
        self.field_type = field_type
        self.main_parameter = main_parameter
        super().__init__(field_type, main_parameter)
    
    def __dict__(self)->dict:
        # Override me!
        return {}

class NotionMultiSelectDatabaseField(NotionDatabaseField):
    """Class for a Notion multi-select database field."""
    def __init__(self, main_parameter:str):
        """Initializes a multi-select database field.

        :param main_parameter: The main text parameter/value in the database field.
        This varies from field to field and is preset to avoid any configuration hassles."""
        super().__init__("database", main_parameter)

    def __dict__(self) ->dict:
        return {
            "multi_select": [
                {
                    "id": self.main_parameter
                }
            ]
        }

class NotionRichTextDatabaseField(NotionDatabaseField):
    """Class for a Notion rich text database field."""
    def __init__(self, main_parameter:str):
        """Initializes a rich text database field.

        :param main_parameter: The main text parameter/value in the database field.
        This varies from field to field and is preset to avoid any configuration hassles."""
        super().__init__("rich_text", main_parameter)

    def __dict__(self) ->dict:
        return {
			"rich_text": [
				{
					"type": "text",
					"text":  {
						"content": self.main_parameter
					}
				}
				]
		}

class NotionTitleDatabaseField(NotionDatabaseField):
    """Class for a Notion title database field."""
    def __init__(self, main_parameter:str):
        """Initializes a title database field.

        :param main_parameter: The main text parameter/value in the database field.
        This varies from field to field and is preset to avoid any configuration hassles."""
        super().__init__("title", main_parameter)

    def __dict__(self) ->dict:
        return {
			"title": [
				{
					"text":  {
						"content": self.main_parameter
					}
				}
				]
		}

# Mapping of database field ID to field class
DATABASE_FIELDS = {
    "title": NotionTitleDatabaseField,
    "rich_text": NotionRichTextDatabaseField,
    "multi_select": NotionMultiSelectDatabaseField
}