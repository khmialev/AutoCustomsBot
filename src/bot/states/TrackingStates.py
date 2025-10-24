from aiogram.fsm.state import StatesGroup, State


class TrackingBidCars(StatesGroup):
    waiting_for_model = State()
    waiting_for_year = State()
    waiting_for_generation = State()