# Trade-Turnover-FIGI-Search-Tinkoff
<p align="center">
  <img src="https://raw.githubusercontent.com/serctn/Trade-Turnover-FIGI-Search/refs/heads/main/icon.ico" alt="Program Icon">
</p>

## Описание

**Trade-Turnover-FIGI-Search** — это программа для автоматизации торговли на платформе **Тинькофф Инвестиции (Т-Банк)**, которая помогает достичь нужного оборота для получения статуса **квалифицированного инвестора**. Она автоматически покупает и продаёт ценные бумаги, что ускоряет выполнение оборота.

Также программа поддерживает поиск **FIGI** — уникальных идентификаторов финансовых инструментов (акции, облигации, ETF и другие), что даёт возможность гибкого выбора активов для накрутки оборота.

#### Основные функции:
- **Автоматическая торговля**: Покупка и продажа акций, облигаций, ETF и других инструментов для накрутки оборота.
- **Поиск FIGI**: Поиск уникальных идентификаторов финансовых инструментов для работы с любыми активами.
- **Отслеживание прогресса**: Программа выводит информацию о количестве операций, накрученном обороте и потерях.
- **Мониторинг скорости**: Программа показывает, сколько рублей в секунду накручивается с помощью библиотеки `tqdm`.

## Использование

Если у вас **Windows 64-бита**, вы можете скачать и запустить готовую сборку:

- [Скачать .exe файл](https://github.com/serctn/Trade-Turnover-FIGI-Search/releases/download/Trade-Turnover-FIGI-Search/TradeTurnover.FIGI.Search-x64.exe)

- [Проверка на VirusTotal](https://www.virustotal.com/gui/file/d7b6271fb3020cb16c4ca8d05eda9c5c355bb1b87a6635a9b4b835e53dcc144a)

После загрузки просто запустите **.exe файл**, и программа начнёт работу.

## Установка и запуск через интерпретатор Python

1. **Установите Python версии 3.12.6:**
   - Если Python уже установлен, пропустите этот шаг
   - Скачайте Python 3.12.6 с официального сайта по [этой ссылке](https://www.python.org/downloads/release/python-3126/).
   - Следуйте инструкциям установщика. Обязательно отметьте опцию **"Add Python to PATH"** перед началом установки.

2. **Установите Git:**
   - Если Git уже установлен, пропустите этот шаг
   - Скачайте и установите Git с официального сайта по [этой ссылке](https://git-scm.com/downloads).
   - Следуйте стандартным инструкциям установщика, оставив все параметры по умолчанию.

3. **Скачайте репозиторий программы и установите зависимости:**
   
   Откройте командную строку или терминал и выполните следующие команды:
   ```bash
   git clone https://github.com/PlyMxt/Trade-Turnover-FIGI-Search-Tinkoff.git
   cd Trade-Turnover-FIGI-Search-Tinkoff
   pip install -r requirements.txt
   ```

4. **Запустите программу:**
   ```bash
   py main.py
   ```
