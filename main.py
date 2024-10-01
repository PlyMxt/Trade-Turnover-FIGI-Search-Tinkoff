from datetime import datetime, timezone
from tinkoff.invest import Client, RequestError, OrderDirection, OrderType
from tqdm import tqdm  # Прогресс-бар
import time

# Глобальные переменные для операций
total_operations = 0
total_loss = 0
last_buy_amount = 0
total_turnover = 0

def format_money(money):
    return money.units + money.nano / 1e9

def select_language():
    print("\nВыберите язык / Select language:")
    print("1 - Русский")
    print("2 - English")
    
    lang_choice = input("\nВведите номер / Enter the number: \n").strip()

    if lang_choice == '1':
        return 'ru'
    elif lang_choice == '2':
        return 'en'
    else:
        print("\nНекорректный выбор / Invalid choice")
        return select_language()

def get_accounts_info(TOKEN, lang):
    with Client(TOKEN) as client:
        accounts = client.users.get_accounts()
        accounts_info = []
        
        if lang == 'ru':
            print("\nДоступные аккаунты:\n")
        else:
            print("\nAvailable accounts:\n")
        
        for i, account in enumerate(accounts.accounts):
            positions = client.operations.get_positions(account_id=account.id)
            balances = {currency.currency: format_money(currency) for currency in positions.money}
            
            if lang == 'ru':
                print(f"{i + 1}. Аккаунт ID: {account.id}, Тип: {account.type}, Название: {account.name}")
                print("Средства на счете:", balances, "\n")
            else:
                print(f"{i + 1}. Account ID: {account.id}, Type: {account.type}, Name: {account.name}")
                print("Available funds:", balances, "\n")
            
            accounts_info.append({'id': account.id, 'type': account.type, 'name': account.name, 'balances': balances})
        
        return accounts_info

def select_account(accounts_info, lang):
    if lang == 'ru':
        account_choice = int(input("\nВыберите номер аккаунта в списке для использования (например, 1), не ID аккаунта: \n"))
    else:
        account_choice = int(input("\nSelect the number from the list of the account to use (e.g., 1), not the account ID: \n"))
    
    # Проверяем, что выбранный номер аккаунта находится в пределах доступных аккаунтов
    if 1 <= account_choice <= len(accounts_info):
        return accounts_info[account_choice - 1]['id']
    else:
        if lang == 'ru':
            print("\nНекорректный выбор. Попробуйте снова.")
        else:
            print("\nInvalid choice. Please try again.")
        return select_account(accounts_info, lang)

def get_user_input(lang):
    if lang == 'ru':
        print("\nДля получения API токена необходимо зайти на страницу https://www.tinkoff.ru/invest/settings/, прокрутить до самого низа страницы, найти раздел 'Токены API' и выпустить токен с полным доступом для всех счетов. После этого просто скопируйте его.\n")
        TOKEN = input("Введите токен API (например, t.xxxxxxxx-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx): \n")
        print("\nОбратите внимание, что для TCS00A108WX3 тикер TPAY имеет нулевую комиссию, и за накрутку оборота в 6 миллионов рублей расходы составят примерно 300 рублей. Просто является неплохим выбором)\n")
        FIGI = input("Введите FIGI инструмента (например, TCS00A108WX3): \n")
        print("\nРекомендую выбирать такое количество лотов, которое можно будет купить повторно после выполнения оборота. Например, если акция стоит 100 рублей, а на счете 1500 рублей, и после оборота комиссия составит около 300 рублей, то для ускорения процесса лучше выбрать 10 лотов акций. Чем больше стартовый капитал, тем быстрее будет происходить выполнение оборота.\n")
        quantity = int(input("Введите количество бумаг за одну операцию (лотов): \n"))
        target_turnover = float(input("\nВведите цель по обороту в цифрах (например, 100000 рублей): \n"))
        return TOKEN, FIGI, quantity, target_turnover
    else:
        print("\nTo obtain your API token, go to https://www.tinkoff.ru/invest/settings/, scroll to the bottom of the page, find the 'API Tokens' section, and generate a token with full access for all accounts. After that, just copy it.\n")
        TOKEN = input("Enter API token (for example, t.xxxxxxxx-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx): \n")
        print("\nNote that for TCS00A108WX3, the ticker TPAY has zero commission, and for a turnover of 6 million rubles, there will be approximately 300 rubles in expenses. It's just a good choice)\n")
        FIGI = input("Enter the FIGI of the instrument (for example, TCS00A108WX3): \n")
        print("\nI recommend choosing a quantity that allows you to repurchase after the turnover. For example, if a share costs 100 rubles and your balance is 1,500 rubles, and after the turnover the fees consume about 300 rubles, then in this case, to speed up the process, it's better to choose 10 lots of shares. The larger the starting capital, the faster the turnover will be.\n")
        quantity = int(input("Enter the number of shares per operation (lots): \n"))
        target_turnover = float(input("Enter the turnover target in numbers (e.g., 100000 rubles): \n"))
        return TOKEN, FIGI, quantity, target_turnover

