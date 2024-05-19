import discord
from discord.ext import commands

class main(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
    
    @commands.command()
    async def ping(self, ctx):
        await ctx.send(f"大約為:'{round(self.bot.latency * 1000)}' (ms)")

    @commands.command()
    async def game1(self, ctx, *args):
        #猜數字遊戲
        if len(args) < 2:
            await ctx.send("請至少提供兩個數字")
            return
        try :
            min_value = int(args[0])
            max_value = int(args[1])
            if min_value >= max_value:
                await ctx.send("第一個參數必須小於第二個參數")
                return
            elif max_value > 2500000 or min_value > 2500000:
                await ctx.send("輸入的數值太大")
                return
        except ValueError:
            await ctx.send("參數必須是整數!")
            return
        
        count = 1
        if len(args) > 2:
            try:
                count = int(args[2])
            except ValueError:
                await ctx.send("抽取數字個數必須是整數")
                return
        
        if count <= 0 or count > (max_value - min_value + 1):
            await ctx.send(f"抽取數字個數必須大於0且不超過{max_value - min_value + 1}個")
            return
        
        import random
        import time

        current_time = int(time.time())
        random.seed(current_time)

        random_numbers = random.sample(range(min_value, max_value + 1), count)
        result_message = ", ".join(str(num) for num in random_numbers)
        await ctx.send(f"隨機抽取的數字為：[{result_message}]")

    @commands.command()
    async def game2(self, ctx, *args):
        if len(args) != 3:
            await ctx.send("請輸入三個參數")
            return

        try:
            min_value = int(args[0])
            max_value = int(args[1])
            count = int(args[2])

            if min_value < 0 or max_value <= 0 or count <= 0:
                raise ValueError
        except ValueError:
            await ctx.send("請輸入正整數")

        if count > (max_value - min_value + 1):
            await ctx.send(f"猜測次數必須不超過{max_value - min_value + 1}次")
            return

        import random
        import time


        current_time = int(time.time())
        random.seed(current_time) #隨機亂數
        secret_number = random.randint(min_value, max_value)

        await ctx.send(f"猜{min_value}~{max_value}之間的數字！你有{count}次機會。")

        import asyncio
        for _ in range(count):
            try:
                guess_msg = await self.bot.wait_for('message', check=lambda m: m.author == ctx.author and m.content.isdigit(), timeout=15.0)
                guess = int(guess_msg.content)

                if guess == secret_number:
                    await ctx.send(f"恭喜你猜對了！ 正確答案為:[{secret_number}]")
                    break
                elif guess < secret_number:
                    await ctx.send(f"猜的數字太小了，再試試！ 剩餘次數{count - (_ + 1)}")
                else:
                    await ctx.send(f"猜的數字太大了，再試試！ 剩餘次數{count - (_ + 1)}")
            except asyncio.TimeoutError:
                await ctx.send("時間已過，遊戲結束！")
                break
        if _ == count - 1 and guess != secret_number:   
            await ctx.send(f"遊戲結束！正確答案是 {secret_number}。")
    
    @commands.command()
    async def say(self, ctx, *, message):
        await ctx.message.delete()
        await ctx.send(message)

    @commands.command()
    async def clear(self, ctx, num):
        try:
            num = int(num)
            if num <= 0:
                await ctx.send("參數須為正整數")
                return

            await ctx.channel.purge(limit=num + 1)
            await ctx.send(f"已清除 {num} 條訊息，此訊息五秒後刪除", delete_after=5)  # 回覆已清除的訊息，5秒後刪除
        except ValueError:
            await ctx.send("參數須為正整數")

#註冊類別
async def setup(bot):
    await bot.add_cog(main(bot))