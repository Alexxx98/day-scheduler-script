from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.triggers.cron import CronTrigger
from discord.ext import commands
from dotenv import load_dotenv

import os
import discord
import pytz
import plyer


load_dotenv()

# Bot env variables
GUILD_ID = os.getenv("GUILD_ID")
CHANNEL_ID = os.getenv("CHANNEL_ID")
BOT_TOKEN = os.getenv("BOT_TOKEN")
TIMEZONE = pytz.timezone('Europe/Warsaw')

# DB env variables
POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_DB = os.getenv("POSTGRES_DB")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")

# Connection string to db
jobstore = {
    'default': SQLAlchemyJobStore(
        url=f'postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}@db:5434/{POSTGRES_DB}'
    )
}

# Send message to the discord channel
async def send_task_message(user_id: int, message: str):
    user = bot.get_user(user_id)
    await user.send(message)
    await plyer.notification(
        title="Task",
        message=message,
        timeout=5 # Displaying time
    )


scheduler = AsyncIOScheduler(timezone=TIMEZONE, jobstores=jobstore)

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

GUILD = discord.Object(id=int(GUILD_ID))

@bot.event
async def on_ready():
    print(f"Bot is up as {bot.user}")
    try:
        synced = await bot.tree.sync(guild=GUILD)
        print(f"Synced {len(synced)} commands")
    except Exception as error:
        print(error)

    scheduler.start()

# COMMANDS

# Add new task
@bot.tree.command(
        name="add",
        description="Add a new task. Usage: day_of_week: mon(single)/mon-sun(multpile)",
        guild=GUILD
    )
async def add_task(interaction: discord.Interaction, day_of_week: str, start_time: str, task: str):
    user = interaction.user

    hour, minute = start_time.split(':')
    scheduler.add_job(
        func=send_task_message,
        trigger=CronTrigger(day_of_week=day_of_week, hour=int(hour), minute=int(minute), timezone=TIMEZONE),
        args=(user.id, task),
        name=task
    )
    await interaction.response.send_message("Task added successfully", ephemeral=True)

# List all user's tasks
@bot.tree.command(name="list", description="List all of your scheduled tasks", guild=GUILD)
async def list_tasks(interaction: discord.Interaction):
    user = interaction.user

    jobs = scheduler.get_jobs()
    user_jobs = [job for job in jobs if job.args[0] == user.id]
    
    message = ''
    try:
        for job in user_jobs:
            task = job.name
            message += f'\nID: {job.id} | Start time: {job.next_run_time} | Task: {task}'

        await interaction.response.send_message(content=message, ephemeral=True)
    except Exception as error:
        await interaction.response.send_message(content=error, ephemeral=True)

# Remove user's task
@bot.tree.command(name="remove", description="Remove task by it's id", guild=GUILD)
async def remove_task(interaction: discord.Interaction, job_id: str):
    try:
        scheduler.remove_job(job_id=str(job_id))
        await interaction.response.send_message(f"Task of id:{job_id} has been removed successfully", ephemeral=True)
    except Exception as error:
        await interaction.response.send_message(error, ephemeral=True)

bot.run(BOT_TOKEN)
