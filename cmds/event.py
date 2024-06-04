import discord
from discord.ext import commands
import json
import os

class Event(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
            await ctx.send("沒有此指令")

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return
        if message.content == "Hello Bot":
            if isinstance(message.channel, discord.DMChannel):
                await message.author.send("您好，這是我的私人訊息")
            else:
                await message.reply("Hello")
        await self.bot.process_commands(message)
        

    @commands.Cog.listener()
    async def on_member_join(self, member):
        guild = member.guild
        server_name = guild.name
        server_json_path = os.path.join(os.path.dirname(__file__), "..", "server", f"{server_name}.json")
        if os.path.exists(server_json_path):
            with open(server_json_path, 'r') as f:
                data = json.load(f)
                join_channel_id = int(data.get("join_channel_id"))
                if join_channel_id:
                    channel = guild.get_channel(join_channel_id)
                    if channel:
                        await channel.send(f"歡迎 {member.mention} 加入伺服器！")
                        print(f"{member} join")

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        guild = member.guild
        server_name = guild.name
        server_json_path = os.path.join(os.path.dirname(__file__), "..", "server", f"{server_name}.json")
        if os.path.exists(server_json_path):
            with open(server_json_path, 'r') as f:
                data = json.load(f)
                leave_channel_id = int(data.get("leave_channel_id"))
                if leave_channel_id:
                    channel = guild.get_channel(leave_channel_id)
                    if channel:
                        await channel.send(f"{member.mention} 退出伺服器！")
                        print(f"{member} leave")

    async def create_bot_channels(self, guild):
        required_channel_names = ["join", "leave", "music", "bot-message"]
        existing_channels = {channel.name for channel in guild.channels}

        for channel_name in required_channel_names:
            if channel_name not in existing_channels:
                channel = await guild.create_text_channel(channel_name)
                overwrite = None
                if channel_name == "bot-message" or channel_name == "music":
                    overwrite = discord.PermissionOverwrite(send_messages=False, read_messages=True, mention_everyone=False)
                else:
                    overwrite = discord.PermissionOverwrite(send_messages=False)
                
                await channel.set_permissions(guild.default_role, overwrite=overwrite)
                print(f"已創建新頻道: {channel_name}")

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        print(f"機器人首次加入伺服器: {guild.name}")
        # 在機器人首次加入伺服器時檢查並創建所需的頻道
        await self.create_bot_channels(guild)

        # 建立此伺服器的 JSON 設定檔案
        server_folder = os.path.join(os.path.dirname(__file__), "..", "server")
        server_json_path = os.path.join(server_folder, f"{guild.name}.json")

        join_channel_id = await self.get_channel_id(guild, "join")
        leave_channel_id = await self.get_channel_id(guild, "leave")
        bot_message_channel_id = await self.get_channel_id(guild, "bot-message")
        music_channel_id = await self.get_channel_id(guild, "music")

        data = {
            "join_channel_id": str(join_channel_id),
            "leave_channel_id": str(leave_channel_id),
            "bot_message_channel_id": str(bot_message_channel_id),
            "music_channel_id": str(music_channel_id)
        }

        with open(server_json_path, 'w') as f:
            json.dump(data, f, indent=4)
            print(f"已建立 {guild.name} 的 JSON 設定檔")

    async def get_channel_id(self, guild, channel_name):
        channel = discord.utils.get(guild.text_channels, name=channel_name)
        if channel:
            return channel.id
        else:
            return None

async def setup(bot):
    await bot.add_cog(Event(bot))
