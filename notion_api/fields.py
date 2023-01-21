"""fields.py
Defines a reusable Field class.
The API supports basic and easy setting of one-key, one-value items in Notion.
For example, the database_fields.py implements classes for database fields that are flexible:
each field has a value which automatically will be formatted and filled out when calling __dict__() on the field.
This approach is used on the page_blocks.py file too, so we define the approach here. 
"""


class Field:
    def __init__(self, field_type: str, main_parameter: str):
        """Defines a some kind of field on Notion.

        :param field_type: The field type.

        :param main_parameter: The main text parameter/value in the field.
        This varies from field to field and is one argument to avoid any configuration hassles.
        This is the main convenience and reason for implementing this class."""
        self.field_type = field_type
        self.main_parameter = main_parameter

    def __dict__(self) -> dict:
        # Override me!
        return {}
