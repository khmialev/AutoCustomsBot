from aiogram.fsm.state import StatesGroup, State


class CopartCalcStates(StatesGroup):
    waiting_for_url = State()
    waiting_for_brand = State()
    waiting_for_engine = State()
    waiting_for_year = State()


class IaaiCalcStates(StatesGroup):
    waiting_for_url = State()
    waiting_for_brand = State()
    waiting_for_engine = State()
    waiting_for_year = State()


class ManualBasicCalcStates(StatesGroup):
    waiting_for_url = State()
    waiting_for_brand = State()
    waiting_for_engine = State()
    waiting_for_year = State()


class ManualSpecCalcStates(StatesGroup):
    waiting_for_model = State()
    waiting_for_engine = State()
    waiting_for_year = State()
