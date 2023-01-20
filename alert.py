import discord
from datetime import datetime, timedelta
import asyncio

# Replace with your bot's token
TOKEN = ""

# Replace with the appropriate channel ID
channel_id = ""

bot = discord.Client(intents=discord.Intents.all())

boss_timers = [
    {"name": "คูทุม", "day_of_week": "Monday", "time": "00:30"},
    {"name": "นูเวอร์", "day_of_week": "Tuesday", "time": "00:30"},
    {"name": "คจาคาร์ & โอฟิน", "day_of_week": "Wednesday", "time": "00:30"},
    {"name": "คูทุม", "day_of_week": "Thursday", "time": "00:30"},
    {"name": "นูเวอร์", "day_of_week": "Friday", "time": "00:30"},
    {"name": "คารานด้า", "day_of_week": "Saturday", "time": "00:30"},
    {"name": "คจาคาร์", "day_of_week": "Sunday", "time": "00:30"},
    {"name": "คจาคาร์ & นูเวอร์", "day_of_week": "Monday", "time": "10:00"},
    {"name": "คูทุม & คารานด้า", "day_of_week": "Tuesday", "time": "10:00"},
    {"name": "คูทุม & นูเวอร์", "day_of_week": "Wednesday", "time": "10:00"},
    {"name": "คารานด้า & คจาคาร์", "day_of_week": "Thursday", "time": "10:00"},
    {"name": "คูทุม & คจาคาร์", "day_of_week": "Friday", "time": "10:00"},
    {"name": "คูทุม & คจาคาร์", "day_of_week": "Saturday", "time": "10:00"},
    {"name": "คจาคาร์ & คารานด้า", "day_of_week": "Sunday", "time": "10:00"},
    {"name": "คูทุม & นูเวอร์", "day_of_week": "Monday", "time": "14:00"},
    {"name": "คูทุม & คจาคาร์", "day_of_week": "Tuesday", "time": "14:00"},
    {"name": "คารานด้า & คจาคาร์", "day_of_week": "Wednesday", "time": "14:00"},
    {"name": "คูทุม & นูเวอร์", "day_of_week": "Thursday", "time": "14:00"},
    {"name": "คารานด้า & คจาคาร์", "day_of_week": "Friday", "time": "14:00"},
    {"name": "คารานด้า & นูเวอร์", "day_of_week": "Saturday", "time": "14:00"},
    {"name": "คูทุม & คารานด้า", "day_of_week": "Sunday", "time": "14:00"},
    {"name": "กามอธ", "day_of_week": "Saturday", "time": "15:00"},
    {"name": "เบลล์", "day_of_week": "Sunday", "time": "15:00"},
    {"name": "คจาคาร์ & คารานด้า", "day_of_week": "Monday", "time": "19:00"},
    {"name": "มูลัคคา & กวินท์", "day_of_week": "Tuesday", "time": "19:00"},
    {"name": "คูทุม & นูเวอร์", "day_of_week": "Wednesday", "time": "19:00"},
    {"name": "นูเวอร์ & คารานด้า", "day_of_week": "Thursday", "time": "19:00"},
    {"name": "คูทุม & นูเวอร์", "day_of_week": "Friday", "time": "19:00"},
    {"name": "มูลัคคา & กวินท์", "day_of_week": "Saturday", "time": "19:00"},
    {"name": "คจาคาร์ & คารานด้า", "day_of_week": "Sunday", "time": "19:00"},
    {"name": "โอฟิน", "day_of_week": "Monday", "time": "23:00"},
    {"name": "กามอธ", "day_of_week": "Tuesday", "time": "23:00"},
    {"name": "เบลล์", "day_of_week": "Wednesday", "time": "23:00"},
    {"name": "กามอธ", "day_of_week": "Thursday", "time": "23:00"},
    {"name": "โอฟิน", "day_of_week": "Friday", "time": "23:00"},
    {"name": "คูทุม & นูเวอร์", "day_of_week": "Sunday", "time": "23:00"},
    ]
    
weekday_dict = {
    'Monday': 0,
    'Tuesday': 1,
    'Wednesday': 2,
    'Thursday': 3,
    'Friday': 4,
    'Saturday': 5,
    'Sunday': 6
}

async def alert(boss_name, delay):
    channel_id = 1000000000000004  # Replace with your channel ID
    target_time = datetime.now() + timedelta(seconds=delay)
    thirty_min_alert = target_time - timedelta(minutes=30)
    fifteen_min_alert = target_time - timedelta(minutes=15)
    five_min_alert = target_time - timedelta(minutes=5)
    while datetime.now() < target_time:
        await asyncio.sleep(5)  # wait for 5 seconds before checking again
        if datetime.now() > thirty_min_alert:
            await bot.get_channel(channel_id).send(f"@everyone 30 นาทีบอส {boss_name} กำลังจะเกิด !")
            thirty_min_alert = None
        if datetime.now() > fifteen_min_alert:
            await bot.get_channel(channel_id).send(f"@everyone 15 นาทีบอส {boss_name} กำลังจะเกิด !")
            fifteen_min_alert = None
        if datetime.now() > five_min_alert:
            await bot.get_channel(channel_id).send(f"@everyone 5 นาทีบอส {boss_name} กำลังจะเกิด !")
            five_min_alert = None
            await bot.get_channel(channel_id).send(f"@everyone บอส {boss_name} เกิดแล้ว รีบไปหวดแม่งเลย !")

@bot.event
async def on_ready():
    for timer in boss_timers:
        now = datetime.now()
        time = datetime.strptime(timer["time"], "%H:%M").time()
        target_day = now.replace(hour=time.hour, minute=time.minute, second=0, microsecond=0)
        if datetime.now().weekday() == weekday_dict[timer["day_of_week"]]:
            if now.time() > time:
                target_day += timedelta(days=7)
        else:
            target_day += timedelta(days=(weekday_dict[timer["day_of_week"]] - now.weekday()) % 7)
        delay = (target_day - datetime.now()).total_seconds()
        bot.loop.create_task(alert(timer["name"], delay))

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
            await message.channel.send(f"บอสตัวต่อไป {next_boss} จะเกิดในอีก {hours} ชั่วโมง, {minutes} นาที.")

bot.run(TOKEN)