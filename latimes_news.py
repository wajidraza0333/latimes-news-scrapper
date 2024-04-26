"""A module to interact with the LA Times website."""
import re
import time
from dataclasses import astuple, dataclass
from typing import List

from openpyxl import Workbook

from RPA.Browser.Selenium import Selenium
from RPA.HTTP import HTTP

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebElement

from constants import *
from exceptions import NoResultsException


@dataclass
class Article:
    """
    Represents a news article.

    Attributes:
        title (str): The title of the news article.
        date (str): The date when the news article was published.
        description (str): The description or summary of the news article.
        profile_picture (str): The URL or path to the profile picture associated with the news article.
        search_phrase_count (int): The count of occurrences of the search phrase in the news article.
        contains_money (bool): Indicates whether the news article contains mentions of money.
    """
    title: str
    date: str
    description: str
    profile_picture: str
    search_phrase_count: int
    contains_money: bool


class LATimes:
    """A class to interact with the LA Times website."""

    def __init__(self):
        """Initialize LATimes instance."""
        self.browser = Selenium()
        self.http = HTTP()

    def open_browser_and_navigate(self, url: str, headless: bool = False, maximized: bool = True) -> None:
        """
        Open a browser window and navigate to the given URL.

        Args:
            url (str): The URL to navigate to.
            headless (bool, optional): Whether to run the browser in headless mode. Defaults to False.
            maximized (bool, optional): Whether to maximize the browser window. Defaults to True.
        """
        self.browser.open_available_browser(url, headless=headless, maximized=maximized)
        self.browser.wait_until_page_contains_element(Locators.BUTTON)

    def search_for_phrase(self, phrase: str) -> None:
        """
        Search for a given phrase on the LA Times website.

        Args:
            phrase (str): The phrase to search for.

        Raises:
            NoResultsException: If no results are found for the given phrase.
        """
        self.browser.click_button(Locators.BUTTON)
        self.browser.input_text_when_element_is_visible(Locators.INPUT, phrase)
        self.browser.click_button(Locators.SUBMIT)
        self.browser.wait_until_page_contains_element(Locators.RESULTS_FOR_TEXT)

        if self.browser.does_page_contain_element(Locators.NO_RESULTS.format(phrase=phrase)):
            raise NoResultsException

        self.__phrase = phrase

    def select_category_and_wait_for_results(self, category: str) -> None:
        """
        Select a category from the LA Times website.

        Args:
            category (str): The category to select.
        """
        topics_section = self.browser.find_element(Locators.TOPICS_SECTION)
        topics_section.find_element(By.XPATH, value=Locators.SEE_ALL_TOPICS).click()
        topics_section.find_element(By.XPATH, value=Locators.TOPIC.format(name=category)).click()
        self.browser.wait_until_page_contains_element(Locators.RESULTS)

    def sort_by_latest(self) -> None:
        """Sort search results by latest."""
        self.browser.select_from_list_by_value(Locators.SELECT_INPUT, '1')
        self.browser.wait_until_page_contains_element(Locators.RESULTS)

    @staticmethod
    def get_field_data(element: WebElement, locator) -> str:
        """
        Get text data from a WebElement based on a locator.

        Args:
            element (WebElement): The WebElement to extract data from.
            locator: Locator to find the desired element.

        Returns:
            str: The text data found.
        """
        try:
            return element.find_element(by=By.XPATH, value=locator).text
        except NoSuchElementException:
            return ''

    def download_profile_picture(self, element: WebElement, file_path) -> str:
        """
        Download the profile picture associated with a news article.

        Args:
            element (WebElement): The WebElement representing the news article.
            file_path (str): The path to save the downloaded profile picture.

        Returns:
            str: The file path where the profile picture is saved.
        """
        try:
            img = element.find_element(by=By.XPATH, value=Locators.PROF_PIC)
            self.http.download(img.get_attribute('src'), file_path)
            return file_path
        except NoSuchElementException:
            return EMPTY_PROFILE_PIC

    def set_phrase_count_and_money_check(self, item: dict) -> None:
        """
        Set the search phrase count and check if the article contains mentions of money.

        Args:
            item (dict): Dictionary containing news article data.
        """
        title_description = f'{item["title"]} {item["description"]}' if item["description"] else item['title']
        item["search_phrase_count"] = re.findall(self.__phrase, title_description, flags=re.IGNORECASE).__len__()

        amount_pattern = r'\$[0-9,]+(\.[0-9]+)?|\b[0-9]+ dollars\b|\b[0-9]+ USD\b'
        item["contains_money"] = MONEY_PRESENT if re.search(amount_pattern, title_description) else MONEY_ABSENT

    def get_news_data(self) -> List[Article]:
        """
        Get news article data from the search results.

        Returns:
            List[Article]: A list of NewsArticle objects representing the search results.
        """
        time.sleep(5)
        article_elements = self.browser.find_elements(Locators.RESULTS)

        articles: List[Article] = []
        idx = 1
        for element in article_elements:
            img_name = PROFILE_PIC_NAME.format(name=f'article_{idx}')
            article_data_map = {
                "title": self.get_field_data(element, Locators.TITLE),
                "date": self.get_field_data(element, Locators.DATE),
                "description": self.get_field_data(element, Locators.DESCRIPTION),
                "profile_picture": self.download_profile_picture(element, img_name)
            }
            self.set_phrase_count_and_money_check(article_data_map)
            articles.append(Article(**article_data_map))
            idx += 1
        return articles

    def create_excel_from_news_data(self) -> None:
        """Download news article data into an Excel file."""
        workbook = Workbook()
        exception_sheet = workbook.active

        exception_sheet.title = "Articles"
        exception_sheet.append(ARTICLE_HEADERS)
        for item in self.get_news_data():
            exception_sheet.append(astuple(item))

        workbook.save(NEWS_DATA)


class Locators:
    """
    Defines XPaths used for interacting with the LA Times website.
    """
    BUTTON = "//button[@data-element='search-button']"
    INPUT = "//input[@data-element='search-form-input']"
    SUBMIT = "//button[@data-element='search-submit-button']"
    NO_RESULTS = """//div[contains(text(),'There are not any results that match "{phrase}".')]"""
    RESULTS_FOR_TEXT = "//h1[text()='Search results for']"
    RESULTS = '//ul[@class="search-results-module-results-menu"]//li'
    TOPICS_SECTION = "//div[@class='search-filter']//p[contains(text(), 'Topics')]/parent::*"
    SEE_ALL_TOPICS = "//span[@class='see-all-text']"
    TOPIC = "//span[text()='{name}']"
    SELECT_INPUT = "//select[@class='select-input']"
    TITLE = ".//h3//a[@class='link']"
    DATE = ".//p[@class='promo-timestamp']"
    DESCRIPTION = ".//p[@class='promo-description']"
    PROF_PIC = ".//img"
