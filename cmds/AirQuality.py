from discord.ext import commands
import requests
from datetime import datetime

url = "https://data.moenv.gov.tw/api/v2/aqx_p_432?api_key=e8dd42e6-9b8b-43f8-991e-b3dee723a52d&limit=1000&sort=ImportDate%20desc&format=JSON"

class AirQuality(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def Air(self, ctx, city: str):
        response = requests.get(url)
        data = response.json()

        filtered_data = [
            {
                "sitename": record["sitename"],
                "status": record["status"],
                "pm2.5": record["pm2.5"],
                "publishtime": datetime.strptime(record["publishtime"], "%Y/%m/%d %H:%M:%S").strftime("%Y/%m/%d %H:%M")
            }
            for record in data["records"]
            if record["county"] == city
        ]

        if filtered_data:
            message = "\n".join(
                f"測站名稱: {item['sitename']}, 狀態: {item['status']}, PM2.5: {item['pm2.5']}, 發布時間: {item['publishtime']}"
                for item in filtered_data
            )
        else:
            message = f"找不到指定的 {city} 縣市。"

        await ctx.send(message)

async def setup(bot):
    await bot.add_cog(AirQuality(bot))
