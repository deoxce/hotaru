import discord
import discord.utils
from discord.ui import Button, View, Modal, InputText, Select
from discord.ext import commands
import config
from logs import logs

class tempvoice(commands.Cog):
    def __init__(self, client):
        self.client: commands.Bot = client
        self.temp_channels = []
        self.current_response: discord.Interaction = None

    @commands.Cog.listener()
    async def on_ready(self):
        interface_embed = discord.Embed(title="tempvoice interface", description="", color=2829617)
        interface_embed.set_image(url="https://cdn.discordapp.com/attachments/1101840195466301460/1107693369158815744/interface.png")

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

        button_rename = Button(label="", custom_id="tempvoice_rename", style=discord.ButtonStyle.blurple, emoji=emoji_rename)
        button_limit = Button(label="", custom_id="tempvoice_limit", style=discord.ButtonStyle.blurple, emoji=emoji_limit)
        button_private = Button(label="", custom_id="tempvoice_private", style=discord.ButtonStyle.blurple, emoji=emoji_private)
        button_visibility = Button(label="", custom_id="tempvoice_visibility", style=discord.ButtonStyle.blurple, emoji=emoji_visibility)
        button_region = Button(label="", custom_id="tempvoice_region", style=discord.ButtonStyle.blurple, emoji=emoji_region)
        button_allow = Button(label="", custom_id="tempvoice_allow", style=discord.ButtonStyle.blurple, emoji=emoji_allow)
        button_forbid = Button(label="", custom_id="tempvoice_forbid", style=discord.ButtonStyle.blurple, emoji=emoji_forbid)
        button_transfer = Button(label="", custom_id="tempvoice_transfer", style=discord.ButtonStyle.blurple, emoji=emoji_transfer)
        button_kick = Button(label="", custom_id="tempvoice_kick", style=discord.ButtonStyle.blurple, emoji=emoji_kick)
        button_delete = Button(label="", custom_id="tempvoice_delete", style=discord.ButtonStyle.blurple, emoji=emoji_delete)

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

        # раскомментить если нету сообщения
        await self.client.get_channel(config.interface_channel).purge(limit=100)
        await self.client.get_channel(config.interface_channel).send(view=interface_view, embed=interface_embed)

        #self.client.add_view(interface_view)

    @commands.Cog.listener()
    async def on_voice_state_update(self, member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
        # Tempvoice creation
        if after.channel != None and after.channel.id == config.tempvoice_channel:
            await self.voice_create(member)
        # Tempvoice deletion
        for channel_owner in self.temp_channels:
            if before.channel != None and before.channel == channel_owner.get("channel") and before.channel.members == []:
                self.temp_channels.remove(channel_owner)
                await self.voice_delete(before.channel)

    async def voice_delete(self, channel: discord.VoiceChannel):
        log_channel = self.client.get_channel(config.voice_log)
        await channel.delete()
        embed:discord.Embed = await logs.log_embed(
            self=self,
            title=f"{self.client.user.name}",
            description=f"<:red:1097244281816748072> tempvoice `#{channel.name}` was deleted",
            user=self.client.user
            )
        await log_channel.send(embed=embed)
    
    async def voice_create(self, member: discord.Member):
        log_channel = self.client.get_channel(config.voice_log)
        role: discord.Role = discord.utils.get(member.guild.roles, id=config.default_role)
        unverified: discord.Role = discord.utils.get(member.guild.roles, id=config.unverified_role)
        create_channel = self.client.get_channel(config.tempvoice_channel)
        temp_channel = await create_channel.category.create_voice_channel(member.name)
        self.temp_channels.append({'channel': temp_channel, 'owner_id': member.id, 'members': []})
        embed:discord.Embed = await logs.log_embed(
            self=self,
            title=f"{self.client.user.name}",
            description=f"<:green:1097244269267402812> tempvoice <#{temp_channel.id}> was created",
            user=self.client.user
            )
        await temp_channel.set_permissions(member, connect=True)
        await temp_channel.set_permissions(role, connect=True, view_channel=True)
        await temp_channel.set_permissions(unverified, view_channel=False)
        await log_channel.send(embed=embed)
        await member.move_to(temp_channel)

    def permission_check(func):
        async def wrapper(self, ctx: discord.Interaction):
            for channel_owner in self.temp_channels:
                if channel_owner.get("owner_id") == ctx.user.id:
                    await func(self, ctx, channel_owner)
                    return wrapper
            if self.current_response and ctx.user.id == self.current_response.user.id: await self.current_response.delete_original_response()
            self.current_response = await ctx.response.send_message("you do not have permission", ephemeral=True)
        return wrapper

    @permission_check
    async def rename(self, ctx: discord.Interaction, channel_owner):
        rename_modal = Modal(title="Rename")
        rename_modal.add_item(InputText(label="Enter new channel name", max_length=100))
        async def callback(interaction: discord.Interaction):
            channel: discord.VoiceChannel = channel_owner.get("channel")
            await channel.edit(name=rename_modal.children[0].value)
            if self.current_response and ctx.user.id == self.current_response.user.id: await self.current_response.delete_original_response()
            self.current_response = await interaction.response.send_message(content="name changed", ephemeral=True)
        rename_modal.callback = callback
        await ctx.response.send_modal(rename_modal)

    @permission_check
    async def limit(self, ctx: discord.Interaction, channel_owner):
        limit_modal = Modal(title="Limit")
        limit_modal.add_item(InputText(
            label="Enter new limit for your channel", 
            placeholder="Leave blank to reset limit",
            required=False,
            max_length=2
            ))
        async def callback(interaction: discord.Interaction):
            value = limit_modal.children[0].value
            channel: discord.VoiceChannel = channel_owner.get("channel")
            if value != "" and value.isnumeric():
                await channel.edit(user_limit=limit_modal.children[0].value)
            else:
                await channel.edit(user_limit=0)
            if self.current_response and ctx.user.id == self.current_response.user.id: await self.current_response.delete_original_response()
            self.current_response = await interaction.response.send_message(content="limit changed", ephemeral=True)
        limit_modal.callback = callback
        await ctx.response.send_modal(limit_modal)

    @permission_check
    async def private(self, ctx: discord.Interaction, channel_owner):
        channel: discord.VoiceChannel = channel_owner.get("channel")
        role: discord.Role = discord.utils.get(ctx.guild.roles, id=config.default_role)
        permissions: discord.Permissions = channel.permissions_for(role)
        if channel.permissions_for(role).connect == True:
            await channel.set_permissions(role, connect=False, view_channel=permissions.view_channel)
        elif channel.permissions_for(role).connect == False:
            await channel.set_permissions(role, connect=True, view_channel=permissions.view_channel)
        if self.current_response and ctx.user.id == self.current_response.user.id: await self.current_response.delete_original_response()
        self.current_response = await ctx.response.send_message(content="privacy changed", ephemeral=True)

    @permission_check
    async def visibility(self, ctx: discord.Interaction, channel_owner):
        channel: discord.VoiceChannel = channel_owner.get("channel")
        role: discord.Role = discord.utils.get(ctx.guild.roles, id=config.default_role)
        permissions: discord.Permissions = channel.permissions_for(role)
        if channel.permissions_for(role).view_channel == True:
            await channel.set_permissions(role, view_channel=False, connect=permissions.connect)
        elif channel.permissions_for(role).view_channel == False:
            await channel.set_permissions(role, view_channel=True, connect=permissions.connect)
        if self.current_response and ctx.user.id == self.current_response.user.id: await self.current_response.delete_original_response()
        self.current_response = await ctx.response.send_message(content="visibility changed", ephemeral=True)

    @permission_check
    async def region(self, ctx: discord.Interaction, channel_owner):
        options = [
            discord.SelectOption(label="automatic", value="0"),
            discord.SelectOption(label="brazil", value="1"),
            discord.SelectOption(label="hong kong", value="2"),
            discord.SelectOption(label="india", value="3"),
            discord.SelectOption(label="japan", value="4"),
            discord.SelectOption(label="rotterdam", value="5"),
            discord.SelectOption(label="russia", value="6"),
            discord.SelectOption(label="singapore", value="7"),
            discord.SelectOption(label="south africa", value="8"),
            discord.SelectOption(label="sydney", value="9"),
            discord.SelectOption(label="us central", value="10"),
            discord.SelectOption(label="us east", value="11"),
            discord.SelectOption(label="us south", value="12"),
            discord.SelectOption(label="us west", value="13")
            ]
        select = Select(placeholder="select an option", options=options)
        async def callback(interaction: discord.Interaction):
            selected = interaction.data["values"][0]
            channel: discord.VoiceChannel = channel_owner.get("channel")
            if selected == "0": await channel.edit(rtc_region=None)
            if selected == "1": await channel.edit(rtc_region="brazil")
            if selected == "2": await channel.edit(rtc_region="hongkong")
            if selected == "3": await channel.edit(rtc_region="india")
            if selected == "4": await channel.edit(rtc_region="japan")
            if selected == "5": await channel.edit(rtc_region="rotterdam")
            if selected == "6": await channel.edit(rtc_region="russia")
            if selected == "7": await channel.edit(rtc_region="singapore")
            if selected == "8": await channel.edit(rtc_region="southafrica")
            if selected == "9": await channel.edit(rtc_region="sydney")
            if selected == "10": await channel.edit(rtc_region="us-central")
            if selected == "11": await channel.edit(rtc_region="us-east")
            if selected == "12": await channel.edit(rtc_region="us-south")
            if selected == "13": await channel.edit(rtc_region="us-west")
            if self.current_response and ctx.user.id == self.current_response.user.id: await self.current_response.delete_original_response()
            self.current_response = await interaction.response.send_message(content="region changed", ephemeral=True)
        select.callback = callback
        view = View()
        view.add_item(select)
        if self.current_response and ctx.user.id == self.current_response.user.id: await self.current_response.delete_original_response()
        self.current_response = await ctx.response.send_message("choose a region:", view=view, ephemeral=True)

    @permission_check
    async def allow(self, ctx: discord.Interaction, channel_owner):
        channel: discord.VoiceChannel = channel_owner.get("channel")
        options = []
        for member in ctx.guild.members:
            if channel.permissions_for(member).connect == False or channel.permissions_for(member).view_channel == False:
                options.append(discord.SelectOption(
                    label=await self.get_name(member),
                    description=f"{member.name}#{member.discriminator}",
                    #emoji=await self.get_avatar(member),
                    value=str(member.id)))
        
        if (len(options) < 1):
            if self.current_response and ctx.user.id == self.current_response.user.id: await self.current_response.delete_original_response()
            self.current_response = await ctx.response.send_message("all users have access already", ephemeral=True)
            return
        
        select = Select(placeholder="selected users will have access to channel", options=options, min_values=1, max_values=len(options))
        async def callback(interaction: discord.Interaction):
            for user_id in interaction.data["values"]:
                await channel.set_permissions(ctx.guild.get_member(int(user_id)), connect=True, view_channel=True)
            if self.current_response and ctx.user.id == self.current_response.user.id: await self.current_response.delete_original_response()
            self.current_response = await interaction.response.send_message("access granted", ephemeral=True)
        select.callback = callback
        view = View()
        view.add_item(select)
        if self.current_response and ctx.user.id == self.current_response.user.id: await self.current_response.delete_original_response()
        self.current_response = await ctx.response.send_message("select users:", view=view, ephemeral=True)

    @permission_check
    async def forbid(self, ctx: discord.Interaction, channel_owner):
        channel: discord.VoiceChannel = channel_owner.get("channel")
        options = []
        for member in ctx.guild.members:
            if channel.permissions_for(member).connect == True or channel.permissions_for(member).view_channel == True:
                options.append(discord.SelectOption(
                    label=await self.get_name(member),
                    description=f"{member.name}#{member.discriminator}",
                    #emoji=await self.get_avatar(member),
                    value=str(member.id)))
        
        if (len(options) < 1):
            if self.current_response and ctx.user.id == self.current_response.user.id: await self.current_response.delete_original_response()
            self.current_response = await ctx.response.send_message("all users does not have access already", ephemeral=True)
            return
        
        select = Select(placeholder="selected users will not have access to channel", options=options, min_values=1, max_values=len(options))
        async def callback(interaction: discord.Interaction):
            for user_id in interaction.data["values"]:
                await channel.set_permissions(ctx.guild.get_member(int(user_id)), connect=False, view_channel=False)
            if self.current_response and ctx.user.id == self.current_response.user.id: await self.current_response.delete_original_response()
            self.current_response = await interaction.response.send_message("access reverted", ephemeral=True)
        select.callback = callback
        view = View()
        view.add_item(select)
        if self.current_response and ctx.user.id == self.current_response.user.id: await self.current_response.delete_original_response()
        self.current_response = await ctx.response.send_message("select users:", view=view, ephemeral=True)

    @permission_check
    async def transfer(self, ctx: discord.Interaction, channel_owner):
        options = []
        for member in ctx.guild.members:
            options.append(discord.SelectOption(
                label=await self.get_name(member),
                description=f"{member.name}#{member.discriminator}",
                #emoji=await self.get_avatar(member),
                value=str(member.id)))
        select = Select(placeholder="channel will be tranfered to selected user", options=options)
        async def callback(interaction: discord.Interaction):
            self.temp_channels.remove(channel_owner)
            channel_owner.update({"owner_id": int(interaction.data["values"][0])})
            self.temp_channels.append(channel_owner)
            if self.current_response and ctx.user.id == self.current_response.user.id: await self.current_response.delete_original_response()
            self.current_response = await interaction.response.send_message("channel transfered", ephemeral=True)
        select.callback = callback
        view = View()
        view.add_item(select)
        if self.current_response and ctx.user.id == self.current_response.user.id: await self.current_response.delete_original_response()
        self.current_response = await ctx.response.send_message("select user:", view=view, ephemeral=True)
            
    @permission_check
    async def kick(self, ctx: discord.Interaction, channel_owner):
        channel: discord.VoiceChannel = channel_owner.get("channel")
        options = []
        for member in channel.members:
            options.append(discord.SelectOption(
                label=await self.get_name(member),
                description=f"{member.name}#{member.discriminator}",
                #emoji=await self.get_avatar(member),
                value=str(member.id)))
        select = Select(placeholder="selected users will be kicked", options=options, min_values=1, max_values=len(options))
        async def callback(interaction: discord.Interaction):
            for user_id in interaction.data["values"]:
                member: discord.Member = ctx.guild.get_member(int(user_id))
                await member.move_to(None)
            if self.current_response and ctx.user.id == self.current_response.user.id: await self.current_response.delete_original_response()
            self.current_response = await interaction.response.send_message("users kicked", ephemeral=True)
        select.callback = callback
        view = View()
        view.add_item(select)
        if self.current_response and ctx.user.id == self.current_response.user.id: await self.current_response.delete_original_response()
        self.current_response = await ctx.response.send_message("select users:", view=view, ephemeral=True)
                
    @permission_check
    async def delete(self, ctx: discord.Interaction, channel_owner):
        self.temp_channels.remove(channel_owner)
        await self.voice_delete(channel_owner.get("channel"))
        if self.current_response and ctx.user.id == self.current_response.user.id: await self.current_response.delete_original_response()
        self.current_response = await ctx.response.send_message(content="channel deleted", ephemeral=True)

    async def get_name(self, member: discord.Member):
        if member.nick == None:
            name = member.name
        else:
            name = member.nick
        return name

    async def get_avatar(self, user: discord.User):
        if user.avatar == None:
            avatar = user.default_avatar.url
        else:
            avatar = user.avatar.url
        return avatar