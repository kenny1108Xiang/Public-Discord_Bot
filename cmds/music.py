import discord
from discord.ext import commands
import asyncio
import yt_dlp


class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.ytdl = yt_dlp.YoutubeDL({"format": "bestaudio/best"})
        self.voice_clients = {}

        self.ffmpeg_options = {"options": "-vn"}

    @commands.command()
    async def play(self, ctx, *, url):
        voice_channel = ctx.author.voice.channel
        if not voice_channel or voice_channel == None:
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

            player = discord.FFmpegPCMAudio(song_url, **self.ffmpeg_options, executable="../ffmpeg/bin/ffmpeg.exe", pipe=False)

            voice_client.play(player)

            while voice_client.is_playing():
                await asyncio.sleep(1)

            await voice_client.disconnect()
            del self.voice_clients[ctx.guild.id]

        except Exception as e:
            await ctx.send(f"錯誤:  {e}")
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

async def setup(bot):
    await bot.add_cog(Music(bot))
