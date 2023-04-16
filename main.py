import discord
import discord.utils
from discord.ui import Button, View
from discord.ext import commands
import config
import asyncio

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
status = discord.Status.offline
client = commands.Bot(intents=intents, status=status)

@client.check
async def guild_only(ctx: discord.Interaction):
    if not ctx.guild:
        await ctx.response.send_message("this command cannot be used in private messages")
        raise commands.NoPrivateMessage
    return True

@client.event
async def on_ready():
    view = await create_button()
    embed = discord.Embed(
        title="verification", 
        description=f"please use the button below to verify that you are not a robot", 
        color=2829617)
    await client.get_channel(1096122598171086979).send(view=view, embed=embed)
    print("ready")

async def create_button():
    view = View(timeout=None)
    button_start = Button(label="verification", style=discord.ButtonStyle.green)
    button_start.callback = give_role
    view.add_item(button_start)
    return view

async def give_role(ctx: discord.Interaction):
    role = discord.utils.get(ctx.guild.roles, name="test")
    await ctx.user.add_roles(role)
    await ctx.response.send_message("done", ephemeral=True)
    await asyncio.sleep(5)
    await ctx.delete_original_response()

async def log_embed(title, description, user):
    if user.avatar == None:
        avatar = user.default_avatar.url
    else:
        avatar = user.avatar.url
    embed = discord.Embed(
        description=description, 
        color=2829617)
    embed.set_author(name=title,icon_url=avatar)
    return embed

@client.event
async def on_voice_state_update(member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
    channel = client.get_channel(config.voice_log)
    if before.channel == None:
        embed:discord.Embed = await log_embed(
            title=f"{member.name}#{member.discriminator}",
            description=f"<@{member.id}> entered <#{after.channel.id}>",
            user=member
            )
        await channel.send(embed=embed)
    if before.channel != None and after.channel != None and before.channel!=after.channel:
        embed:discord.Embed = await log_embed(
            title=f"{member.name}#{member.discriminator}",
            description=f"<@{member.id}> moved from <#{before.channel.id}> to <#{after.channel.id}>",
            user=member
        )
        await channel.send(embed=embed)
    if after.channel == None:
        embed:discord.Embed = await log_embed(
            title=f"{member.name}#{member.discriminator}",
            description=f"<@{member.id}> left <#{before.channel.id}>",
            user=member
        )
        await channel.send(embed=embed)

@client.event
async def on_member_ban(guild: discord.Guild, user: discord.User):
    channel = client.get_channel(config.ban_log)
    embed:discord.Embed = await log_embed(
        title="member banned",
        description=f"<@{user.id}>",
        user=user
    )
    await channel.send(embed=embed)

@client.event
async def on_member_unban(guild: discord.Guild, user: discord.User):
    channel = client.get_channel(config.ban_log)
    embed:discord.Embed = await log_embed(
        title="member unbanned",
        description=f"<@{user.id}>",
        user=user
    )
    await channel.send(embed=embed)

@client.event
async def on_message_edit(before: discord.Message, after: discord.Message):
    channel = client.get_channel(config.message_log)
    if before.content == after.content and after.attachments != [] and len(after.attachments) < len(before.attachments):
        embed:discord.Embed = await log_embed(
            title=f"{before.author.name}#{before.author.discriminator}",
            description=f"<@{before.author.id}> removed attachment from {before.jump_url}\n",
            user=before.author
        )
        files = [item for item in before.attachments if item not in after.attachments]
        log = await channel.send(embed=embed)
        await log.reply(files=await get_attachments(files))
    elif before.content != after.content:
        embed:discord.Embed = await log_embed(
            title=f"{before.author.name}#{before.author.discriminator}",
            description=f"**<@{before.author.id}> edited message {before.jump_url}**",
            user=before.author
        )
        embed.add_field(name="before",value=before.content,inline=False)
        embed.add_field(name="after",value=after.content,inline=False)
        await channel.send(embed=embed)
    

@client.event
async def on_message_delete(message: discord.Message):
    channel = client.get_channel(config.message_log)
    embed: discord.Embed = await log_embed(
        title=f"{message.author.name}#{message.author.discriminator}",
        description=f"**deleted message sent by <@{message.author.id}> in <#{message.channel.id}>**\n{message.content}",
        user=message.author
    )
    log = await channel.send(embed=embed)
    if message.attachments != []:
        await log.reply(files=await get_attachments(message.attachments))

@client.event
async def on_member_join(member: discord.Member):
    channel = client.get_channel(config.join_leave_log)
    embed: discord.Embed = await log_embed(
        title=f"{member.name}#{member.discriminator}",
        description=f"<@{member.id}> joined the server",
        user=member
    )
    await channel.send(embed=embed)

@client.event
async def on_member_remove(member: discord.Member):
    channel = client.get_channel(config.join_leave_log)
    embed: discord.Embed = await log_embed(
        title=f"{member.name}#{member.discriminator}",
        description=f"<@{member.id}> left the server",
        user=member
    )
    await channel.send(embed=embed)

async def get_attachments(attachments):
    files = []
    for attach in attachments:
        converted_file = await attach.to_file()
        files.append(converted_file)
    return files

client.run(config.token)