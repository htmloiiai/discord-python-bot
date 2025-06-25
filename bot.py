import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

load_dotenv()  # 載入 .env 檔案裡的環境變數

TOKEN = os.getenv("DISCORD_TOKEN")  # 從環境變數取出 Token

intents = discord.Intents.default()
intents.message_content = True

class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        # 自動載入 cogs/ 資料夾中所有模組
        for filename in os.listdir("./cogs"):
            if filename.endswith(".py") and not filename.startswith("_"):
                module = f"cogs.{filename[:-3]}"
                try:
                    await self.load_extension(module)
                    print(f"📦 已載入模組：{module}")
                except Exception as e:
                    print(f"❌ 載入模組失敗：{module}，錯誤：{e}")

        # Slash 指令同步
        synced = await self.tree.sync()
        print(f"🔁 Slash 指令同步完成，共 {len(synced)} 個指令")

bot = MyBot()

@bot.event
async def on_ready():
    print(f"✅ Bot 登入為 {bot.user}")

bot.run(TOKEN)
