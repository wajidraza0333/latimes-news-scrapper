import os
import logging

from RPA.Robocorp.WorkItems import WorkItems

from latimes_news import LATimes

OUTPUT_DIR = os.path.join(os.getcwd(), f"output/")
try:
    os.mkdir(OUTPUT_DIR)
except FileExistsError:
    pass

log_file = os.path.join(OUTPUT_DIR, 'la_times.log')
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[
                        logging.FileHandler(log_file),
                        logging.StreamHandler()
                    ])

if not logging.getLogger().handlers:
    raise RuntimeError("Logging configuration failed. No handlers found.")


if os.getenv("ROBOCORP"):
    work_items = WorkItems()
    work_items.get_input_work_item()
    variables = work_items.get_work_item_payload()
    phrase = variables.get("PHRASE")
    topic = variables.get("TOPIC")
else:
    phrase = "IPL"
    topic = "Sports"


def task():
    try:
        logging.info("Initializing LA Times automation task.")
        la_times = LATimes()
        la_times.open_browser_and_navigate('https://www.latimes.com/')
        logging.info("Opened browser successfully.")
        la_times.search_for_phrase(phrase)
        logging.info("Search phrase entered successfully.")
        la_times.sort_by_latest()
        logging.info("Results sorted by latest.")
        la_times.select_category_and_wait_for_results(topic)
        logging.info("Category 'World & Nation' selected.")
        la_times.create_excel_from_news_data()
        logging.info("News data downloaded and saved to Excel.")
        la_times.browser.close_all_browsers()
        logging.info("Closed all browser windows.")
        logging.info("LA Times automation task completed successfully.")
    except Exception as e:
        logging.error(f"An error occurred during LA Times automation task: {e}", exc_info=True)


if __name__ == "__main__":
    task()
