import os
import requests
import time
import random
from typing import Optional, Dict, Any
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler, CallbackQueryHandler
import logging

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Conversation states
WAITING_FOR_ADMISSION, WAITING_FOR_NAME = range(2)

# API endpoint
API_URL = "https://api.eaes.et/api/v1/results/web"

# User agents for rotation
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:89.0) Gecko/20100101 Firefox/89.0"
]

class Grade12ResultBot:
    def __init__(self, token: str):
        self.token = token
        self.application = Application.builder().token(token).build()
        self.setup_handlers()
    
    def setup_handlers(self):
        """Setup all bot handlers"""
        # Conversation handler for checking results
        conv_handler = ConversationHandler(
            entry_points=[
                CommandHandler('start', self.start_command),
                CommandHandler('check', self.start_check_command),
                CallbackQueryHandler(self.start_check_from_button, pattern='^start_check$')
            ],
            states={
                WAITING_FOR_ADMISSION: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.get_admission_number)],
                WAITING_FOR_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.get_first_name)],
            },
            fallbacks=[CommandHandler('cancel', self.cancel_command)],
        )
        
        self.application.add_handler(conv_handler)
        self.application.add_handler(CommandHandler('help', self.help_command))
        self.application.add_handler(CallbackQueryHandler(self.help_from_button, pattern='^help$'))
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Start the conversation"""
        welcome_message = """
🎓 *Welcome to Grade 12 Results Checker!*

I can help you check your Ethiopian Grade 12 examination results quickly and easily.

📋 *What I need from you:*
1️⃣ Your admission number
2️⃣ Your first name

🔍 *How to use:*
• Send /check to start checking your results
• Send /help if you need assistance
• Send /cancel anytime to stop

