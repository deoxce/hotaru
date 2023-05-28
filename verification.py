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
    async def on_member_join(self, member: discord.Member):
        role = discord.utils.get(member.guild.roles, id=config.unverified_role)
        await member.add_roles(role)

    @commands.slash_command(name="verification_panel")
    async def create_verification(self, ctx:discord.Interaction):
        verif_view, verif_embed = await self.verify_embed()
        await self.client.get_channel(config.verification_channel).purge(limit=100)
        await self.client.get_channel(config.verification_channel).send(view=verif_view, embed=verif_embed)
        await ctx.response.send_message("done", ephemeral=True)
    
    @commands.Cog.listener()
    async def on_ready(self):
        verif_view, verif_embed = await self.verify_embed()
        self.client.add_view(verif_view)
        print("ready")
    
    async def verify_embed(self):
        verif_embed = discord.Embed(title="verification", description=f"please use the button below to verify that you are not a robot", color=2829617)

        emoji_verified = discord.PartialEmoji(name="verified", animated=False, id=1105969558692569198)
        verif_view = View(timeout=None)
        button_start = Button(label="verify", custom_id="verification_button", style=discord.ButtonStyle.blurple, emoji=emoji_verified)
        button_start.callback = self.give_role
        verif_view.add_item(button_start)
        return verif_view, verif_embed

    async def give_role(self, ctx: discord.Interaction):
        unverified_role = discord.utils.get(ctx.guild.roles, id=config.unverified_role)
        verified_role = discord.utils.get(ctx.guild.roles, id=config.default_role)
        await ctx.user.remove_roles(unverified_role)
        await ctx.user.add_roles(verified_role)
        await ctx.response.send_message("done", ephemeral=True)
        await asyncio.sleep(5)
        await ctx.delete_original_response()
