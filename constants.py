"""Defines constants used in the LA Times automation."""
# Define a constant for the output directory
OUTPUT_DIR = "output"

# Use the OUTPUT_DIR constant to define the paths
NEWS_DATA = f"{OUTPUT_DIR}/news_data.xlsx"
PROFILE_PIC_NAME = f"{OUTPUT_DIR}/{{name}}.jpeg"

EMPTY_PROFILE_PIC = ''
MONEY_PRESENT = 'Yes'
MONEY_ABSENT = 'No'

HEADER_TITLE = "Title"
HEADER_DATE = "Date"
HEADER_DESCRIPTION = "Description"
HEADER_PROFILE_PICTURE = "ProfilePicture"
HEADER_SEARCH_PHRASE_COUNT = "Search Phrase Count"
HEADER_CONTAINS_MONEY = "Contains Money"

ARTICLE_HEADERS = [
    HEADER_TITLE,
    HEADER_DATE,
    HEADER_DESCRIPTION,
    HEADER_PROFILE_PICTURE,
    HEADER_SEARCH_PHRASE_COUNT,
    HEADER_CONTAINS_MONEY
]