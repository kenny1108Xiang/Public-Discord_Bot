from discord.ext import commands
import requests
import json
from datetime import datetime


with open("setting.json", mode='r', encoding="utf8") as jsetting:
    setting = json.load(jsetting)

weather_url = f"https://opendata.cwa.gov.tw/api/v1/rest/datastore/F-C0032-001?Authorization={setting['Weather_Token']}"

class Weather(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def weather(self, ctx, city: str):
        data = requests.get(weather_url)

        if data.status_code != 200:
            await ctx.send("目前獲取失敗")
            return

        data_json = data.json()

        location_data = None
        for location in data_json['records']['location']:
            if location['locationName'] == city:
                location_data = location
                break

        if not location_data:
            await ctx.send(f"找不到城市 {city} 的天氣訊息。")
            return
        
        weather_elements = location_data['weatherElement']
        periods = {}
        
        for element in weather_elements:
            element_name = element['elementName']
            for time in element['time']:
                start_time = time['startTime']
                end_time = time['endTime']
                period_key = f"{start_time} - {end_time}"
                if period_key not in periods:
                    periods[period_key] = {}
                periods[period_key][element_name] = time['parameter']['parameterName']

        weather_info = f"{city}的天氣預報：\n\n"
        for period, elements in periods.items():
            formatted_period = " - ".join([
                datetime.strptime(time, "%Y-%m-%d %H:%M:%S").strftime("%Y/%m/%d %H:%M") 
                for time in period.split(" - ")
            ])
            weather_info += f"時間段: {formatted_period}\n"
            if 'Wx' in elements:
                weather_info += f"  天氣: {elements['Wx']}\n"
            if 'PoP' in elements:
                weather_info += f"  降雨機率: {elements['PoP']}%\n"
            if 'MinT' in elements:
                weather_info += f"  最低溫度: {elements['MinT']}°C\n"
            if 'CI' in elements:
                weather_info += f"  舒適度: {elements['CI']}\n"
            if 'MaxT' in elements:
                weather_info += f"  最高溫度: {elements['MaxT']}°C\n"
            weather_info += "\n"

        await ctx.send(weather_info)

async def setup(bot):
    await bot.add_cog(Weather(bot))
