import os
import sys
import feedparser
from sql import db
from time import sleep, time
from pyrogram import Client, filters
from pyrogram.errors import FloodWait
from apscheduler.schedulers.background import BackgroundScheduler


try:
    api_id = 10247139   # Get it from my.telegram.org
    api_hash = "96b46175824223a33737657ab943fd6a"   # Get it from my.telegram.org
    feed_urls = "https://siftrss.com/f/1LNyVoo9RP" # RSS Feed URL of the site.
    bot_token = "6260118289:AAGh0xHLLAVaBOed8sPMFEoL5QhwNDN-qvc"   # Get it by creating a bot on https://t.me/botfather
    log_channel = -1001900103251   # Telegram Channel ID where the bot is added and have write permission. You can use group ID too.
    check_interval = 30   # Check Interval in seconds.  
    max_instances = 3  # Max parallel instance to be used.
    str_session = ""    #String session generate using your tg mobile number for sending mirror cmd on your behalf. Generate using python gen_str.py
    mirr_chat = ""     #Group/chat_id of mirror chat or mirror bot to send mirror cmd
    mirr_cmd = ""    #if you have changed default cmd of mirror bot, replace this.
except Exception as e:
    print(e)
    print("One or more variables missing or have error. Exiting !")
    sys.exit(1)


for feed_url in feed_urls:
    if db.get_link(feed_url) == None:
        db.update_link(feed_url, "*")


app = Client(":memory:", api_id=api_id, api_hash=api_hash, bot_token=bot_token)
app2 = None
if str_session is not None and str_session != "":
    app2 = Client(str_session, api_id=api_id, api_hash=api_hash)

def create_feed_checker(feed_url):
    def check_feed():
        FEED = feedparser.parse(feed_url)
        if len(FEED.entries) == 0:
            return
        entry = FEED.entries[0]
        if entry.id != db.get_link(feed_url).link:
                       # ↓ Edit this message as your needs.
            if "eztv.re" in entry.link:   
                message = f"{mirr_cmd} {entry.links[1]['href']} \n\nTitle ⏩ {entry.title} \n\n⚠️ EZTV"
            elif "yts.mx" in entry.link:
                message = f"{mirr_cmd} {entry.links[1]['href']} \n\nTitle ⏩ {entry.title} \n\n⚠️ YTS"
            elif "rarbg" in entry.link:
                message = f"{mirr_cmd} {entry.link} \n\nTitle ⏩ {entry.title} \n\n⚠️ RARBG"
            elif "watercache" in entry.link:
                message = f"{mirr_cmd} {entry.link} \n\nTitle ⏩ {entry.title} \n\n⚠️ TorrentGalaxy"
            elif "limetorrents.pro" in entry.link:
                message = f"{mirr_cmd} {entry.link} \n\nTitle ⏩ {entry.title} \n\n⚠️ LimeTorrents"
            elif "etorrent.click" in entry.link:
                message = f"{mirr_cmd} {entry.link} \n\nTitle ⏩ {entry.title} \n\n⚠️ ETorTV"
            else:
                message = f"{mirr_cmd} {entry.link} \n\nTitle ⏩ {entry.title} \n\n⚠️ ThePirateBay"
            try:
                msg = app.send_message(log_channel, message)
                if app2 is not None:
                    mirr_msg = f"{mirr_cmd} {entry.link}"
                    app2.send_message(mirr_chat, message)
                db.update_link(feed_url, entry.id)
            except FloodWait as e:
                print(f"FloodWait: {e.x} seconds")
                sleep(e.x)
            except Exception as e:
                print(e)
        else:
            print(f"Checked RSS FEED: {entry.id}")
    return check_feed


scheduler = BackgroundScheduler()
for feed_url in feed_urls:
    feed_checker = create_feed_checker(feed_url)
    scheduler.add_job(feed_checker, "interval", seconds=check_interval, max_instances=max_instances)
scheduler.start()
if app2 is not None:
    app2.start()
app.run()
