import logging
from logging import Logger
import colorlog


class MyLoggerAdapter(logging.LoggerAdapter):
    """
    Адаптер, который автоматически добавляет префикс (prefix) в начало каждого сообщения.
    """

    def process(self, msg, kwargs):
        prefix = self.extra.get("prefix", "???")
        return f"[{prefix}] {msg}", kwargs


class MyLogger(Logger):
    """
    Класс для настройки и использования логгера с поддержкой цветного вывода в консоль.
    Имеет метод get_adapter(...) для получения LoggerAdapter с нужным префиксом.
    """

    def __init__(
        self, name: str = None, log_file: str = None, file_level: int = logging.WARNING
    ):
        super().__init__(name)

        # 1. Логгер вашего приложения
        self.logger = logging.getLogger(name or "Car Bot")
        self.logger.setLevel(logging.INFO)

        if not self.logger.hasHandlers():
            # 2. Настраиваем цветной форматер (colorlog)
            console_formatter = colorlog.ColoredFormatter(
                "%(log_color)s%(asctime)s - %(levelname)s - %(name)s - %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
                log_colors={
                    "DEBUG": "cyan",
                    "INFO": "green",
                    "WARNING": "yellow",
                    "ERROR": "red",
                    "CRITICAL": "bold_red",
                },
            )

            # 3. Хендлер для вашего логгера (console)
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(console_formatter)
            self.logger.addHandler(console_handler)

        aiogram_logger = logging.getLogger("aiogram")
        aiogram_logger.setLevel(logging.INFO)
        if (
            not aiogram_logger.hasHandlers()
        ):  # <-- Добавляем обработчик только если его нет
            aiogram_logger.addHandler(console_handler)

    def get_logger(self) -> logging.Logger:
        """
        Возвращает базовый логгер (без префикса).
        """
        return self.logger

    def get_adapter(self, prefix: str) -> logging.LoggerAdapter:
        """
        Возвращает адаптер логгера, который будет автоматически
        добавлять [prefix] к каждому сообщению.
        """
        return MyLoggerAdapter(self.logger, {"prefix": prefix})
