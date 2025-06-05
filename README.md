# Gopnik Weather Bot

This Telegram bot gives you weather updates with clothing advice in a friendly Russian street style.

## Features
- Replies to `/start` with a greeting and asks for your location or city name.
- Uses free [Open-Meteo](https://open-meteo.com/) APIs to get current weather.
- Generates simple clothing advice based on temperature, precipitation and wind.
- All responses are in Russian with a casual "gopnik" tone.
- No paid services or API keys required (only your Telegram bot token).

## Installation and Usage

Follow these steps on macOS Sequoia 15.5 (or later) with Python 3.10+.
The bot relies on `python-telegram-bot` version 21 or newer, so installing
packages from `requirements.txt` is important.

### 1. Install Python libraries
Open Terminal and run:
```bash
python3 -m pip install --user -r requirements.txt
```
This installs `python-telegram-bot` and `requests` into your user Python environment.

### 2. Get a Telegram bot token
1. In Telegram, talk to [@BotFather](https://t.me/BotFather).
2. Use `/newbot` to create a bot and copy the token you receive.
3. Keep this token safe—it allows your script to send messages.

### 3. Prepare the script
Place `gopnik_weather_bot.py` and `requirements.txt` in a directory, for example `~/gopnik_bot/`.

### 4. Set the token and run
In Terminal, navigate to that directory and set the environment variable before running:
```bash
export TELEGRAM_BOT_TOKEN=YOUR_TOKEN_HERE
python3 gopnik_weather_bot.py
```
Leave the script running to keep the bot online. Press `Ctrl+C` to stop.

## Example interaction
```
/start
👉 Bot: "Здарова, Артём! Поделись локацией или напиши свой город, посмотрим что там по погоде."
```
Share your location or type a city, and you'll receive the current weather with advice like:
```
Братан, в Москве сейчас 5°C, осадки 2мм, ветер 4 м/с — куртку не забудь
```

Enjoy!
