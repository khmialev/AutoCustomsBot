import os

from dotenv import load_dotenv

load_dotenv()
DB_USERNAME = os.getenv("DB_USERNAME")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

ASYNC_DATABASE_URL = (
    f"postgresql+asyncpg://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)


AUCTION_BUTTON = os.getenv("AUCTION_BUTTON")
AUCTION_TAX = os.getenv("AUCTION_TAX")
DELIVERY = os.getenv("DELIVERY")
DECLARANTS = os.getenv("DECLARANTS")
DISABLED_PERSON = os.getenv("DISABLED_PERSON")

BASE_URL = os.getenv("BASE_URL")
NOT_GENERATION_URL = os.getenv("NOT_GENERATION_URL")
USD_URL = os.getenv("USD_URL")
COPART_URL = os.getenv("COPART_URL")
COPART_MAIN_URL = os.getenv("COPART_MAIN_URL")

IAAI_URL = os.getenv("IAAI_URL")

EURO_USD = os.getenv("EURO_USD")
TOKEN = os.getenv("TOKEN")

PROXY_HOST = os.getenv("PROXY_HOST")
PROXY_PORT = os.getenv("PROXY_PORT")
PROXY_USER = os.getenv("PROXY_USER")
PROXY_PASS = os.getenv("PROXY_PASS")

PROXY_URL = f"https://{PROXY_USER}:{PROXY_PASS}@{PROXY_HOST}:{PROXY_PORT}"

brands = [
    "Acura",
    "Alfa-Romeo",
    "Aston-Martin",
    "Audi",
    "Bentley",
    "BMW",
    "Bugatti",
    "Buick",
    "Cadillac",
    "Chevrolet",
    "Chrysler",
    "Citroën",
    "Dacia",
    "Daewoo",
    "Dodge",
    "Ferrari",
    "Fiat",
    "Ford",
    "Genesis",
    "Geely",
    "GMC",
    "Great-Wall",
    "Honda",
    "Hummer",
    "Hyundai",
    "Infiniti",
    "Jaguar",
    "Jeep",
    "Kia",
    "Lamborghini",
    "Lancia",
    "Land-Rover",
    "Lexus",
    "Lincoln",
    "Lotus",
    "Maserati",
    "Maybach",
    "Mazda",
    "McLaren",
    "Mercedes-Benz",
    "Mini",
    "Mitsubishi",
    "Nissan",
    "Opel",
    "Peugeot",
    "Porsche",
    "Renault",
    "Rolls-Royce",
    "Saab",
    "Seat",
    "Skoda",
    "Smart",
    "SsangYong",
    "Subaru",
    "Suzuki",
    "Tesla",
    "Toyota",
    "Volkswagen",
    "Volvo",
]
