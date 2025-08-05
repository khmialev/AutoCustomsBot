from src.bot.settings import get_settings

settings = get_settings()


class BasicCalculate:
    auction_button = settings.AUCTION_BUTTON
    auction_tax = settings.AUCTION_TAX
    delivery = settings.DELIVERY

    async def expenses_to_the_tsw(self):
        """Расходы до свх"""
        return sum((self.auction_tax, self.auction_button, self.delivery))

    async def before_three_years(
        self, engine_volume: float, declared_cost: float
    ) -> float:
        """
        Расчёт таможенного платежа для автомобиля возрастом до 3 лет.

        :param engine_volume: объём двигателя в см³
        :param declared_cost: таможенная стоимость автомобиля в евро
        :return: сумма таможенного платежа в евро
        """
        if declared_cost <= 8500:
            rate_percent = 0.54
            min_rate_per_cc = 2.5
        elif declared_cost <= 16700:
            rate_percent = 0.48
            min_rate_per_cc = 3.5
        elif declared_cost <= 42300:
            rate_percent = 0.48
            min_rate_per_cc = 5.5
        elif declared_cost <= 84500:
            rate_percent = 0.48
            min_rate_per_cc = 7.5
        elif declared_cost <= 169000:
            rate_percent = 0.48
            min_rate_per_cc = 15
        else:
            # Свыше 169.000 евро
            rate_percent = 0.48
            min_rate_per_cc = 20

        # Считаем платеж двумя способами:
        # 1) как процент от заявленной стоимости
        cost_by_percent = declared_cost * rate_percent

        # 2) как фиксированная ставка за 1 см³
        cost_by_volume = engine_volume * min_rate_per_cc

        # Итоговая сумма — максимум из двух вариантов
        total_payment = max(cost_by_percent, cost_by_volume)

        return total_payment

    async def between_three_five_years(self, engine_volume: float) -> float:
        """
        Расчёт ставки таможенного платежа для авто от 3 до 5 лет
        в зависимости от объёма двигателя.
        Возвращает сумму платежа в евро.
        """

        if engine_volume <= 1000:
            return engine_volume * 1.5
        elif engine_volume <= 1500:
            return engine_volume * 1.7
        elif engine_volume <= 1800:
            return engine_volume * 2.5
        elif engine_volume <= 2300:
            return engine_volume * 2.7
        elif engine_volume <= 3000:
            return engine_volume * 3.0
        else:
            # Для объёма свыше 3000 см³
            return engine_volume * 3.6

    async def after_five_years(self, engine_volume: float) -> float:
        """
        Расчёт ставки таможенного платежа для авто старше 5 лет
        в зависимости от объёма двигателя.
        Возвращает сумму платежа в евро.
        """
        if engine_volume <= 1000:
            return engine_volume * 3.0
        elif engine_volume <= 1500:
            return engine_volume * 3.2
        elif engine_volume <= 1800:
            return engine_volume * 3.5
        elif engine_volume <= 2300:
            return engine_volume * 4.6
        elif engine_volume <= 3000:
            return engine_volume * 5
        else:
            # Для объёма свыше 3000 см³
            return engine_volume * 5.7
