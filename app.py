#!/usr/bin/env python3
"""
Railway-compatible version of the Grade 12 Results Bot
This version includes a simple web server for health checks
"""

import os
import asyncio
import logging
from telegram_bot import Grade12ResultBot

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def health_check():
    """Simple health check for Railway"""
    from aiohttp import web
    
    async def handler(request):
        return web.Response(text="Grade 12 Results Bot is running! 🎓", status=200)
    
    app = web.Application()
    app.router.add_get('/', handler)
    app.router.add_get('/health', handler)
    
    runner = web.AppRunner(app)
    await runner.setup()
    
    # Use Railway's PORT environment variable or default to 8080
    port = int(os.environ.get('PORT', 8080))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    
    logger.info(f"Health check server started on port {port}")
    return runner

async def main():
    """Main function to run both web server and bot"""
    # Start health check server
    web_runner = await health_check()
    
    # Start the bot
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    
    if not bot_token:
        logger.error("TELEGRAM_BOT_TOKEN environment variable not set!")
        return
    
    bot = Grade12ResultBot(bot_token)
    
    try:
        # Start bot in background
        bot_task = asyncio.create_task(
            asyncio.get_event_loop().run_in_executor(None, bot.run)
        )
        
        # Wait for both tasks
        await asyncio.gather(web_runner.cleanup(), bot_task)
        
    except KeyboardInterrupt:
        logger.info("Shutting down...")
        await web_runner.cleanup()

if __name__ == '__main__':
    asyncio.run(main())
