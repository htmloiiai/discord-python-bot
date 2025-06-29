import discord
from discord.ext import commands
from discord import app_commands

class VoiceControl(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def is_mod():
        async def predicate(interaction: discord.Interaction) -> bool:
            perms = interaction.user.guild_permissions
            return perms.mute_members or perms.move_members
        return app_commands.check(predicate)

    @app_commands.command(name="語音踢出", description="將成員踢出語音頻道")
    @is_mod()
    @app_commands.describe(member="要踢出的成員")
    async def voice_kick(self, interaction: discord.Interaction, member: discord.Member):
        try:
            await member.move_to(None)
            await interaction.response.send_message(f"✅ 已將 {member.display_name} 從語音中踢出", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ 踢出失敗：{e}", ephemeral=True)

    @app_commands.command(name="移動成員", description="將成員移動到指定語音頻道")
    @is_mod()
    @app_commands.describe(member="要移動的成員", channel="目標語音頻道")
    async def move_member(self, interaction: discord.Interaction, member: discord.Member, channel: discord.VoiceChannel):
        try:
            await member.move_to(channel)
            await interaction.response.send_message(f"✅ 已移動 {member.display_name} 到 {channel.name}", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ 移動失敗：{e}", ephemeral=True)

    @app_commands.command(name="語音禁音", description="禁用成員語音")
    @is_mod()
    @app_commands.describe(member="要禁音的成員")
    async def mute(self, interaction: discord.Interaction, member: discord.Member):
        try:
            await member.edit(mute=True)
            await interaction.response.send_message(f"✅ 成員 {member.display_name} 已被禁音", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ 禁音失敗：{e}", ephemeral=True)

    @app_commands.command(name="解除禁音", description="解除成員語音禁用")
    @is_mod()
    @app_commands.describe(member="要解除禁音的成員")
    async def unmute(self, interaction: discord.Interaction, member: discord.Member):
        try:
            await member.edit(mute=False)
            await interaction.response.send_message(f"✅ 成員 {member.display_name} 已解除禁音", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ 解除禁音失敗：{e}", ephemeral=True)

    @app_commands.command(name="拒聽", description="禁止成員聽語音")
    @is_mod()
    @app_commands.describe(member="要拒聽的成員")
    async def deafen(self, interaction: discord.Interaction, member: discord.Member):
        try:
            await member.edit(deafen=True)
            await interaction.response.send_message(f"✅ 成員 {member.display_name} 已被拒聽", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ 拒聽失敗：{e}", ephemeral=True)

    @app_commands.command(name="解除拒聽", description="解除成員拒聽狀態")
    @is_mod()
    @app_commands.describe(member="要解除拒聽的成員")
    async def undeafen(self, interaction: discord.Interaction, member: discord.Member):
        try:
            await member.edit(deafen=False)
            await interaction.response.send_message(f"✅ 成員 {member.display_name} 已解除拒聽", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ 解除拒聽失敗：{e}", ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(VoiceControl(bot))
