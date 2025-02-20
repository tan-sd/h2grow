from constants import TELEGRAM_BOT_KEY
from utils.telegram_handlers import start, send_reminder, forecast, edit_reminder
from telegram.ext import ApplicationBuilder, ConversationHandler, CommandHandler
import datetime
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
    application.add_handler(CommandHandler('send_reminder', send_reminder))
    application.add_handler(CommandHandler('forecast', forecast))
    application.add_handler(CommandHandler('editreminder', edit_reminder))

    job_queue.run_daily(
        send_reminder,
        datetime.time(hour=8, minute=0, tzinfo=pytz.timezone('Asia/Kuala_Lumpur')),
        name="daily_reminder"
    )

    application.run_polling()

if __name__ == '__main__':
    main()