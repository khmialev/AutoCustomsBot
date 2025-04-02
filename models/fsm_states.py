from aiogram.fsm.state import StatesGroup, State


class BidCarsCalcStates(StatesGroup):
    waiting_for_url = State()
    waiting_for_price_under_3_years = State()


class CopartCalcStates(StatesGroup):
    waiting_for_url = State()
    waiting_for_price_under_3_years = State()


class IaaiCalcStates(StatesGroup):
    waiting_for_url = State()
    waiting_for_price_under_3_years = State()


class ManualBasicCalcStates(StatesGroup):
    waiting_for_url = State()
    waiting_for_brand = State()
    waiting_for_engine = State()
    waiting_for_year = State()


class ManualSpecCalcStates(StatesGroup):
    waiting_for_model = State()
    waiting_for_engine = State()
    waiting_for_year = State()
