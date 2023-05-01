import discord
import discord.utils
from discord.ui import Button, View
from discord.ext import commands
import config
from logs import logs

class tempvoice(commands.Cog):
    def __init__(self, client):
        self.client: commands.Bot = client
        self.temp_channels = []

    @commands.Cog.listener()
    async def on_ready(self):
        interface_embed = discord.Embed(title="tempvoice interface", description="", color=2829617)
        interface_embed.set_image(url="https://media.discordapp.net/attachments/1101840195466301460/1101858557168734218/interface.png")

        emoji_rename = discord.PartialEmoji(name="rename", animated=False, id=1101840047549984779)
        emoji_limit = discord.PartialEmoji(name="limit", animated=False, id=1101840054764183592)
        emoji_private = discord.PartialEmoji(name="private", animated=False, id=1101840061030477926)
        emoji_region = discord.PartialEmoji(name="region", animated=False, id=1101840066990583880)
        emoji_delete = discord.PartialEmoji(name="delete", animated=False, id=1101839965798793227)

        interface_view = View(timeout=None)

        button_rename = Button(label="", style=discord.ButtonStyle.blurple, emoji=emoji_rename)
        button_limit = Button(label="", style=discord.ButtonStyle.blurple, emoji=emoji_limit)
        button_private = Button(label="", style=discord.ButtonStyle.blurple, emoji=emoji_private)
        button_region = Button(label="", style=discord.ButtonStyle.blurple, emoji=emoji_region)
        button_delete = Button(label="", style=discord.ButtonStyle.blurple, emoji=emoji_delete)

        button_rename.callback = tempvoice.rename
        button_limit.callback = tempvoice.limit
        button_private.callback = tempvoice.private
        button_region.callback = tempvoice.region
        button_delete.callback = tempvoice.delete

        interface_view.add_item(button_rename)
        interface_view.add_item(button_limit)
        interface_view.add_item(button_private)
        interface_view.add_item(button_region)
        interface_view.add_item(button_delete)

        await self.client.get_channel(config.interface_channel).purge(limit=100)
        await self.client.get_channel(config.interface_channel).send(view=interface_view, embed=interface_embed)

    @commands.Cog.listener()
    async def on_voice_state_update(self, member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
        log_channel = self.client.get_channel(config.voice_log)
        # Tempvoice creation
        if after.channel != None and after.channel.id == config.tempvoice_channel:
            await tempvoice.voice_create(self, member)
        # Tempvoice deletion
        if before.channel != None and before.channel in self.temp_channels and before.channel.members == []:
            await before.channel.delete()
            embed:discord.Embed = await logs.log_embed(
                title=f"{self.client.user.name}",
                description=f"<:red:1097244281816748072> tempvoice `#{before.channel.name}` was deleted",
                user=self.client.user
                )
            await log_channel.send(embed=embed)

    async def voice_create(self, member: discord.Member):
        log_channel = self.client.get_channel(config.voice_log)
        create_channel = self.client.get_channel(config.tempvoice_channel)
        temp_channel = await create_channel.category.create_voice_channel(member.name)
        self.temp_channels.append(temp_channel)
        embed:discord.Embed = await logs.log_embed(
            title=f"{self.client.user.name}",
            description=f"<:green:1097244269267402812> tempvoice <#{temp_channel.id}> was created",
            user=self.client.user
            )
        await log_channel.send(embed=embed)
        await member.move_to(temp_channel)

    async def rename():
        pass

    async def limit():
        pass

    async def private():
        pass

    async def region():
        pass

    async def delete():
        pass