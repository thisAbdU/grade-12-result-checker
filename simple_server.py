#!/usr/bin/env python3
"""
Simple HTTP server for Railway health checks
"""

import os
import threading
import time
import asyncio
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram_bot import Grade12ResultBot

class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path in ['/', '/health']:
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write('Grade 12 Results Bot is running! 🎓'.encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()

def start_web_server():
    """Start a simple web server for health checks"""
    port = int(os.environ.get('PORT', 8080))
    server = HTTPServer(('0.0.0.0', port), HealthHandler)
    print(f"Health check server started on port {port}")
    server.serve_forever()

def main():
    """Main function"""
    print("🚀 Starting Grade 12 Results Bot with health check...")
    
    # Start web server in a separate thread
    web_thread = threading.Thread(target=start_web_server, daemon=True)
    web_thread.start()
    
    # Give the web server a moment to start
    time.sleep(2)
    
    # Start the bot in the main thread
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    
    if not bot_token:
        print("❌ TELEGRAM_BOT_TOKEN environment variable not set!")
        return
    
    print("🤖 Starting Telegram bot...")
    try:
        bot = Grade12ResultBot(bot_token)
        bot.run()
    except Exception as e:
        print(f"❌ Bot error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