def choose_task(lang):
    if lang == 'ru':
        
        print("\n1 - Накрутить оборот")
        print("2 - Поиск FIGI по тикеру")
        print("Выберите задачу:")
    else:
        print("\nChoose a task:")
        print("1 - Turnover trading")
        print("2 - Search for FIGI by ticker")

    choice = input("").strip()
    if choice == '1' or choice == '2':
        return choice
    else:
        if lang == 'ru':
            print("\nНекорректный выбор")
        else:
            print("\nInvalid choice")
        return choose_task(lang)

def run_order(direction, TOKEN, FIGI, account_id, quantity):
    global total_operations, total_loss, last_buy_amount, total_turnover
    try:
        with Client(TOKEN) as client:
            response = client.orders.post_order(
                order_id=str(datetime.now(timezone.utc).timestamp()),  # Используем timezone-aware datetime
                figi=FIGI, quantity=quantity, account_id=account_id,
                direction=direction, order_type=OrderType.ORDER_TYPE_MARKET
            )
            total_amount = response.total_order_amount.units + response.total_order_amount.nano / 1e9

            if direction == OrderDirection.ORDER_DIRECTION_BUY:
                last_buy_amount = total_amount
            elif direction == OrderDirection.ORDER_DIRECTION_SELL:
                total_loss += abs(last_buy_amount - total_amount)

            total_turnover += total_amount
            total_operations += 1
    except RequestError as e:
        print(f"\nError: {str(e)}")
        time.sleep(1)

def turnover_trading(TOKEN, FIGI, account_id, quantity, target_turnover, lang):
    global total_operations, total_loss, last_buy_amount, total_turnover
    with tqdm(total=target_turnover, unit=' rubles') as pbar:
        while total_turnover < target_turnover:
            run_order(OrderDirection.ORDER_DIRECTION_BUY, TOKEN, FIGI, account_id, quantity)
            time.sleep(0.4)
            run_order(OrderDirection.ORDER_DIRECTION_SELL, TOKEN, FIGI, account_id, quantity)
            time.sleep(0.4)
            pbar.update(last_buy_amount * 2)

    if lang == 'ru':
        print(f"\nВсего операций: {total_operations}")
        print(f"Общие потери: {total_loss:.2f} рублей")
    else:
        print(f"\nTotal number of operations: {total_operations}")
        print(f"Total loss: {total_loss:.2f} rubles")

