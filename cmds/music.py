import discord
from discord.ext import commands
import asyncio
import yt_dlp

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.ytdl = yt_dlp.YoutubeDL({"format": "bestaudio/best"})
        self.voice_clients = {}

        self.ffmpeg_options = {
            "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
            "options": "-vn"
        }
        self.ffmpeg_path = "/usr/bin/ffmpeg"

    @commands.command()
    async def play(self, ctx, *, url):
        voice_channel = ctx.author.voice.channel
        if not voice_channel:
            await ctx.send("請先加入一個語音頻道")
            return

        if ctx.guild.id in self.voice_clients:
            await ctx.send("已經在播音樂了")
            return

        try:
            voice_client = await voice_channel.connect()
            self.voice_clients[ctx.guild.id] = voice_client

            loop = asyncio.get_event_loop()
            data = await loop.run_in_executor(None, lambda: self.ytdl.extract_info(url, download=False))
            song_url = data["url"]

            player = discord.FFmpegPCMAudio(song_url, **self.ffmpeg_options, executable=self.ffmpeg_path)

            def after_playing(error):
                if error:
                    print(f"Player error: {error}")
                asyncio.run_coroutine_threadsafe(self.check_disconnect(ctx.guild.id), self.bot.loop)

            voice_client.play(player, after=after_playing)
            await ctx.send(f"正在播放: {data['title']}")
            await self.bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name=url))

        except discord.errors.ClientException as e:
            await ctx.send(f"連接錯誤: {e}")
            if ctx.guild.id in self.voice_clients:
                await self.voice_clients[ctx.guild.id].disconnect()
                del self.voice_clients[ctx.guild.id]

        except yt_dlp.utils.DownloadError as e:
            await ctx.send(f"下載錯誤: {e}")
            if ctx.guild.id in self.voice_clients:
                await self.voice_clients[ctx.guild.id].disconnect()
                del self.voice_clients[ctx.guild.id]

        except Exception as e:
            await ctx.send(f"錯誤: {e}")
            if ctx.guild.id in self.voice_clients:
                await self.voice_clients[ctx.guild.id].disconnect()
                del self.voice_clients[ctx.guild.id]

    @commands.command()
    async def stop(self, ctx):
        if ctx.guild.id in self.voice_clients:
            voice_client = self.voice_clients[ctx.guild.id]
            if voice_client.is_playing():
                voice_client.stop()
            await voice_client.disconnect()
            del self.voice_clients[ctx.guild.id]
            await ctx.send("停止播放且中斷連線")
            await self.bot.change_presence(activity=None)
        else:
            await ctx.send("目前沒有音樂在播放")

    async def check_disconnect(self, guild_id):
        await asyncio.sleep(5)
        if guild_id in self.voice_clients:
            voice_client = self.voice_clients[guild_id]
            if not voice_client.is_playing():
                await voice_client.disconnect()
                del self.voice_clients[guild_id]
                print(f"離開語音頻道 {guild_id}")

async def setup(bot):
    await bot.add_cog(Music(bot))
