# import logging
# from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove, Update,
#                       InlineKeyboardButton, InlineKeyboardMarkup)
# from telegram.ext import (Application, CallbackQueryHandler, CommandHandler,
#                           ContextTypes, ConversationHandler, MessageHandler, filters)
# import key
#
# # Enable logging
# logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
#                     level=logging.INFO)
#
# logger = logging.getLogger(__name__)
#
# # Define states
# CAR_TYPE, CAR_COLOR, CAR_MILEAGE_DECISION, CAR_MILEAGE, PHOTO, SUMMARY = range(6)
#
#
# async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
#     """Starts the conversation and asks the user about their preferred car type."""
#     reply_keyboard = [['Sedan', 'SUV', 'Sports', 'Electric']]
#
#     await update.message.reply_text(
#         '<b>Welcome to the Car Sales Listing Bot!\n'
#         'Let\'s get some details about the car you\'re selling.\n'
#         'What is your car type?</b>',
#         parse_mode='HTML',
#         reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True),
#     )
#
#     return CAR_TYPE
#
#
#
# def main() -> None:
#     """Run the bot."""
#     application = Application.builder().token(key.Token).build()
#
#     conv_handler = ConversationHandler(
#         entry_points=[CommandHandler('start', start)],
#     )
#
#     application.add_handler(conv_handler)
#
#     # Handle the case when a user sends /start but they're not in a conversation
#     application.add_handler(CommandHandler('start', start))
#
#     application.run_polling()
#
#
# if __name__ == '__main__':
#     main()