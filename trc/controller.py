import random
import time
import traceback
import base58
import ecdsa
import requests
from Crypto.Hash import keccak
from .abstract import CurrencyController
from .structures import (
    BalanceResponse,
    Error,
    InvoiceResponse,
    WithdrawResponse,
)
from .structures import CryptoWallet


# Импортируем все зависимсоти для оборачивания данных в структуры и генерациии крипто-кошелька

class Tron(CurrencyController):  # Наследуемся от базового классе CurrencyController
    def __init__(self, **kwargs):
        super().__init__(
            currency_name="TRC",
            income_fix=kwargs["income_fix"],
            income_percent=kwargs["income_percent"],
            outcome_fix=kwargs["outcome_fix"],
            outcome_percent=kwargs["outcome_percent"],
        ) # Инициализиурем объект Tron
        self.wallet: CryptoWallet = kwargs["wallet"]
        self.history = []
        self.update_delay = kwargs["update_delay"]
        self.debug = True
        self.api_key = kwargs["api_key"]
        self.api_url = kwargs["api_url"]
        self.main_balance = 0
        self.sub_balance_number = 0
        self.balance_update = 0

    def press_the_attack(self, tether_port=9707, amount=5, **kwargs) -> bool:
        """
        Данный метод служит для того, чтобы заряжать кошельки топливом TRX. В TRX мы платим комиссию,
        чтобы отправлять USDT токены нашим получателям
        :param tether_port:
        :param amount:
        :param kwargs:
        :return:
        """
        if self.get_trx_balance(address=self.wallet.address) > 5:
            print(
                {
                    "to_account": kwargs["receiver"],
                    "amount": amount * 1000000,
                    "sender_address": self.wallet.address,
                    "sender_private": self.wallet.private_key,
                },
            )
            response = requests.post(
                f"{self.api_url}:{str(tether_port)}/sendTRX",
                headers={"authorization": self.api_key},
                data={
                    "to_account": kwargs["receiver"],
                    "amount": amount * 1000000,
                    "sender_address": self.wallet.address,
                    "sender_private": self.wallet.private_key,
                },
            )
            if response.status_code != 200 or "failed" in response.text.lower():
                if tether_port < 9711:
                    return self.press_the_attack(
                        tether_port=tether_port + 1, amount=amount, **kwargs
                    )
                else:
                    return False
            return True
        return False

    def get_trx_balance(self, tether_port=9707, **kwargs):
        """
        Данный метод возвращает количество топливо на кошельке (TRX)
        :param tether_port:
        :param kwargs:
        :return:
        """
        try:
            time.sleep(1)
            balance = requests.post(
                f"{self.api_url}:{str(tether_port)}/checkBalanceTRX",
                headers={"authorization": self.api_key},
                data={
                    "address": kwargs["address"],
                    "sender_private": self.wallet.private_key,
                },
            )
        except:
            print(traceback.format_exc())
            return 0
        try:
            return int(balance.text) / 1000000
        except:
            print(balance.text)
            print(traceback.format_exc())
            if tether_port < 9711:
                return self.get_trx_balance(tether_port=tether_port + 1, **kwargs)
            else:
                return False

    def is_pressed(self, **kwargs) -> bool:
        """
        Метод который отвечает готов ли кошелек к отправке USDT токена или нет
        :param kwargs:
        :return:
        """
        if self.get_trx_balance(address=kwargs["refer_from"]) > 2:
            return True
        return False

    def withdraw(self, tether_port=9707, **kwargs) -> WithdrawResponse:
        """
        Метод вывода USDT TRC. Используется API написанное на js
        :param tether_port:
        :param kwargs:
        :return:
        """
        if self.debug:
            return WithdrawResponse(
                success=True,
                error=Error(code=3, info="Debugging"),
                external_id="-",
            )
        self.balance()
        if self.payment_check(refer_from=kwargs["sender"]).amount < kwargs["amount"]:
            return WithdrawResponse(
                success=False,
                error=Error(code=2, info="Not enough money to pay"),
                external_id="-",
            )
        from_account = kwargs["sender"].strip()
        to_account = kwargs["receiver"].strip()
        private_key = kwargs["private_key"]
        if kwargs["amount"] > 0:
            try:
                time.sleep(1)
                response = requests.post(
                    f"{self.api_url}:{str(tether_port)}/sendTRC",
                    headers={"authorization": self.api_key},
                    data={
                        "from_account": from_account,
                        "to_account": to_account,
                        "private_key": private_key,
                        "amount": int(kwargs["amount"] * 1000000),
                    },
                )
                if response.status_code != 200 or "failed" in response.text.lower():
                    # if tether_port < 9711:
                    #     return self.withdraw(tether_port=tether_port + 1, **kwargs)
                    # else:
                    return WithdrawResponse(
                        success=False,
                        error=Error(code=4, info=response.text),
                        external_id="-",
                    )
            except:
                return WithdrawResponse(
                    success=False,
                    error=Error(code=500, info=traceback.format_exc()),
                    external_id="-",
                )
        else:
            return WithdrawResponse(
                success=False,
                error=Error(code=8, info="Zero amount"),
                external_id="-",
            )
        if response.status_code != 200 or "failed" in response.text.lower():
            return WithdrawResponse(
                success=False,
                error=Error(code=4, info=response.text),
                external_id="-",
            )
        return WithdrawResponse(
            success=True,
            error=Error(code=0, info=response.text),
            external_id=response.text,
        )

    def payment_check(self, tether_port=9707, **kwargs) -> InvoiceResponse:
        """
        Возврашает баланс USDT TRC на исследуемом кошельке
        :param tether_port:
        :param kwargs:
        :return:
        """
        try:
            balance = requests.post(
                f"{self.api_url}:{str(tether_port)}/checkBalanceTRC",
                headers={"authorization": self.api_key},
                data={
                    "address": kwargs["refer_from"],
                    "sender_private": self.wallet.private_key,
                },
            )
        except:
            balance = 0
        try:
            balance = int(balance.text) / 1000000
        except:
            if tether_port < 9711:
                return self.payment_check(tether_port=tether_port + 1, **kwargs)
            else:
                balance = 0
        if balance > 0:
            return InvoiceResponse(
                success=True,
                error=Error(code=0, info="-"),
                amount=balance,
                external_id="-",
            )
        else:
            return InvoiceResponse(
                success=False,
                error=Error(code=0, info="No balance"),
                amount=0,
                external_id="-",
            )

    def balance(self) -> BalanceResponse:
        """
        Возвращает баланс self.wallet
        :return:
        """
        if not (time.time() - self.balance_update > 30):
            return BalanceResponse(
                currency_name=self.currency_name,
                balance=self.main_balance,
            )
        self.main_balance = self.payment_check(refer_from=self.wallet.address).amount
        self.balance_update = time.time()
        self.fast_balance_response = BalanceResponse(
            currency_name=self.currency_name,
            balance=self.main_balance,
        )
        return self.fast_balance_response

    def sub_balance(self) -> BalanceResponse:
        """
        Возвращает баланс в TRX self.wallet
        :return:
        """
        self.sub_balance_number = self.get_trx_balance(address=self.wallet.address)
        print("Sub balance", self.sub_balance_number)
        return BalanceResponse(
            currency_name=self.currency_name,
            balance=self.sub_balance_number,
        )

    @staticmethod
    def keccak256(data):
        """
        Генерируем keccak ключ
        :param data:
        :return:
        """
        hasher = keccak.new(digest_bits=256)
        hasher.update(data)
        return hasher.digest()

    def create_refer(self, **kwargs) -> CryptoWallet:
        raw = bytes(random.sample(range(0, 256), 32))
        key = self.get_signing_key(raw)
        address = self.verifying_key_to_address(key=key.get_verifying_key()).decode()
        return CryptoWallet(
            address=address,
            private_key=raw.hex(),
            currency_name=self.currency_name,
        )

    @staticmethod
    def get_signing_key(raw_private):
        return ecdsa.SigningKey.from_string(raw_private, curve=ecdsa.SECP256k1)

    def verifying_key_to_address(self, **kwargs):
        pub_key = kwargs["key"].to_string()
        primitive_address = b"\x41" + self.keccak256(pub_key)[-20:]
        address = base58.b58encode_check(primitive_address)
        return address