Let's get started! Send /check to begin. 🚀
        """
        
        keyboard = [
            [InlineKeyboardButton("🔍 Check Results", callback_data="start_check")],
            [InlineKeyboardButton("❓ Help", callback_data="help")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            welcome_message, 
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
        return ConversationHandler.END
    
    async def start_check_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Start the result checking process"""
        message = """
📝 *Step 1 of 2: Admission Number*

Please send me your **admission number**.

💡 *Tip:* This is the number you received when you registered for the exam.

Example: 1234567890
        """
        
        await update.message.reply_text(message, parse_mode='Markdown')
        return WAITING_FOR_ADMISSION
    
    async def get_admission_number(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Get admission number from user"""
        admission_no = update.message.text.strip()
        
        if not admission_no:
            await update.message.reply_text(
                "❌ Please enter a valid admission number.\n\nTry again:"
            )
            return WAITING_FOR_ADMISSION
        
        # Store admission number in context
        context.user_data['admission_no'] = admission_no
        
        message = f"""
✅ *Admission Number Received: {admission_no}*

📝 *Step 2 of 2: First Name*

Now please send me your **first name** exactly as it appears on your exam registration.

💡 *Tip:* Use the same spelling as in your official documents.
        """
        
        await update.message.reply_text(message, parse_mode='Markdown')
        return WAITING_FOR_NAME
    
    async def get_first_name(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Get first name and process the request"""
        first_name = update.message.text.strip()
        
        if not first_name:
            await update.message.reply_text(
                "❌ Please enter a valid first name.\n\nTry again:"
            )
            return WAITING_FOR_NAME
        
        # Get stored admission number
        admission_no = context.user_data.get('admission_no', '')
        
        # Send processing message
        processing_msg = await update.message.reply_text(
            "🔍 *Checking your results...*\n\n⏳ Please wait while I fetch your information from the server.\n\nThis may take a few moments...",
            parse_mode='Markdown'
        )
        
        try:
            # Make API request
            result_data = await self.make_api_request(admission_no, first_name)
            
            if result_data:
                await self.send_results(update, result_data)
            else:
                await update.message.reply_text(
                    "❌ *Sorry, I couldn't find your results.*\n\n"
                    "This could be because:\n"
                    "• The admission number or name is incorrect\n"
                    "• The server is currently busy\n"
                    "• Your results are not yet available\n\n"
                    "💡 *Try again:* Send /check to start over",
                    parse_mode='Markdown'
                )
        
        except Exception as e:
            logger.error(f"Error processing request: {e}")
            await update.message.reply_text(
                "❌ *An error occurred while checking your results.*\n\n"
                "Please try again later or contact support.\n\n"
                "💡 *Try again:* Send /check to start over",
                parse_mode='Markdown'
            )
        
        # Clear user data
        context.user_data.clear()
        return ConversationHandler.END
    
    async def make_api_request(self, admission_no: str, first_name: str, max_retries: int = 3) -> Optional[Dict[Any, Any]]:
        """Make API request with retry mechanism"""
        
        for attempt in range(max_retries):
            try:
                # Random delay to avoid overwhelming the server
                if attempt > 0:
                    delay = min(2 ** attempt + random.uniform(0, 1), 10)
                    time.sleep(delay)
                
                # Rotate user agent
                user_agent = random.choice(USER_AGENTS)
                
                # Request payload
                payload = {
                    "admissionNo": admission_no,
                    "firstName": first_name,
                    "turnstileToken": ""
                }
                
                # Headers
                headers = {
                    "Content-Type": "application/json",
                    "User-Agent": user_agent,
                    "Accept": "application/json, text/plain, */*",
                    "Accept-Language": "en-US,en;q=0.9",
                    "Accept-Encoding": "gzip, deflate, br",
                    "Connection": "keep-alive",
                    "Referer": "https://eaes.et/",
                    "Origin": "https://eaes.et"
                }
                
                # Send POST request
                response = requests.post(
                    API_URL, 
                    json=payload, 
                    headers=headers, 
                    timeout=30,
                    allow_redirects=True
                )
                
                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 429:  # Too Many Requests
                    time.sleep(5 + random.uniform(0, 3))
                elif response.status_code == 503:  # Service Unavailable
                    time.sleep(3 + random.uniform(0, 2))
                    
            except requests.exceptions.Timeout:
                logger.warning(f"Request timeout (attempt {attempt + 1})")
            except requests.exceptions.ConnectionError:
                logger.warning(f"Connection error (attempt {attempt + 1})")
            except Exception as e:
                logger.error(f"Request error: {e}")
        
        return None
    
    async def send_results(self, update: Update, data: Dict[Any, Any]) -> None:
        """Send formatted results to user"""
        student = data.get('studentInfo', {})
        results = data.get('results', [])
        
        # Student information
        student_info = f"""
👨‍🎓 *STUDENT INFORMATION*

📝 **Name:** {student.get('FullName', 'N/A')}
🎓 **Admission No:** {student.get('Admission_No', 'N/A')}
👤 **Gender:** {student.get('Sex', 'N/A')}
🏫 **School:** {student.get('School', 'N/A')}
📚 **Stream:** {student.get('Stream', 'N/A')}
        """
        
        await update.message.reply_text(student_info, parse_mode='Markdown')
        
        # Display subject results and get total from last item
        total_result = 0
        if results:
            results_text = "📊 *SUBJECT RESULTS*\n\n"
            for result in results:
                subject = result.get('Subject', 'N/A')
                grade = result.get('Result', 'N/A')
                results_text += f"📖 **{subject}:** {grade}\n"
            
            # Get total result from the last item in the array
            if results:
                last_result = results[-1]
                total_grade = last_result.get('Result', 'N/A')
                
                # Try to convert the last result to number for comparison
                try:
                    if isinstance(total_grade, (int, float)):
                        total_result = total_grade
                    elif isinstance(total_grade, str) and total_grade.replace('.', '').isdigit():
                        total_result = float(total_grade)
                except (ValueError, TypeError):
                    total_result = 0
                
                results_text += f"\n🎯 **Total Result:** {total_grade}"
            
            await update.message.reply_text(results_text, parse_mode='Markdown')
        else:
            await update.message.reply_text("📊 *No subject results found.*", parse_mode='Markdown')
        
        # Send appropriate GIF based on total result
        await self.send_result_gif(update, total_result)
        
        # Success message with options
        keyboard = [
            [InlineKeyboardButton("🔍 Check Another Result", callback_data="start_check")],
            [InlineKeyboardButton("❓ Help", callback_data="help")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "✅ *Results retrieved successfully!*\n\n"
            "Need to check another result? Use the button below:",
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
    
    async def send_result_gif(self, update: Update, total_result: float) -> None:
        """Send appropriate GIF based on total result"""
        try:
            if total_result > 300:
                # Send celebration GIF for passing
                gif_path = "assets/tom-and-jerry-throwing-flowers-celebration-dance.gif"
                message = "🎉 *Congratulations! You passed!* 🎉\n\nYour hard work paid off!"
                
                with open(gif_path, 'rb') as gif_file:
                    await update.message.reply_animation(
                        animation=gif_file,
                        caption=message,
                        parse_mode='Markdown'
                    )
            else:
                # Send sad GIF for not passing
                gif_path = "assets/sushichaeng-tom-and-jerry.gif"
                message = "😔 *You didn't pass this time*\n\nDon't give up! You can try again next time. Keep studying and you'll succeed! 💪"
                
                with open(gif_path, 'rb') as gif_file:
                    await update.message.reply_animation(
                        animation=gif_file,
                        caption=message,
                        parse_mode='Markdown'
                    )
        except FileNotFoundError as e:
            logger.error(f"GIF file not found: {e}")
            # Fallback message if GIF files are not found
            if total_result > 300:
                await update.message.reply_text(
                    "🎉 *Congratulations! You passed!* 🎉\n\nYour hard work paid off!",
                    parse_mode='Markdown'
                )
            else:
                await update.message.reply_text(
                    "😔 *You didn't pass this time*\n\nDon't give up! You can try again next time. Keep studying and you'll succeed! 💪",
                    parse_mode='Markdown'
                )
        except Exception as e:
            logger.error(f"Error sending GIF: {e}")
            # Fallback message if there's any error
            if total_result > 300:
                await update.message.reply_text(
                    "🎉 *Congratulations! You passed!* 🎉\n\nYour hard work paid off!",
                    parse_mode='Markdown'
                )
            else:
                await update.message.reply_text(
                    "😔 *You didn't pass this time*\n\nDon't give up! You can try again next time. Keep studying and you'll succeed! 💪",
                    parse_mode='Markdown'
                )
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Send help information"""
        help_text = """
❓ *How to Use Grade 12 Results Checker*

🔍 *To check your results:*
1. Send /check or click "Check Results"
2. Enter your admission number
3. Enter your first name
4. Wait for your results!

📋 *Commands:*
• /start - Welcome message
• /check - Start checking results
• /help - Show this help message
• /cancel - Cancel current operation

💡 *Tips:*
• Make sure your admission number and name are correct
• Use the same spelling as in your official documents
• If results aren't found, double-check your information

🆘 *Need more help?*
Contact the bot administrator for assistance.
        """
        
        keyboard = [
            [InlineKeyboardButton("🔍 Check Results", callback_data="start_check")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            help_text, 
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
    
    async def cancel_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Cancel the current operation"""
        context.user_data.clear()
        await update.message.reply_text(
            "❌ *Operation cancelled.*\n\n"
            "Send /check to start checking results again.",
            parse_mode='Markdown'
        )
        return ConversationHandler.END
    
    async def start_check_from_button(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Handle start check button callback"""
        query = update.callback_query
        await query.answer()
        
        # Send the same message as start_check_command but as a reply to the button
        message = """
📝 *Step 1 of 2: Admission Number*

Please send me your **admission number**.

💡 *Tip:* This is the number you received when you registered for the exam.

Example: 1234567890
        """
        
        await query.message.reply_text(message, parse_mode='Markdown')
        return WAITING_FOR_ADMISSION
    
    async def help_from_button(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle help button callback"""
        query = update.callback_query
        await query.answer()
        
        help_text = """
❓ *How to Use Grade 12 Results Checker*

🔍 *To check your results:*
1. Send /check or click "Check Results"
2. Enter your admission number
3. Enter your first name
4. Wait for your results!

📋 *Commands:*
• /start - Welcome message
• /check - Start checking results
• /help - Show this help message
• /cancel - Cancel current operation

💡 *Tips:*
• Make sure your admission number and name are correct
• Use the same spelling as in your official documents
• If results aren't found, double-check your information

🆘 *Need more help?*
Contact the bot administrator for assistance.
        """
        
        keyboard = [
            [InlineKeyboardButton("🔍 Check Results", callback_data="start_check")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.message.reply_text(
            help_text, 
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
    
    def run(self):
        """Start the bot"""
        logger.info("Starting Grade 12 Results Bot...")
        self.application.run_polling(allowed_updates=Update.ALL_TYPES)

def main():
    """Main function"""
    # Get bot token from environment variable
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    
    if not bot_token:
        print("❌ Error: TELEGRAM_BOT_TOKEN environment variable not set!")
        print("\nTo set up your bot:")
        print("1. Create a bot with @BotFather on Telegram")
        print("2. Get your bot token")
        print("3. Set the environment variable:")
        print("   export TELEGRAM_BOT_TOKEN='your_bot_token_here'")
        print("4. Run this script again")
        return
    
    # Create and run bot
    bot = Grade12ResultBot(bot_token)
    bot.run()

if __name__ == '__main__':
    main()
