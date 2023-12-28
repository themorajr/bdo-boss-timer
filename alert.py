import discord
import schedule
from typing import List, Dict, Union
import logging
from dict import *
from prettytable import PrettyTable
from datetime import datetime, timedelta
import asyncio

# Replace with your bot's token
TOKEN = ""

# Replace with the appropriate channel ID
channel_id = ""

bot = discord.Client(intents=discord.Intents.all())
logger = logging.getLogger(__name__)

async def send_embed(channel, title, description):
    embed = discord.Embed(title=title, description=description, color=0x00ff00)
    await channel.send(embed=embed)

async def alert(boss_name: str, target_time: datetime, channel_id: int) -> None:
    messages = [f"@everyone 3 minutes left before {boss_name} spawns!",
                f"@everyone 2 minutes left before {boss_name} spawns!",
                f"@everyone 1 minute left before {boss_name} spawns!",
                f"@everyone {boss_name} has spawned!"]

    message_times = [target_time - timedelta(minutes=3),
                     target_time - timedelta(minutes=2),
                     target_time - timedelta(minutes=1),
                     target_time]

    for i, message_time in enumerate(message_times):
        await asyncio.sleep((message_time - datetime.now()).total_seconds())
        try:
            channel = bot.get_channel(channel_id)
            if channel is None:
                logger.error(f'Error: Could not find channel with ID {channel_id}')
                return
            await channel.send(messages[i])
        except discord.errors.Forbidden as e:
            logger.error(f"Error occurred: {e}")
            return

async def show_table(channel):
    table = PrettyTable()
    table.field_names = ["Boss Name", "Day of Week", "Time"]
    for boss in boss_timers:
        table.add_row([boss["name"], boss["day_of_week"], boss["time"]])

    await send_embed(channel, "Boss Timers", f"```{table.get_string()}```")

async def show_today_table(channel):
    today_weekday = datetime.now().strftime("%A")
    now = datetime.now()
    table = PrettyTable()
    table.field_names = ["Boss Name", "Time"]
    next_boss = None
    next_time = None

    for timer in boss_timers:
        time = datetime.strptime(timer["time"], "%H:%M").time()
        if timer['day_of_week'] == today_weekday:
            table.add_row([timer["name"], timer["time"]])
            target_day = now.replace(hour=time.hour, minute=time.minute, second=0, microsecond=0)
            target_day += timedelta(days=(timer["day_of_week"] - now.weekday() + 7) % 7)
            if now.time() > time:
                target_day += timedelta(days=7)
            if next_time is None or target_day < next_time:
                next_boss = timer["name"]
                next_time = target_day

    if next_boss is None:
        await send_embed(channel, "Boss Timers", "No upcoming boss spawns.")
    else:
        time_until = next_time - now
        hours, remainder = divmod(int(time_until.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        await send_embed(channel, "Boss Timers", f"```{table.get_string()}```\n\nบอสตัวต่อไป ```{next_boss}``` จะเกิดในอีก {hours} ชั่วโมง, {minutes} นาที.")

@bot.event
async def on_ready():
    await asyncio.gather(*[alert(timer["name"], target_time, channel.id) for timer in boss_timers
                           if (target_time := calculate_target_time(timer)) > datetime.now() and
                           (channel := discord.utils.get(bot.guilds[0].channels, name='boss-alert'))])

def calculate_target_time(timer):
    now = datetime.now()
    time = datetime.strptime(timer["time"], "%H:%M").time()
    target_day = now.replace(hour=time.hour, minute=time.minute, second=0, microsecond=0)
    target_day += timedelta(days=(timer["day_of_week"] - now.weekday() + 7) % 7) if timer["day_of_week"] != now.weekday() else timedelta(days=7)
    if now.time() > time:
        target_day += timedelta(days=7)
    return target_day

@bot.event
async def on_message(message):
    if message.content.startswith("!next"):
        now = datetime.now()
        next_boss = None
        next_time = None

        for timer in boss_timers:
            target_time = calculate_target_time(timer)
            if next_time is None or target_time < next_time:
                next_boss = timer["name"]
                next_time = target_time

        if next_boss is None:
            await send_embed(message.channel, "Boss Timers", "No upcoming boss spawns.")
        else:
            time_until = next_time - now
            hours, remainder = divmod(int(time_until.total_seconds()), 3600)
            minutes, seconds = divmod(remainder, 60)
            await send_embed(message.channel, "Next Boss", f"บอสตัวต่อไป ```{next_boss}``` จะเกิดในอีก {hours} ชั่วโมง, {minutes} นาที.")
    elif message.content.startswith("!table"):
        await show_table(message.channel)
    elif message.content.startswith("!today"):
        await show_today_table(message.channel)

bot.run(TOKEN)
