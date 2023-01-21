"""page_formatter.py
Since everyone's Notion Database is different, you have to customize and create a page formatter
function that fills out a page with all the details you want.
See the implementation below."""

class PageFormatter:
    def __init__(self):
        pass


    def format_according_to_data(self, document_title):
        return {
            "Namn": {
                "title": document_title
            },
            "Typ": {
                "title": "Anteckning"
            }
        }