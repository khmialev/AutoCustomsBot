from aiogram.fsm.state import StatesGroup, State


class CustomFeesStates(StatesGroup):
    waiting_for_delivery_through_georgia = State()
    waiting_for_delivery_through_lithuania = State()
    waiting_for_auction_fee = State()
    waiting_for_declarant_fee = State()
    waiting_for_beneficiary_fee = State()
    waiting_for_customs_duty = State()
    waiting_for_recycling_fee = State()
    waiting_for_auction_play_fee = State()


class CalculateBidCarsStates(StatesGroup):
    waiting_for_url = State()
    waiting_for_price_under_3_years = State()
