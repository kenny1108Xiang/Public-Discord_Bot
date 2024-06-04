import discord
from discord.ext import commands
import json
import asyncio

with open("setting.json", mode='r', encoding="utf8") as jsetting:
    setting = json.load(jsetting)

intents = discord.Intents.all()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='%', intents=intents)

async def setup_bot():
    initial_extensions = ['cmds.main', 'cmds.event', 'cmds.music', 'cmds.weather', 'cmds.AirQuality']
    for extension in initial_extensions:
        try:
            await bot.load_extension(extension)
        except Exception as e:
            print(f"Failed to load extension {extension}: {type(e).__name__} - {e}")

@bot.event
async def on_message(message):
    if message.content.startswith(bot.command_prefix):
        return  # 這是命令，交由 commands 模組處理

@bot.event
async def on_ready():
    await bot.wait_until_ready()
    await bot.change_presence(activity=discord.Game(name="Python😀"))

    channel_id = setting["bot-message"]
    channel = bot.get_channel(channel_id)
    
    if channel:
        await channel.send(f"@everyone 機器人已經啟動!")
        print(f">> 機器人已就緒！目前登入身份為 {bot.user} <<")
    else:
        print(f"找不到指定的頻道，channel_id: {channel_id}")

@bot.command()
async def load(ctx, extension):
    try:
        await bot.load_extension(f"cmds.{extension}")
        await ctx.send(f"Loaded {extension} done.")
    except Exception as e:
        await ctx.send(f"Failed to load extension {extension}: {type(e).__name__} - {e}")

@bot.command()
async def unload(ctx, extension):
    try:
        await bot.unload_extension(f"cmds.{extension}")
        await ctx.send(f"Unloaded {extension} done.")
    except Exception as e:
        await ctx.send(f"Failed to unload extension {extension}: {type(e).__name__} - {e}")

@bot.command()
async def reload(ctx, extension):
    try:
        await bot.reload_extension(f"cmds.{extension}")
        await ctx.send(f"Reloaded {extension} done.")
    except Exception as e:
        await ctx.send(f"Failed to reload extension {extension}: {type(e).__name__} - {e}")

async def cog():
    await setup_bot()

if __name__ == "__main__":
    try:
        asyncio.run(cog())
        bot.run(setting["Token"])
    except Exception as e:
        print(">> 機器人關閉 <<")
        print(f"\n{e}")
