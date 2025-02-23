from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from constants import CHANNEL_ID, NEA_24_HOUR_FORECAST_URL, NEA_2_HOUR_FORECAST_URL
from utils.firebase import get_fb_reminder, edit_fb_reminder, get_fb_roster, edit_fb_roster
from datetime import datetime, time
import requests
import pytz

# Retrieve the roster from Firebase
roster = get_fb_roster()

"""Define the possible values for forecast"""
# Dry & Clear Weather (No Rain), watering is needed
dry_weather = [
    "Fair",
    "Fair (Day)",
    "Fair (Night)",
    "Fair and Warm",
    "Partly Cloudy",
    "Partly Cloudy (Day)",
    "Partly Cloudy (Night)",
    "Cloudy",
    "Hazy",
    "Slightly Hazy",
    "Windy",
    "Mist",
    "Fog"
]

# Light to Moderate Rain, optional watering → check temperature and soil condition before skipping.
light_moderate_rain = [
    "Light Rain",
    "Moderate Rain",
    "Passing Showers",
    "Light Showers",
    "Showers"
]

# Heavy Rain & Thunderstorms, no watering needed → rain will take care of the plants.
heavy_rain = [
    "Heavy Rain",
    "Heavy Showers",
    "Thundery Showers",
    "Heavy Thundery Showers",
    "Heavy Thundery Showers with Gusty Winds"
]

async def fetch_weather():
    """Fetch the latest 24-hour weather forecast from NEA API."""
    response = requests.get(
        NEA_24_HOUR_FORECAST_URL,
        headers={"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"},
    )
    return response.json()["data"]["records"][0]["general"]["forecast"]["text"]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Send a welcome message and commands list."""
    if update.message: 
        message = await update.message.reply_text(
            "🌱 *Welcome to H2Grow!*\n\n"
            "I can help you to manage and send watering reminders for your community garden.\n\n"
            "You can control me by sending these commands:\n\n"
            
            "*Reminder*:\n"
            "/showreminder - Show reminder\n"
            "/editreminder - Edit reminder\n\n"

            "*Roster*:\n"
            "/showroster - Show roster\n"
            "/editroster - Edit roster\n\n"

            "*Weather*:\n"
            "/forecast - Show weather forecast\n\n",
            
            parse_mode='Markdown'
        )
    return ConversationHandler.END

"""REMINDERS"""
async def send_reminder(context: ContextTypes.DEFAULT_TYPE):
    """Sends the watering reminder to the Telegram Channel."""

    # Fetch latest weather data
    hour_24_forecast = await fetch_weather()

    # Get today's date and day
    today = datetime.now().strftime("%A, %d %B %Y")
    day_of_week = datetime.now().strftime("%A")

    # Get assigned person from the roster
    assigned_person = roster.get(day_of_week.lower(), "No one assigned")

    if hour_24_forecast in dry_weather:
        watering_message = "💧 *Please water the plants today!*\nLet's keep them happy and hydrated. 🌿✨"
    elif hour_24_forecast in light_moderate_rain:
        watering_message = "⚠️ *Light rain expected!*\nConsider checking soil moisture before watering."
    elif hour_24_forecast in heavy_rain:
        watering_message = "🌧 *No watering needed today!*\nThe rain will take care of it. ☔️"

    message = (
        f"[*Daily Reminder*]\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"📅 *{today}*\n"
        f"👤 *Gardener of the Day:* {assigned_person}\n"
        f"☁️ *Weather Forecast:* {hour_24_forecast}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"{watering_message}\n\n"
        # f"🌍 *Sustainable Gardening Together!* 🌱"
    )

    print("✅ Daily reminder sent.")
    
    await context.bot.send_message(
        chat_id=CHANNEL_ID,
        text=message,
        parse_mode="markdown"
    )

async def show_reminder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Shows the current reminder time in 24-hour format."""
    # fetch reminder time from Firebase
    reminder_time = get_fb_reminder()
    await update.message.reply_text(
        text=f"🔔 *Daily Reminder Time*: {reminder_time}",
        parse_mode="markdown"
    )

async def edit_reminder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Allows users to edit the reminder time (HH:MM)."""

    if len(context.args) != 1:
        await update.message.reply_text("⏰ Usage: /editreminder HH:MM (24-hour format)")
        return

    try:
        time_str = context.args[0]

        new_time = datetime.strptime(time_str, "%H:%M").time()
        timezone = pytz.timezone('Asia/Kuala_Lumpur')
        new_time = time(new_time.hour, new_time.minute, tzinfo=timezone)

        await edit_fb_reminder(time_str)

        job_queue = context.job_queue
        if job_queue is None:
            await update.message.reply_text("❌ Error: Job queue is not available.")
            return
        
        old_jobs = job_queue.get_jobs_by_name("daily_reminder")
        for job in old_jobs:
            job.schedule_removal()

        job_queue.run_daily(
            send_reminder,
            new_time,
            name="daily_reminder"
        )

        await update.message.reply_text(f"✅ Reminder time updated to {time_str} daily!")

    except ValueError:
        await update.message.reply_text("❌ Invalid format! Please use HH:MM in 24-hour format.")
""""""

"""ROSTER"""
async def show_roster(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Shows the current roster."""

    await update.message.reply_text(
        text="👥 *Current Roster*\n\n"
        f"*Monday*: {roster['monday']}\n"
        f"*Tuesday*: {roster['tuesday']}\n"
        f"*Wednesday*: {roster['wednesday']}\n"
        f"*Thursday*: {roster['thursday']}\n"
        f"*Friday*: {roster['friday']}\n"
        f"*Saturday*: {roster['saturday']}\n"
        f"*Sunday*: {roster['sunday']}\n",
        parse_mode="markdown"
    )

async def edit_roster(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Allows users to edit the roster."""
    if len(context.args) < 2:
        await update.message.reply_text(
            "⚠️ Usage: /editroster <day> <name>\n\n"
            "Example: `/editroster Monday John Doe`\n"
            "This updates Monday's roster to John Doe",
            parse_mode="markdown"
        )
        return

    day = context.args[0].lower()
    name = " ".join(context.args[1:])  # Combine multiple words for the name

    valid_days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]

    if day not in valid_days:
        await update.message.reply_text(
            text="❌ *Invalid day!* Please enter a valid day (Monday to Sunday)",
            parse_mode="markdown"
        )
        return
    
    await edit_fb_roster(day, name)

    # Update the roster
    roster[day] = name
    await update.message.reply_text(
        text=f"✅ *Roster updated!* {day.capitalize()} is now assigned to {name}",
        parse_mode="markdown"
    )
""""""

"""FORECAST"""
async def forecast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Sends the latest 24-hour weather forecast"""
    # Fetch latest weather data
    hour_24_forecast = await fetch_weather()
    
    # Get today's date
    today = datetime.now().strftime("%A, %d %B %Y")

    message = (
        f"*24-Hour Weather Forecast*\n\n"
        f"📅 *{today}*\n"
        f"☁️ *Weather Forecast: *{hour_24_forecast}\n\n"
    )

    await update.message.reply_text (
        text=message,
        parse_mode="markdown"
    )

    return ConversationHandler.END
""""""