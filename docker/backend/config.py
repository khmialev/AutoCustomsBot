import os

from dotenv import load_dotenv

load_dotenv()


PROXY_HOST = os.getenv("PROXY_HOST")
PROXY_PORT = os.getenv("PROXY_PORT")
PROXY_USER = os.getenv("PROXY_USER")
PROXY_PASS = os.getenv("PROXY_PASS")
PROXY_URL = f"https://{PROXY_USER}:{PROXY_PASS}@{PROXY_HOST}:{PROXY_PORT}"
PROXY_CONFIG = {
    "server": f"http://{PROXY_HOST}:{PROXY_PORT}",
    "username": PROXY_USER,
    "password": PROXY_PASS,
}

AUCTION_BUTTON = os.getenv("AUCTION_BUTTON")
AUCTION_TAX = os.getenv("AUCTION_TAX")
DELIVERY = os.getenv("DELIVERY")
DECLARANTS = os.getenv("DECLARANTS")
DISABLED_PERSON = os.getenv("DISABLED_PERSON")


EURO_USD = os.getenv("EURO_USD")


BASE_URL = os.getenv("BASE_URL")
NOT_GENERATION_URL = os.getenv("NOT_GENERATION_URL")
USD_URL = os.getenv("USD_URL")
AV_PAGE_URL = os.getenv("AV_PAGE_URL")


IAAI_URL = os.getenv("IAAI_URL")
IMAGE_URL = os.getenv("IMAGE_URL")
