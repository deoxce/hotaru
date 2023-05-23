import discord
import discord.utils
from discord.ui import Button, View
from discord.ext import commands
import config

class logs(commands.Cog):
    def __init__(self, client):
        self.client: commands.Bot = client
    
    @commands.Cog.listener()
    async def on_voice_state_update(self, member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
        log_channel = self.client.get_channel(config.voice_log)
        if member.guild.id != config.guild_id: return None
        # Joined channel
        if before.channel == None:
            embed:discord.Embed = await self.log_embed(
                title=f"{member.name}#{member.discriminator}",
                description=f"<:green:1097244269267402812> <@{member.id}> entered <#{after.channel.id}>",
                user=member
                )
            await log_channel.send(embed=embed)
        # Moved between channels
        if before.channel != None and after.channel != None and before.channel!=after.channel:
            embed:discord.Embed = await self.log_embed(
                title=f"{member.name}#{member.discriminator}",
                description=f"<:blue:1097244258043445309> <@{member.id}> moved from <#{before.channel.id}> to <#{after.channel.id}>",
                user=member
            )
            await log_channel.send(embed=embed)
        # Left channel
        if after.channel == None:
            embed:discord.Embed = await self.log_embed(
                title=f"{member.name}#{member.discriminator}",
                description=f"<:red:1097244281816748072> <@{member.id}> left <#{before.channel.id}>",
                user=member
            )
            await log_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_ban(self, guild: discord.Guild, user: discord.User):
        if guild.id != config.guild_id: return None
        channel = self.client.get_channel(config.ban_log)
        embed:discord.Embed = await self.log_embed(
            title=f"{user.name}#{user.discriminator}",
            description=f"<:red:1097244281816748072> <@{user.id}> was banned",
            user=user
        )
        await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_unban(self, guild: discord.Guild, user: discord.User):
        if guild.id != config.guild_id: return None
        channel = self.client.get_channel(config.ban_log)
        embed:discord.Embed = await self.log_embed(
            title=f"{user.name}#{user.discriminator}",
            description=f"<:green:1097244269267402812> <@{user.id}> was unbanned",
            user=user
        )
        await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_message_edit(self, before: discord.Message, after: discord.Message):
        if before.author == self.client.user: return None
        if before.guild.id != config.guild_id: return None
        channel = self.client.get_channel(config.message_log)
        if before.content == after.content and len(after.attachments) < len(before.attachments):
            embed:discord.Embed = await self.log_embed(
                title=f"{before.author.name}#{before.author.discriminator}",
                description=f"<:red:1097244281816748072> <@{before.author.id}> removed attachment from {before.jump_url}\n",
                user=before.author
            )
            files = [item for item in before.attachments if item not in after.attachments]
            log = await channel.send(embed=embed)
            await log.reply(files=await self.get_attachments(files))
        elif before.content != after.content:
            embed:discord.Embed = await self.log_embed(
                title=f"{before.author.name}#{before.author.discriminator}",
                description=f"<:blue:1097244258043445309> **<@{before.author.id}> edited message {before.jump_url}**",
                user=before.author
            )
            embed.add_field(name="before",value=before.content,inline=False)
            embed.add_field(name="after",value=after.content,inline=False)
            await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message):
        if message.author.id == self.client.user.id: return None
        if message.guild.id != config.guild_id: return None
        channel = self.client.get_channel(config.message_log)
        embed: discord.Embed = await self.log_embed(
            title=f"{message.author.name}#{message.author.discriminator}",
            description=f"<:red:1097244281816748072> **deleted message sent by <@{message.author.id}> in {message.jump_url}**\n{message.content}",
            user=message.author
        )
        log = await channel.send(embed=embed)
        if message.attachments != []:
            await log.reply(files=await self.get_attachments(message.attachments))

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        if member.guild.id != config.guild_id: return None
        channel = self.client.get_channel(config.join_leave_log)
        embed: discord.Embed = await self.log_embed(
            title=f"{member.name}#{member.discriminator}",
            description=f"<:green:1097244269267402812> <@{member.id}> joined the server",
            user=member
        )
        await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        if member.guild.id != config.guild_id: return None
        channel = self.client.get_channel(config.join_leave_log)
        embed: discord.Embed = await self.log_embed(
            title=f"{member.name}#{member.discriminator}",
            description=f"<:red:1097244281816748072> <@{member.id}> left the server",
            user=member
        )
        await channel.send(embed=embed)

    async def get_attachments(self, attachments):
        files = []
        for attach in attachments:
            converted_file = await attach.to_file()
            files.append(converted_file)
        return files

    async def log_embed(self, title, description, user):
        if user.avatar == None:
            avatar = user.default_avatar.url
        else:
            avatar = user.avatar.url
        embed = discord.Embed(
            description=description, 
            color=2829617)
        embed.set_author(name=title,icon_url=avatar)
        return embed