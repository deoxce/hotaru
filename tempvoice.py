import discord
import discord.utils
from discord.ui import Button, View, Modal, InputText
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
        interface_embed.set_image(url="https://media.discordapp.net/attachments/1101840195466301460/1105105018174062672/interface.png")

        emoji_rename = discord.PartialEmoji(name="rename", animated=False, id=1101840047549984779)
        emoji_limit = discord.PartialEmoji(name="limit", animated=False, id=1101840054764183592)
        emoji_private = discord.PartialEmoji(name="private", animated=False, id=1101840061030477926)
        emoji_visibility = discord.PartialEmoji(name="visibility", animated=False, id=1105095004738822224)
        emoji_region = discord.PartialEmoji(name="region", animated=False, id=1101840066990583880)
        emoji_allow = discord.PartialEmoji(name="allow", animated=False, id=1105095038402297968)
        emoji_forbid = discord.PartialEmoji(name="forbid", animated=False, id=1105095059289944185)
        emoji_transfer = discord.PartialEmoji(name="transfer", animated=False, id=1105103753687871623)
        emoji_kick = discord.PartialEmoji(name="kick", animated=False, id=1105103727112757269)
        emoji_delete = discord.PartialEmoji(name="delete", animated=False, id=1101839965798793227)

        interface_view = View(timeout=None)

        button_rename = Button(label="", style=discord.ButtonStyle.blurple, emoji=emoji_rename)
        button_limit = Button(label="", style=discord.ButtonStyle.blurple, emoji=emoji_limit)
        button_private = Button(label="", style=discord.ButtonStyle.blurple, emoji=emoji_private)
        button_visibility = Button(label="", style=discord.ButtonStyle.blurple, emoji=emoji_visibility)
        button_region = Button(label="", style=discord.ButtonStyle.blurple, emoji=emoji_region)
        button_allow = Button(label="", style=discord.ButtonStyle.blurple, emoji=emoji_allow)
        button_forbid = Button(label="", style=discord.ButtonStyle.blurple, emoji=emoji_forbid)
        button_transfer = Button(label="", style=discord.ButtonStyle.blurple, emoji=emoji_transfer)
        button_kick = Button(label="", style=discord.ButtonStyle.blurple, emoji=emoji_kick)
        button_delete = Button(label="", style=discord.ButtonStyle.blurple, emoji=emoji_delete)

        button_rename.callback = self.rename
        button_limit.callback = self.limit
        button_private.callback = self.private
        button_visibility.callback = self.visibility
        button_region.callback = self.region
        button_allow.callback = self.allow
        button_forbid.callback = self.forbid
        button_transfer.callback = self.transfer
        button_kick.callback = self.kick
        button_delete.callback = self.delete

        interface_view.add_item(button_rename)
        interface_view.add_item(button_limit)
        interface_view.add_item(button_private)
        interface_view.add_item(button_visibility)
        interface_view.add_item(button_region)
        interface_view.add_item(button_allow)
        interface_view.add_item(button_forbid)
        interface_view.add_item(button_transfer)
        interface_view.add_item(button_kick)
        interface_view.add_item(button_delete)

        await self.client.get_channel(config.interface_channel).purge(limit=100)
        await self.client.get_channel(config.interface_channel).send(view=interface_view, embed=interface_embed)

    @commands.Cog.listener()
    async def on_voice_state_update(self, member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
        log_channel = self.client.get_channel(config.voice_log)
        # Tempvoice creation
        if after.channel != None and after.channel.id == config.tempvoice_channel:
            await self.voice_create(member)
        # Tempvoice deletion
        for t in self.temp_channels:
            if before.channel != None and before.channel == t.get("channel") and before.channel.members == []:
                await before.channel.delete()
                embed:discord.Embed = await logs.log_embed(
                    self=self,
                    title=f"{self.client.user.name}",
                    description=f"<:red:1097244281816748072> tempvoice `#{before.channel.name}` was deleted",
                    user=self.client.user
                    )
                await log_channel.send(embed=embed)
                self.temp_channels.remove(t)

    async def voice_create(self, member: discord.Member):
        log_channel = self.client.get_channel(config.voice_log)
        create_channel = self.client.get_channel(config.tempvoice_channel)
        temp_channel = await create_channel.category.create_voice_channel(member.name)
        self.temp_channels.append({'channel': temp_channel, 'owner_id': member.id})
        embed:discord.Embed = await logs.log_embed(
            self=self,
            title=f"{self.client.user.name}",
            description=f"<:green:1097244269267402812> tempvoice <#{temp_channel.id}> was created",
            user=self.client.user
            )
        await log_channel.send(embed=embed)
        await member.move_to(temp_channel)

    async def rename(self, ctx: discord.Interaction):
        rename_modal = Modal(title="Rename")
        rename_modal.add_item(InputText(label="Enter new channel name"))
        async def callback(interaction: discord.Interaction):
            await self.client.get_channel(t.get("channel").id).edit(name=rename_modal.children[0].value)
            await interaction.response.send_message(content="name changed", ephemeral=True)
        rename_modal.callback = callback
        for t in self.temp_channels:
            if t.get("owner_id") == ctx.user.id:
                await ctx.response.send_modal(rename_modal)
                return
        await ctx.response.send_message(content="пошел нахуй", ephemeral=True)

    async def limit():
        pass

    async def private():
        pass

    async def visibility():
        pass

    async def region():
        pass

    async def allow():
        pass

    async def forbid():
        pass

    async def transfer():
        pass

    async def kick():
        pass

    async def delete():
        pass