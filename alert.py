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

@bot.event
# async def on_ready():
#     channel_id = 1065650881036550234 # hardcoded channel ID
#     for timer in boss_timers:
#         now = datetime.now()
#         time = datetime.strptime(timer["time"], "%H:%M").time()
#         target_day = now.replace(hour=time.hour, minute=time.minute, second=0, microsecond=0)
#         if datetime.now().weekday() == weekday_dict[timer["day_of_week"]]:
#             if now.time() > time:
#                     target_day += timedelta(days=1)
#         else:
#             target_day += timedelta(days=(weekday_dict[timer["day_of_week"]] - now.weekday()) % 7)
#         delay = (target_day - datetime.now()).total_seconds()
#         bot.loop.create_task(alert(timer["name"], delay, channel_id))
#         await asyncio.sleep(1)


# async def alert(boss_name: str, delay: int, channel_id: int) -> None:
#     channel_id = 1065650881036550234 # hardcoded channel ID
#     messages = [f"@everyone 30 minutes left before {boss_name} spawns!",
#                 f"@everyone 15 minutes left before {boss_name} spawns!",
#                 f"@everyone 5 minutes left before {boss_name} spawns!",
#                 f"@everyone {boss_name} has spawned!"]

#     delay = delay - 1800  # starts sending messages 30 minutes before spawn
#     delay_between_messages = [1800, 900, 900, 300]
#     for i in range(len(messages)):
#         await asyncio.sleep(delay)
#         try:
#             await bot.get_channel(channel_id).send(messages[i])
#         except Exception as e:
#             print("Error occured: ", e)
#         delay += delay_between_messages[i]


# async def show_table(channel):
#     table = PrettyTable()
#     table.field_names = ["Boss Name", "Day of Week", "Time"]
#     for boss in boss_timers:
#         table.add_row([boss["name"], boss["day_of_week"], boss["time"]])
#     await channel.send("```"+table.get_string()+"```")

async def on_ready():
    for timer in boss_timers:
        now = datetime.now()
        time = datetime.strptime(timer["time"], "%H:%M").time()
        target_day = datetime.combine(now, time)
        if now.weekday() == weekday_dict[timer["day_of_week"]]:
            if now.time() > time:
                target_day += timedelta(days=1)
        else:
            target_day += timedelta(days=(weekday_dict[timer["day_of_week"]] - now.weekday()) % 7)
        if target_day > now:
            delay = (target_day - datetime.now()).total_seconds()
            channel = discord.utils.get(bot.guilds[0].channels, name='boss-alert')
            if channel:
                bot.loop.create_task(alert(timer["name"], target_day, channel.id))
                await asyncio.sleep(1)
            else:
                print(f'Error: Channel "boss-alert" not found')

async def alert(boss_name: str, target_time: datetime, channel_id: int) -> None:
    messages = [f"@everyone 30 minutes left before {boss_name} spawns!",
                f"@everyone 15 minutes left before {boss_name} spawns!",
                f"@everyone 5 minute left before {boss_name} spawns!",
                f"@everyone {boss_name} has spawned!"]
    message_times = [target_time - timedelta(minutes=30),
                     target_time - timedelta(minutes=15),
                     target_time - timedelta(minutes=5),
                     target_time]
    i = 0
    while True:
        now = datetime.now()
        if now >= message_times[i]:
            try:
                channel = bot.get_channel(channel_id)
                if channel is None:
                    logger.error(f'Error: Could not find channel with ID {channel_id}')
                    return
                await channel.send(messages[i])
                i += 1
                if i >= len(messages):
                    break
            except discord.errors.Forbidden as e:
                logger.error(f"Error occured: {e}")
                return
        await asyncio.sleep(60)


# async def alert(boss_name: str, delay: int, channel_id: int) -> None:
#     messages = [f"@everyone 3 minutes left before {boss_name} spawns!",
#                 f"@everyone 2 minutes left before {boss_name} spawns!",
#                 f"@everyone 1 minute left before {boss_name} spawns!",
#                 f"@everyone {boss_name} has spawned!"]

#     delay = delay - 180  # starts sending messages 3 minutes before spawn
#     for i in range(len(messages) -1):
#         await asyncio.sleep(60 * (3-i))
#         try:
#             channel = bot.get_channel(channel_id)
#             if channel is None:
#                 print(f'Error: Could not find channel with ID {channel_id}')
#                 return
#             await channel.send(messages[i])
#         except Exception as e:
#             print("Error occured: ", e)
#     await asyncio.sleep(delay)
#     try:
#         channel = bot.get_channel(channel_id)
#         if channel is None:
#             print(f'Error: Could not find channel with ID {channel_id}')
#             return
#         await channel.send(messages[-1])
#     except Exception as e:
#         print("Error occured: ", e)

async def show_table(channel):
    table = PrettyTable()
    table.field_names = ["Boss Name", "Day of Week", "Time"]
    for boss in boss_timers:
        table.add_row([boss["name"], boss["day_of_week"], boss["time"]])

    embed = discord.Embed(title="Boss Timers", description=f"```{table.get_string()}```", color=0x00ff00)
    await channel.send(embed=embed)

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
            if now.time() > time:
                target_day += timedelta(days=7)
            if next_time is None or target_day < next_time:
                next_boss = timer["name"]
                next_time = target_day
    if next_boss is None:
        await channel.send("No upcoming boss spawns.")
    else:
        time_until = next_time - datetime.now()
        hours, remainder = divmod(int(time_until.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        await channel.send("```"+table.get_string()+"```")
        await channel.send(f"\nบอสตัวต่อไป ```{next_boss}``` จะเกิดในอีก {hours} ชั่วโมง, {minutes} นาที.")

@bot.event
async def on_message(message):
    if message.content.startswith("!next"):
        now = datetime.now()
        next_boss = None
        next_time = None
        for timer in boss_timers:
            time = datetime.strptime(timer["time"], "%H:%M").time()
            target_day = now.replace(hour=time.hour, minute=time.minute, second=0, microsecond=0)
            if datetime.now().weekday() == weekday_dict[timer["day_of_week"]]:
                if now.time() > time:
                    target_day += timedelta(days=7)
            else:
                target_day += timedelta(days=(weekday_dict[timer["day_of_week"]] - now.weekday()) % 7)
            if next_time is None or target_day < next_time:
                next_boss = timer["name"]
                next_time = target_day
        if next_boss is None:
            await message.channel.send("No upcoming boss spawns.")
        else:
            time_until = next_time - datetime.now()
            hours, remainder = divmod(int(time_until.total_seconds()), 3600)
            minutes, seconds = divmod(remainder, 60)
            await message.channel.send(f"บอสตัวต่อไป ```{next_boss}``` จะเกิดในอีก {hours} ชั่วโมง, {minutes} นาที.")
    if message.content.startswith("!table"):
        await show_table(message.channel)
    if message.content.startswith("!today"):
        await show_today_table(message.channel)

bot.run(TOKEN)