def search_figi(TOKEN, lang):
    if lang == 'ru':
        TICKER = input("\nВведите тикер (например, AFLT для Аэрофлота): \n")
        print("\nВыберите тип инструмента для поиска FIGI:")
        print("1 - Акции (Shares)")
        print("2 - Облигации (Bonds)")
        print("3 - ETF (Биржевые фонды)")
        print("4 - Валюты (Currencies)")
        print("5 - Фьючерсы (Futures)")
        print("\nВведите 'all' или 'все', чтобы искать везде.\n")
        choice = input("\nВведите номер или 'all'/'все' для поиска во всех типах: \n").strip().lower()
    else:
        TICKER = input("\nEnter ticker (for example, AFLT for Aeroflot): \n")
        print("\nSelect instrument type for FIGI search:")
        print("1 - Shares")
        print("2 - Bonds")
        print("3 - ETFs")
        print("4 - Currencies")
        print("5 - Futures")
        print("\nEnter 'all' to search across all types.\n")
        choice = input("\nEnter number or 'all' to search in all types: \n").strip().lower()

    options_map = {
        '1': 'shares',
        '2': 'bonds',
        '3': 'etfs',
        '4': 'currencies',
        '5': 'futures',
        'all': ['shares', 'bonds', 'etfs', 'currencies', 'futures'],
        'все': ['shares', 'bonds', 'etfs', 'currencies', 'futures']
    }

    if choice in ['all', 'все']:
        selected_methods = options_map['all']
    elif choice in options_map:
        selected_methods = [options_map[choice]]
    else:
        if lang == 'ru':
            print("\nНекорректный выбор")
        else:
            print("\nInvalid choice")
        return

    with Client(TOKEN) as cl:
        instruments = cl.instruments
        instrument_list = []
        for method in selected_methods:
            method_instruments = getattr(instruments, method)().instruments
            for item in method_instruments:
                instrument_list.append({
                    'ticker': item.ticker,
                    'figi': item.figi,
                    'type': method,
                    'name': item.name
                })

        # Фильтруем список по введенному тикеру
        filtered_instruments = [instr for instr in instrument_list if instr['ticker'] == TICKER]

        if not filtered_instruments:
            if lang == 'ru':
                print(f"\nТикер {TICKER} не найден\n")
            else:
                print(f"\nTicker {TICKER} not found\n")
            return

        # Получаем FIGI первого найденного инструмента
        figi = filtered_instruments[0]['figi']

        if lang == 'ru':
            print(f"\nFIGI для ТИКЕРА {TICKER}: {figi}\n")
        else:
            print(f"\nFIGI for TICKER {TICKER}: {figi}\n")

        # Добавляем вопрос о накрутке оборота
        if lang == 'ru':
            proceed_to_turnover = input("\nХотите ли вы перейти к накрутке оборота? (да/нет): \n").strip().lower()
        else:
            proceed_to_turnover = input("\nDo you want to proceed to turnover trading? (yes/no): \n").strip().lower()

        # Если пользователь соглашается, запускаем накрутку оборота
        if proceed_to_turnover in ['да', 'yes']:
            TOKEN, FIGI, quantity, target_turnover = get_user_input(lang)
            accounts_info = get_accounts_info(TOKEN, lang)
            account_id = select_account(accounts_info, lang)
            turnover_trading(TOKEN, FIGI, account_id, quantity, target_turnover, lang)

if __name__ == '__main__':
    lang = select_language()
    
    # Получаем выбор задачи: накрутка оборота или поиск FIGI по тикеру
    task = choose_task(lang)
    
    if task == '1':
        TOKEN, FIGI, quantity, target_turnover = get_user_input(lang)
        # Получаем информацию о счетах
        accounts_info = get_accounts_info(TOKEN, lang)
        # Выбираем аккаунт для использования
        account_id = select_account(accounts_info, lang)
        turnover_trading(TOKEN, FIGI, account_id, quantity, target_turnover, lang)
    elif task == '2':
        if lang == 'ru':
            print("\nДля получения API токена необходимо зайти на страницу https://www.tinkoff.ru/invest/settings/, прокрутить до самого низа страницы, найти раздел 'Токены API' и выпустить токен с полным доступом для всех счетов. После этого просто скопируйте его.")
        else:
            print("\nTo obtain your API token, go to https://www.tinkoff.ru/invest/settings/, scroll to the bottom of the page, find the 'API Tokens' section, and generate a token with full access for all accounts. After that, just copy it.")
        TOKEN = input("\nВведите ваш API токен: \n") if lang == 'ru' else input("\nEnter your API token: \n")
        search_figi(TOKEN, lang)
