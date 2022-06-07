from dataclasses import dataclass


@dataclass
class Error:
    code: int
    info: str


@dataclass
class WithdrawResponse:
    success: bool
    error: Error
    external_id: str


@dataclass
class InvoiceResponse:
    success: bool
    error: Error
    external_id: str
    amount: float


@dataclass
class BalanceResponse:
    currency_name: str
    balance: float


@dataclass
class BaseRefer:
    address: str
    currency_name: str


@dataclass
class CryptoWallet(BaseRefer):
    private_key: str = None
