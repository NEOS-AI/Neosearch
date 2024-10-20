from aws_lambda_powertools import Logger
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By

# custom modules
from .base import BaseAbstractCrawler
from ray_crawler.mongo_db.documents import ArticleDocument


logger = Logger(service="decodingml/crawler")


class MediumCrawler(BaseAbstractCrawler):
    model = ArticleDocument

    def set_extra_driver_options(self, options) -> None:
        options.add_argument(r"--profile-directory=Profile 2")

    def extract(self, link: str, **kwargs) -> None:
        logger.info(f"Starting scrapping Medium article: {link}")

        self.driver.get(link)
        self.scroll_page()

        soup = BeautifulSoup(self.driver.page_source, "html.parser")
        title = soup.find_all("h1", class_="pw-post-title")
        subtitle = soup.find_all("h2", class_="pw-subtitle-paragraph")

        data = {
            "Title": title[0].string if title else None,
            "Subtitle": subtitle[0].string if subtitle else None,
            "Content": soup.get_text(),
        }

        logger.info(f"Successfully scraped and saved article: {link}")
        self.driver.close()
        instance = self.model(
            platform="medium", content=data, link=link, author_id=kwargs.get("user")
        )
        instance.save()

    def login(self):
        """Log in to Medium with Google"""
        self.driver.get("https://medium.com/m/signin")
        self.driver.find_element(By.TAG_NAME, "a").click()
