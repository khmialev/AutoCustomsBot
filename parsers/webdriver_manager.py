from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.chrome.options import Options
from selenium import webdriver


class DriverManager:
    def __init__(self, ua):
        self.driver = None  # Инициализируем как None
        self.ua = ua.random

    async def setup_driver(self):
        """Настройки драйвера"""
        o = Options()
        # service=ChromeService(ChromeDriverManager().install()) # когда были траблы с драйвером помогло
        o.add_experimental_option("detach", True)
        o.add_argument(f"user-agent={self.ua}")

        o.add_argument("--no-sandbox")
        o.add_argument("--disable-dev-shm-usage")
        # o.add_argument("--headless")  # Запуск в headless режиме
        o.add_argument(
            "--disable-blink-features=AutomationControlled"
        )  # Скрывает, что это автоматизация
        o.add_experimental_option("excludeSwitches", ["enable-automation"])
        o.add_experimental_option("useAutomationExtension", False)
        o.add_argument(
            "--disable-gpu"
        )  # Отключение использования GPU (рекомендуется для headless режима)
        # o.add_argument(
        #     "--window-size=1920,1080"
        # )  # Задаем размер окна (рекомендуется для headless режима)
        driver = webdriver.Chrome(options=o)
        # driver.maximize_window()
        return driver

    async def initialize_driver(self):
        """Запускает драйвер"""
        if self.driver is None:
            self.driver = await self.setup_driver()

    async def get_driver(self) -> WebDriver:
        """Получает драйвер и выполняет авторизацию"""
        if self.driver is None:
            await self.initialize_driver()

        self.driver.get("https://av.by/")

        return self.driver

    async def close_driver(self):
        """Закрывает драйвер"""
        if self.driver:
            self.driver.quit()
            self.driver = None  # Освобождаем ресурс

    async def restart_driver(self):
        if self.driver:
            self.driver.quit()
            self.driver = None
        return await self.get_driver()
