import asyncio

from fake_useragent import UserAgent

from selenium.webdriver.ie.webdriver import WebDriver

from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

from parsers.webdriver_manager import DriverManager


class BrandsParser:
    def __init__(self):
        self.ua = UserAgent()
        self.driver_manager: DriverManager = DriverManager(ua=self.ua)
        self.driver: WebDriver = None

    async def get_driver(self):
        """Асинхронная инициализация"""
        self.driver = await self.driver_manager.get_driver()

    def wait_for_element(self, xpath, timeout=10, by_id=False):
        """Получаем один элемент"""
        return WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located((By.XPATH if not by_id else By.ID, xpath))
        )

    def wait_for_click(self, element, timeout=10):
        link = WebDriverWait(element, timeout).until(
            EC.element_to_be_clickable((By.TAG_NAME, "a"))
        )
        link.click()

    async def start_pars(self):
        await self.get_driver()
        button = self.driver.find_element(By.CLASS_NAME, "button__text")
        button.click()


a = BrandsParser()
asyncio.run(a.start_pars())
