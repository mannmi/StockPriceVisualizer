from telegram import ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler
import key
import messageText
import logging

message = ""

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# Define states
QUESTION1, QUESTION2, QUESTION3 = range(3)


class python_bot(object):
    async def start_comand(update, context: ContextTypes.DEFAULT_TYPE):
        reply_keyboard = [['True', 'False']]
        await update.message.reply_text(
            "Question 1: Is the sky blue?",
            parse_mode="HTML",
            reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False, resize_keyboard=True)
        )
        return QUESTION1  # Set the state to QUESTION1

    async def help_comand(update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(messageText.welcomeMessage)

    async def handle_message(update, context) -> str:
        print(update.message.text)

    async def handle_question1(update, context: ContextTypes.DEFAULT_TYPE) -> int:
        user_reply = update.message.text
        if user_reply == 'True':
            await update.message.reply_text("Correct! The sky is blue.")
        elif user_reply == 'False':
            await update.message.reply_text("Incorrect. The sky is blue.")
        else:
            await update.message.reply_text("Invalid selection.")
            return QUESTION1  # Stay in the same state if the response is invalid

        # Move to the next question
        reply_keyboard = [['True', 'False']]
        await update.message.reply_text(
            "Question 2: Is water wet?",
            parse_mode="HTML",
            reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False, resize_keyboard=True)
        )
        return QUESTION2

    async def handle_question2(update, context: ContextTypes.DEFAULT_TYPE) -> int:
        user_reply = update.message.text
        if user_reply == 'True':
            await update.message.reply_text("Correct! Water is wet.")
        elif user_reply == 'False':
            await update.message.reply_text("Incorrect. Water is wet.")
        else:
            await update.message.reply_text("Invalid selection.")
            return QUESTION2  # Stay in the same state if the response is invalid

        # Move to the next question
        reply_keyboard = [['True', 'False']]
        await update.message.reply_text(
            "Question 3: Is fire cold?",
            parse_mode="HTML",
            reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False, resize_keyboard=False)
        )
        return QUESTION3

    async def handle_question3(update, context: ContextTypes.DEFAULT_TYPE) -> int:
        user_reply = update.message.text
        if user_reply == 'True':
            await update.message.reply_text("Incorrect. Fire is hot.")
        elif user_reply == 'False':
            await update.message.reply_text("Correct! Fire is hot.")
        else:
            await update.message.reply_text("Invalid selection.")
            return QUESTION3  # Stay in the same state if the response is invalid

        # End the conversation after the last question
        await update.message.reply_text("Thank you for answering the questions!")
        return ConversationHandler.END


if __name__ == '__main__':
    print("Start up bot...")

    # Run the bot
    application = ApplicationBuilder().token(key.Token).build()

    # Add conversation handler with the states
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', python_bot.start_comand)],
        states={
            QUESTION1: [MessageHandler(filters.TEXT & ~filters.COMMAND, python_bot.handle_question1)],
            QUESTION2: [MessageHandler(filters.TEXT & ~filters.COMMAND, python_bot.handle_question2)],
            QUESTION3: [MessageHandler(filters.TEXT & ~filters.COMMAND, python_bot.handle_question3)],
        },
        fallbacks=[CommandHandler('help', python_bot.help_comand)]
    )

    application.add_handler(conv_handler)

    # Start the bot
    application.run_polling()
