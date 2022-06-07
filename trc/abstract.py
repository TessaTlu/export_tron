from abc import ABC, abstractmethod

from .structures import (
    BalanceResponse,
    InvoiceResponse,
    WithdrawResponse,
    BaseRefer
)


class CurrencyController(ABC):
    def __init__(self, **kwargs):
        self.currency_name: str = kwargs["currency_name"]
        self.income_percent = kwargs["income_percent"]
        self.income_fix = kwargs["income_fix"]
        self.outcome_percent = kwargs["outcome_percent"]
        self.outcome_fix = kwargs["outcome_fix"]
        self.fast_balance_response: BalanceResponse = BalanceResponse(
            currency_name=self.currency_name,
            balance=0,
        )

    @abstractmethod
    def withdraw(self) -> WithdrawResponse:
        pass

    @abstractmethod
    def balance(self) -> BalanceResponse:
        pass

    @abstractmethod
    def is_pressed(self) -> bool:
        pass

    @abstractmethod
    def press_the_attack(self) -> bool:
        pass

    @abstractmethod
    def payment_check(self, **kwargs) -> InvoiceResponse:
        pass

    @abstractmethod
    def create_refer(self) -> BaseRefer.__subclasses__:
        pass

    def fast_balance(self) -> BalanceResponse:
        return self.fast_balance_response

    def calc_commission_to(self, **kwargs) -> float:
        return kwargs["request_sum"] * self.outcome_percent / 100 + self.outcome_fix

    def calc_commission_from(self, **kwargs) -> float:
        return kwargs["request_sum"] * self.income_percent / 100 + self.income_fix
