import discord
from discord.ext import commands
from discord import app_commands
import random
import datetime
import json
import os
import math

FORTUNE_FILE = "data/user_fortunes.json"

# === 資料載入與儲存 ===
def load_fortunes():
    if os.path.exists(FORTUNE_FILE):
        with open(FORTUNE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_fortunes(data):
    os.makedirs(os.path.dirname(FORTUNE_FILE), exist_ok=True)
    with open(FORTUNE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# === 抽獎視圖 ===
class LotteryView(discord.ui.View):
    def __init__(self, host_id: int, prize: str):
        super().__init__(timeout=None)
        self.participants = set()
        self.host_id = host_id
        self.prize = prize
        self.message = None

    async def update_message(self):
        if self.message:
            embed = discord.Embed(
                title="🎁 抽獎進行中",
                description=f"抽獎品項：`{self.prize}`\n目前共有 {len(self.participants)} 人參加！",
                color=discord.Color.from_rgb(135, 206, 235)
            )
            await self.message.edit(embed=embed, view=self)

    @discord.ui.button(label="參加抽獎", style=discord.ButtonStyle.green, custom_id="join_lottery")
    async def join_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        user = interaction.user
        if user.id in self.participants:
            await interaction.response.send_message(f"{user.mention} 你已經參加過了！", ephemeral=True)
        else:
            self.participants.add(user.id)
            await interaction.response.send_message(f"{user.mention} 已加入抽獎名單！", ephemeral=True)
            await self.update_message()

    @discord.ui.button(label="抽獎", style=discord.ButtonStyle.blurple, custom_id="run_lottery")
    async def draw_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.host_id:
            await interaction.response.send_message("只有抽獎發起者可以按這個按鈕。", ephemeral=True)
            return

        if not self.participants:
            await interaction.response.send_message("目前沒有人參加，無法抽獎！", ephemeral=True)
            return

        winner_id = random.choice(list(self.participants))
        winner = interaction.guild.get_member(winner_id)
        if winner is None:
            await interaction.response.send_message("無法找到得獎者，請再試一次。", ephemeral=True)
            return

        await interaction.response.send_message(f"🎉 恭喜 {winner.mention} 中獎啦！")
        self.participants.clear()
        await self.update_message()

# === 指令功能 ===
class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.EMBED_COLOR = discord.Color.from_rgb(135, 206, 235)
        self.user_fortunes = load_fortunes()

    def save_fortunes_file(self):
        save_fortunes(self.user_fortunes)

    @app_commands.command(name="計算", description="解一個數學式子（支援 sin, sqrt, pi 等）")
    @app_commands.describe(expression="輸入像 sqrt(9)+2 或 sin(pi/2)")
    async def calculate(self, interaction: discord.Interaction, expression: str):
        embed = discord.Embed(title="🧮 計算結果", color=self.EMBED_COLOR)
        try:
            expression = expression.replace("^", "**")
            allowed_names = {k: v for k, v in math.__dict__.items() if not k.startswith("__")}
            allowed_names.update({"abs": abs, "round": round})

            result = eval(expression, {"__builtins__": {}}, allowed_names)

            embed.add_field(name="輸入式子", value=f"`{expression}`", inline=False)
            embed.add_field(name="計算結果", value=f"`{result}`", inline=False)
        except Exception as e:
            embed.title = "❌ 計算錯誤"
            embed.description = (
                "這不是合法的數學式子，或使用了不支援的函數。\n\n"
                "支援函式包括：`sin`, `cos`, `sqrt`, `log`, `pi`, `e`, `abs`, `round` 等"
            )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="擲骰", description="擲出 1~6 的隨機骰子點數")
    @app_commands.describe(times="要擲幾次？最多10次")
    async def dice(self, interaction: discord.Interaction, times: int = 1):
        embed = discord.Embed(title="🎲 擲骰結果", color=self.EMBED_COLOR)
        if 1 <= times <= 10:
            results = [str(random.randint(1, 6)) for _ in range(times)]
            embed.description = "擲出： " + "、".join(results)
        else:
            embed.title = "❌ 錯誤"
            embed.description = "只能擲 1~10 顆骰子"
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="猜數字", description="猜 1 到 100 的數字，看看你猜得準不準！")
    async def guess_number(self, interaction: discord.Interaction):
        answer = random.randint(1, 100)
        embed = discord.Embed(title="❓ 猜數字遊戲", description=f"我心裡想了一個 1~100 的數字，是 `{answer}`！你猜對了嗎？", color=self.EMBED_COLOR)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="占卜", description="隨機抽一個今日運勢（每天只會變一次）")
    async def fortune(self, interaction: discord.Interaction):
        user_id = str(interaction.user.id)
        today_str = datetime.datetime.now().strftime("%Y-%m-%d")
        fortunes = [
            "✨ 大吉：今天非常順利！",
            "😊 中吉：會有不錯的驚喜。",
            "😐 小吉：平凡的一天。",
            "😕 凶：有點小狀況要小心。",
            "💀 大凶：今天適合低調行事。"
        ]

        if user_id in self.user_fortunes and self.user_fortunes[user_id]["date"] == today_str:
            fortune_text = self.user_fortunes[user_id]["fortune"]
        else:
            fortune_text = random.choice(fortunes)
            self.user_fortunes[user_id] = {"date": today_str, "fortune": fortune_text}
            self.save_fortunes_file()

        embed = discord.Embed(title="🔮 今日運勢", description=fortune_text, color=self.EMBED_COLOR)
        embed.set_footer(text=f"{interaction.user.display_name} 的專屬運勢")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="say", description="讓機器人幫你說一句話")
    @app_commands.describe(message="要說的內容")
    async def say(self, interaction: discord.Interaction, message: str):
        embed = discord.Embed(title="🗣️ 我說：", description=message, color=self.EMBED_COLOR)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="時間戳", description="取得現在的 Discord Timestamp 格式")
    async def timestamp(self, interaction: discord.Interaction):
        now = int(datetime.datetime.now().timestamp())
        timestamp_str = f"<t:{now}:F>"
        embed = discord.Embed(title="🕒 Discord Timestamp", color=self.EMBED_COLOR)
        embed.add_field(name="時間預覽", value=timestamp_str, inline=False)
        embed.add_field(name="複製格式", value=f"```{timestamp_str}```", inline=False)
        embed.set_footer(text="貼上到 Discord 時會自動顯示時間")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="開始抽獎", description="發送抽獎按鈕，讓成員點擊參加並抽獎")
    @app_commands.describe(prize="這次抽獎的品項")
    async def start_lottery(self, interaction: discord.Interaction, prize: str):
        view = LotteryView(host_id=interaction.user.id, prize=prize)
        embed = discord.Embed(
            title="🎁 抽獎開始",
            description=f"抽獎品項：`{prize}`\n目前共有 0 人參加！",
            color=self.EMBED_COLOR
        )
        await interaction.response.send_message(embed=embed, view=view)
        sent_message = await interaction.original_response()
        view.message = sent_message

# === 加入 Cog ===
async def setup(bot):
    await bot.add_cog(Utility(bot))
