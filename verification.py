import discord
import discord.utils
from discord.ui import Button, View
from discord.ext import commands
import config
import asyncio

class verification(commands.Cog):
    def __init__(self, client):
        self.client: commands.Bot = client
    
    @commands.Cog.listener()
    async def on_ready(self):
        verif_embed = discord.Embed(title="verification", description=f"please use the button below to verify that you are not a robot", color=2829617)

        emoji_verified = discord.PartialEmoji(name="verified", animated=False, id=1105969558692569198)
        verif_view = View(timeout=None)
        button_start = Button(label="verify", style=discord.ButtonStyle.blurple, emoji=emoji_verified)
        button_start.callback = verification.give_role
        verif_view.add_item(button_start)

        await self.client.get_channel(config.verification_channel).purge(limit=100)
        await self.client.get_channel(config.verification_channel).send(view=verif_view, embed=verif_embed)
        print("ready")
    
    async def give_role(ctx: discord.Interaction):
        role = discord.utils.get(ctx.guild.roles, name=config.default_role)
        await ctx.user.add_roles(role)
        await ctx.response.send_message("done", ephemeral=True)
        await asyncio.sleep(5)
        await ctx.delete_original_response()
