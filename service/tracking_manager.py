import asyncio

from parsers.tracking_bid_cars_parser import TrackingBidCarsParser


class TrackingManager:
    def __init__(self):
        self._tasks: dict[int, asyncio.Task] = {}

    def _is_tracking(self, user_id: int) -> bool:
        return user_id in self._tasks and not self._tasks[user_id].done()

    async def start_tracking(
        self, bot, user_id, chat_id, brand, model, year_from, year_to
    ):
        if self._is_tracking(user_id):
            self._tasks[user_id].cancel()

        parser = TrackingBidCarsParser()
        task = asyncio.create_task(
            parser.track_cars_for_user(
                bot=bot,
                user_id=user_id,
                chat_id=chat_id,
                brand=brand,
                model=model,
                year_from=year_from,
                year_to=year_to,
                on_stop=self.stop_tracking,
            )
        )
        self._tasks[user_id] = task

    async def stop_tracking(self, user_id: int):
        if self._is_tracking(user_id):
            self._tasks[user_id].cancel()
            del self._tasks[user_id]
