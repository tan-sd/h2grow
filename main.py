from constants import TELEGRAM_BOT_KEY
from utils.telegram_handlers import start, send_reminder, show_reminder, edit_reminder, show_roster, edit_roster, forecast
from telegram.ext import ApplicationBuilder, ConversationHandler, CommandHandler
from utils.firebase import get_fb_reminder
from datetime import datetime, time
import pytz

def main() -> None:
    application = ApplicationBuilder().token(TELEGRAM_BOT_KEY).build()
    job_queue = application.job_queue

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={},
        fallbacks=[]
    )

    application.add_handler(conv_handler)
    application.add_handler(CommandHandler('sendreminder', send_reminder))
    application.add_handler(CommandHandler('showreminder', show_reminder))
    application.add_handler(CommandHandler('editreminder', edit_reminder))
    application.add_handler(CommandHandler('showroster', show_roster))
    application.add_handler(CommandHandler('editroster', edit_roster))
    application.add_handler(CommandHandler('forecast', forecast))

    time_str = get_fb_reminder()
    reminder_time = datetime.strptime(time_str, "%H:%M").time()
    timezone = pytz.timezone('Asia/Kuala_Lumpur')
    reminder_time = time(reminder_time.hour, reminder_time.minute, tzinfo=timezone)

    job_queue.run_daily(
        send_reminder,
        reminder_time,
        name="daily_reminder"
    )

    application.run_polling()

if __name__ == '__main__':
    main()