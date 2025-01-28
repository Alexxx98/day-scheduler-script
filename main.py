from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from dotenv import load_dotenv
from schedule import schedule

import os
import discord
import pytz


load_dotenv()

CHANNEL_ID = os.getenv("CHANNEL_ID")
BOT_TOKEN = os.getenv("BOT_TOKEN")
TIMEZONE = pytz.timezone('Europe/Warsaw')


async def send_message(channel, message):
    await channel.send(message)


class Client(discord.Client):
    async def on_ready(self):
        print(f'Logged on as {self.user}')

        channel = self.get_channel(int(CHANNEL_ID))
        
        scheduler = AsyncIOScheduler(timezone=TIMEZONE)

        for time, task in schedule.items():
            hour, minute = time.split(':')
            scheduler.add_job(
                func=send_message,
                trigger=CronTrigger(
                    day_of_week='mon-sat',
                    hour=int(hour),
                    minute=int(minute)
                ),
                args=(channel, task)
            )

        scheduler.start()
        

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True

client = Client(intents=intents)
client.run(BOT_TOKEN)
