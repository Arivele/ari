import logging
import requests
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

# --- AI clothing advice -------------------------------------------------------

MODEL_NAME = "sberbank-ai/rugpt3small_based_on_gpt2"
_tokenizer = None
_model = None


def generate_clothing_advice(temp_c, precipitation, wind_speed):
    """Generate clothing advice using a small Russian GPT model."""
    global _tokenizer, _model
    if _tokenizer is None or _model is None:
        _tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
        _model = AutoModelForCausalLM.from_pretrained(MODEL_NAME)

    prompt = (
        f"Погода: {temp_c}°C, осадки {precipitation} мм, ветер {wind_speed} м/с. "
        "Дай совет, что надеть. Отвечай коротко и по-гопницки."
    )
    inputs = _tokenizer(prompt, return_tensors="pt")
    with torch.no_grad():
        tokens = _model.generate(
            **inputs,
            max_new_tokens=30,
            do_sample=True,
            top_p=0.9,
            temperature=0.8,
        )
    text = _tokenizer.decode(tokens[0], skip_special_tokens=True)
    # Remove the prompt part if model repeats it
    if prompt in text:
        text = text[len(prompt) :]
    return text.strip()


def get_weather_by_coords(lat, lon):
    url = (
        f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}"
        "&current_weather=true"
    )
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    current = data.get("current_weather", {})
    temp_c = current.get("temperature")
    wind_speed = current.get("windspeed")
    precipitation = current.get("precipitation", 0)
    return temp_c, wind_speed, precipitation


def get_coords_by_city(city):
    url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1&language=ru"
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    results = data.get("results")
    if not results:
        return None
    return results[0]["latitude"], results[0]["longitude"]


# Command handlers

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_first = update.effective_user.first_name
    reply_keyboard = [[KeyboardButton(text="Отправить локацию", request_location=True)]]
    await update.message.reply_text(
        f"Здарова, {user_first}! Поделись локацией или напиши свой город, посмотрим что там по погоде.",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True, one_time_keyboard=True)
    )


async def handle_location(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    lat = update.message.location.latitude
    lon = update.message.location.longitude
    temp_c, wind_speed, precipitation = get_weather_by_coords(lat, lon)
    advice = generate_clothing_advice(temp_c, precipitation, wind_speed)
    await update.message.reply_text(
        f"Сейчас {temp_c}°C, осадки {precipitation}мм, ветер {wind_speed} м/с — {advice}"
    )


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    city = update.message.text.strip()
    coords = get_coords_by_city(city)
    if not coords:
        await update.message.reply_text("Не нашёл такой город, попробуй другую локацию, брат")
        return
    lat, lon = coords
    temp_c, wind_speed, precipitation = get_weather_by_coords(lat, lon)
    advice = generate_clothing_advice(temp_c, precipitation, wind_speed)
    await update.message.reply_text(
        f"В {city} сейчас {temp_c}°C, осадки {precipitation}мм, ветер {wind_speed} м/с — {advice}"
    )


async def main() -> None:
    import os
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        raise RuntimeError("TELEGRAM_BOT_TOKEN environment variable not set")
    application = ApplicationBuilder().token(token).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.LOCATION, handle_location))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_text))

    await application.run_polling()


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
