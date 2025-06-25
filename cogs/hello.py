import discord
from discord.ext import commands
from discord import app_commands
import random
from datetime import datetime

class Hello(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # 傳統指令：!hello
    @commands.command()
    async def hello(self, ctx):
        await ctx.send(f"👋 傳統 hello, {ctx.author.mention}")

    # Slash 指令：/打招呼
    @app_commands.command(name="打招呼", description="跟機器人打個招呼")
    async def greet(self, interaction: discord.Interaction):
        now = datetime.now()
        hour = now.hour
        now_time = now.strftime("%H:%M")

        # 根據時間判斷餐別
        if 5 <= hour < 11:
            meal = "早餐"
        elif 11 <= hour < 17:
            meal = "午餐"
        elif 17 <= hour < 23:
            meal = "晚餐"
        else:
            meal = "宵夜"

        # 隨機選擇一句話
        messages = [
            f"嗨嗨 {interaction.user.mention}，你今天要來做什麼呢？",
            f"嗨嗨 {interaction.user.mention}，現在是 {now_time}，你吃過{meal}了嗎？"
        ]
        response = random.choice(messages)

        await interaction.response.send_message(response)

# 註冊 Cog
async def setup(bot):
    await bot.add_cog(Hello(bot))
