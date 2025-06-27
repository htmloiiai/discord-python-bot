import discord
from discord.ext import commands
from discord import app_commands
from datetime import timedelta

class AdminCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def is_mod():
        async def predicate(interaction: discord.Interaction) -> bool:
            perms = interaction.user.guild_permissions
            return perms.kick_members or perms.ban_members or perms.moderate_members
        return app_commands.check(predicate)

    @app_commands.command(name="kick", description="踢出成員")
    @is_mod()
    @app_commands.describe(member="要踢出的成員", reason="踢出的理由（選填）")
    async def kick(self, interaction: discord.Interaction, member: discord.Member, reason: str = None):
        try:
            await member.kick(reason=reason)
            await interaction.response.send_message(
                f"✅ 已踢出成員：{str(member)} 理由：{reason or '無'}",
                ephemeral=True
            )
        except Exception as e:
            await interaction.response.send_message(f"❌ 踢出失敗：{e}", ephemeral=True)

    @app_commands.command(name="ban", description="封鎖成員")
    @is_mod()
    @app_commands.describe(member="要封鎖的成員", reason="封鎖理由（選填）")
    async def ban(self, interaction: discord.Interaction, member: discord.Member, reason: str = None):
        try:
            await member.ban(reason=reason)
            await interaction.response.send_message(
                f"✅ 已封鎖成員：{str(member)} 理由：{reason or '無'}",
                ephemeral=True
            )
        except Exception as e:
            await interaction.response.send_message(f"❌ 封鎖失敗：{e}", ephemeral=True)

    @app_commands.command(name="unban", description="解除封鎖成員")
    @is_mod()
    @app_commands.describe(user="要解除封鎖的使用者 (輸入名稱#1234)")
    async def unban(self, interaction: discord.Interaction, user: str):
        guild = interaction.guild
        banned_users = await guild.bans()
        try:
            name, discriminator = user.split('#')
        except ValueError:
            await interaction.response.send_message("❌ 請使用 正確的名稱#數字 格式", ephemeral=True)
            return

        for ban_entry in banned_users:
            user_obj = ban_entry.user
            if (user_obj.name, user_obj.discriminator) == (name, discriminator):
                try:
                    await guild.unban(user_obj)
                    await interaction.response.send_message(f"✅ 已解除封鎖：{user}", ephemeral=True)
                    return
                except Exception as e:
                    await interaction.response.send_message(f"❌ 解除封鎖失敗：{e}", ephemeral=True)
                    return
        await interaction.response.send_message(f"❌ 找不到被封鎖的使用者：{user}", ephemeral=True)

    @app_commands.command(name="timeout", description="禁言成員（指定時間）")
    @is_mod()
    @app_commands.describe(member="要禁言的成員", duration_minutes="禁言時間（分鐘）")
    async def timeout(self, interaction: discord.Interaction, member: discord.Member, duration_minutes: int):
        try:
            duration = timedelta(minutes=duration_minutes)
            await member.edit(timed_out_until=discord.utils.utcnow() + duration)
            await interaction.response.send_message(
                f"✅ 成員 {str(member)} 已禁言 {duration_minutes} 分鐘", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ 禁言失敗：{e}", ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(AdminCommands(bot))
