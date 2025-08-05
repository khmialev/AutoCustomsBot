HANDLE_START_COMMAND = "Главное меню\nВыберите действие:"
SHOW_TRACKING_MENU = "Меню отслеживания авто:"
SHOW_CALCULATE_MENU = "Меню расчета авто:"


START_SET_CUSTOM_FEES = "<b>Информация:</b>\nЕсли вы введёте <b>0</b> на любом шаге,бот использует <i>значения по умолчанию</i>.\n\n"
DELIVERY_VIA_GEORGIA = "Введите стоимость доставки через Грузию ($):"
DELIVERY_VIA_LITHUANIA = "Введите стоимость доставки через Грузию ($):"
AUCTION_FEE = "Введите комиссию аукциона ($):"
DECLARANTS_FEE = "Введите услуги декларанта ($):"
BENEFICIARY_FEE = "Введите услуги льготника ($):"
CUSTOMS_DUTY = "Введите таможенный сбор ($):"
RECYCLING_FEE = "Введите утилизационный сбор ($):"
AUCTION_PLAY_FEE = "Введите услуги игры на аукционе ($):"

START_CALCULATE = "<b>Вставьте ссылку</b> на автомобиль (например):\n<code>https://bid.cars/ru/lot/0-41546549/2021-BMW-228i-Gran-Coupe-WBA73AK05M7H21100</code>\n\n━━━━━━━━━━━━━━━━━━━━\nЯ буду ждать вашу ссылку!"
INCORRECT_URL = "<b>Некорректный URL.</b> Попробуйте снова.\n(Ссылка должна начинаться с <code>http</code>)"
CORRECT_URL = "<b>Ссылка получена:</b> <code>{url}</code>\nНачинаю обработку..."


INPUT_CAR_PRICE = "<b>Без стоимости авто нельзя рассчитать таможенную пошлину</b>.\nДля машин младше 3 лет пошлина идёт как % от цены.\n\nПожалуйста, введите предполагаемую стоимость авто (в $):"
INPUT_NUMBER = "Пожалуйста, введите число (например, 15000)."
INCORRECT_CAR_DATA = "Данные о машине не найдены, начните заново."


CAR_SOURCE = "<b>Источник:</b> {url}"
CAR_INFO = """<b>Автомобиль</b>
• Бренд: <b>{brand}</b>
• Модель: <b>{model}</b>
• Год: <b>{year}</b>
• Двигатель: <b>{engine}</b> см³"""

CAR_AUCTION_INFO = """<b>Данные по аукциону</b>
{buy_now}{current_bid}{sales_status}"""

BUY_NOW = "• Купить сейчас: <b>{buy_now}</b> $"
CURRENT_BID = "• Текущая ставка ({timestamp}): <b>{current_bid}</b> $"
SALES_STATUS = "• Статус продажи: <b>{sales_status}</b>"

CAR_DAMAGE_MAIN = "• Основное повреждение: <b>{main_damage}</b>"
CAR_DAMAGE_SECONDARY = "• Вторичные повреждение: <b>{secondary_damage}</b>"

EXPENSES_HEADER = "<b>Расходы</b>"
EXPENSES_ITEM = "• {name}: <b>{value} $</b>"
EXPECTED_PRICE = "• <b>Ожидаемая стоимость: {estimated_price} $</b>"

FEES_UP_TO_THREE_YEARS = "<b>Пошлина ДО 3 лет</b>:"
FEES_THREE_TO_FIVE_YEARS = "<b>Пошлина (3–5 лет)</b>:"
FEES_OLDER_FIVE_YEARS = "<b>Пошлина СТАРШЕ 5 лет</b>"

CUSTOMS_TAX_HEADER = "<b>{header}</b>"
CUSTOMS_TAX_ITEM = " {discounted:.2f} $ ({full:.2f} $)"
CUSTOMS_TOTAL = "──────────\nИтог: <b>{discounted_total:.2f} $</b> (без льготы: {total:.2f} $)"

WARNING_MESSAGE = "<b>Возможно, пока автомобиль будет в пути, он попадёт в категорию {years} </b>"
WARNING_3_YEARS = "«3–5 лет»."
WARNING_5_YEARS = "«СТАРШЕ 5 лет»."

NOT_FOUND = (
    "<b>Бренд: {brand}, модель: {model}, год выпуска: {year}.</b> Нет в базе\n"
)
MULTIPLE_FOUND_HEADER = (
    "<b>Найдено несколько вариантов в базе по этим данным:</b>"
)
MULTIPLE_FOUND_ITEM = """• <b>{brand} {model} {generation} {year}</b> 
• Средняя цена: <b>{average_price}$</b>
• Среднее количество дней в продаже: <b>{average_sell_days}</b>"""

NOT_CAR_DATA = "<b>Сервер так и не ответил.</b>\nПопробуйте позже."
