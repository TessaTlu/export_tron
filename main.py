from trc.controller import Tron

tron = Tron(  # инициализируем Tron класс
    income_percent=0,
    income_fix=0,
    outcome_fix=0,
    outcome_percent=0,
    api_key="",
    api_url="http://188.34.183.152",
    update_delay=15,
    wallet=None
)

crypto_wallet = tron.create_refer()
print(crypto_wallet)  # генерируем кошелек и выводим данные о нем в консоль
tron.wallet = crypto_wallet  # присваиваем tron.wallet ссылку на объект crypto_wallet
print(tron.balance())  # выводим баланс USDT токена в консоль
