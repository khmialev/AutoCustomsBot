import asyncio

from telegram_bot.car_bot import CarBot


async def main():
    tg_bot = CarBot()
    await tg_bot.main()


if __name__ == "__main__":
    asyncio.run(main())
