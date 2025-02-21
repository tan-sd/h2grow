from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from constants import CHANNEL_ID, NEA_24_HOUR_FORECAST_URL, NEA_2_HOUR_FORECAST_URL
from datetime import datetime
import requests
import pytz

# Default reminder time
reminder_time = {"hour": 8, "minute": 0}

# Default roster
roster = {
    "Monday": "Daniel Tan",
    "Tuesday": "Aidan Lee",
    "Wednesday": "Kelvin Lim",
    "Thursday": "Tan Sheng Da",
    "Friday": "Zachary Wah",
    "Saturday": "Angela Wee",
    "Sunday": "Nicole Tay"
}

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
            "I can help you to manage and send watering reminders for the community garden.\n\n"
            "You can control me by sending these commands:\n\n"
            
            "*Reminders*:\n"
            "/showreminder - List reminder\n"
            "/editreminder - Edit reminder\n\n"

            "*Roster*:\n"
            "/showroster - Show roster\n"
            "/editroster - Edit roster\n\n"

            "*Weather*:\n"
            "/forecast - View weather forecast\n\n",
            
            parse_mode='Markdown'
        )
    return ConversationHandler.END

"""REMINDERS"""
async def send_reminder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Sends the watering reminder to the Telegram Channel."""
    job = context.job

    # Fetch latest weather data
    hour_24_forecast = await fetch_weather()

    # Get today's date and day
    today = datetime.now().strftime("%A, %d %B %Y")

    if hour_24_forecast in dry_weather:
        watering_message = "💧 *Please water the plants today!*\nLet's keep them happy and hydrated. 🌿✨"
    elif hour_24_forecast in light_moderate_rain:
        watering_message = "⚠️ *Light rain expected!*\nConsider checking soil moisture before watering."
    elif hour_24_forecast in heavy_rain:
        watering_message = "🌧 *No watering needed today!*\nThe rain will take care of it. ☔️"

    message = (
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"📅 *{today}*\n"
        f"☁️ *Weather Forecast:* {hour_24_forecast}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"{watering_message}\n\n"
        f"🌍 *Sustainable Gardening Together!* 🌱"
    )

    print("✅ Daily reminder sent.")
    
    await context.bot.send_message(
        chat_id=CHANNEL_ID,
        text=message,
        parse_mode="markdown"
    )

async def show_reminder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Shows the current reminder time in 24-hour format."""
    global reminder_time
    time_str = f"{reminder_time['hour']:02d}:{reminder_time['minute']:02d}"
    await update.message.reply_text(
        text=f"🔔 *Daily Reminder Time*: {time_str}",
        parse_mode="markdown"
    )

async def edit_reminder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Allows users to edit the reminder time (HH:MM)."""
    global reminder_time
    
    if len(context.args) != 1:
        await update.message.reply_text("⏰ Usage: /editreminder HH:MM (24-hour format)")
        return

    try:
        time_str = context.args[0]
        new_time = datetime.strptime(time_str, "%H:%M").time()

        reminder_time["hour"] = new_time.hour
        reminder_time["minute"] = new_time.minute

        job_queue = context.job_queue
        if job_queue is None:
            await update.message.reply_text("❌ Error: Job queue is not available.")
            return
        
        old_jobs = job_queue.get_jobs_by_name("daily_reminder")
        for job in old_jobs:
            job.schedule_removal()

        job_queue.run_daily(
            send_reminder,
            time=new_time.replace(tzinfo=pytz.timezone('Asia/Kuala_Lumpur')),
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
        f"*Monday*: {roster['Monday']}\n"
        f"*Tuesday*: {roster['Tuesday']}\n"
        f"*Wednesday*: {roster['Wednesday']}\n"
        f"*Thursday*: {roster['Thursday']}\n"
        f"*Friday*: {roster['Friday']}\n"
        f"*Saturday*: {roster['Saturday']}\n"
        f"*Sunday*: {roster['Sunday']}\n",
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

    day = context.args[0].capitalize()
    name = " ".join(context.args[1:])  # Combine multiple words for the name

    if day not in roster:
        await update.message.reply_text(
            text="❌*Invalid day!* Please enter a valid day (Monday to Sunday)",
            parse_mode="markdown"
        )
        return

    # Update the roster
    roster[day] = name
    await update.message.reply_text(
        text=f"✅ *Roster updated!* {day} is now assigned to {name}",
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