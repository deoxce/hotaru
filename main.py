import discord
import discord.utils
from discord.ui import Button, View
from discord.ext import commands
import config
import asyncio

from aiohttp import web

async def handle(request: web.Request):
    if request.path == '/hotarustop':
        tgid = request.rel_url.query['user']
        if tgid in config.admin_ids:
            print("stopped")
            asyncio.create_task(client.close())
            return web.Response(text='bot stopped')
        else:
            print(tgid)
            return web.Response(text='you have no permission')
    elif request.path == '/ping':
        print("pong")
        return web.Response(text='pong 🏓')
    else:
        return web.Response(status=404)
    
async def start_http_server():
    app = web.Application()
    app.add_routes([web.get('/{tail:.*}', handle)])

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 8080)
    await site.start()

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
status = discord.Status.offline
client = commands.Bot(intents=intents, status=status)

temp_channels = []

client.loop.create_task(start_http_server())

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
    await client.get_channel(config.verification_channel).send(view=view, embed=embed)
    print("ready")

async def create_button():
    view = View(timeout=None)
    button_start = Button(label="verification", style=discord.ButtonStyle.green)
    button_start.callback = give_role
    view.add_item(button_start)
    return view

async def give_role(ctx: discord.Interaction):
    role = discord.utils.get(ctx.guild.roles, name=config.default_role)
    await ctx.user.add_roles(role)
    await ctx.response.send_message("done", ephemeral=True)
    await asyncio.sleep(5)
    await ctx.delete_original_response()

async def voice_create(member: discord.Member):
    global temp_channels
    log_channel = client.get_channel(config.voice_log)
    create_channel = client.get_channel(config.tempvoice_channel)
    temp_channel = await create_channel.category.create_voice_channel(member.name)
    temp_channels.append(temp_channel)
    embed:discord.Embed = await log_embed(
        title=f"{client.user.name}",
        description=f"<:green:1097244269267402812> tempvoice <#{temp_channel.id}> was created",
        user=client.user
        )
    await log_channel.send(embed=embed)
    await member.move_to(temp_channel)

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
    global temp_channels
    log_channel = client.get_channel(config.voice_log)
    if member.guild.id != config.guild_id: return None
    # Joined channel
    if before.channel == None:
        embed:discord.Embed = await log_embed(
            title=f"{member.name}#{member.discriminator}",
            description=f"<:green:1097244269267402812> <@{member.id}> entered <#{after.channel.id}>",
            user=member
            )
        await log_channel.send(embed=embed)
    # Moved between channels
    if before.channel != None and after.channel != None and before.channel!=after.channel:
        embed:discord.Embed = await log_embed(
            title=f"{member.name}#{member.discriminator}",
            description=f"<:blue:1097244258043445309> <@{member.id}> moved from <#{before.channel.id}> to <#{after.channel.id}>",
            user=member
        )
        await log_channel.send(embed=embed)
    # Left channel
    if after.channel == None:
        embed:discord.Embed = await log_embed(
            title=f"{member.name}#{member.discriminator}",
            description=f"<:red:1097244281816748072> <@{member.id}> left <#{before.channel.id}>",
            user=member
        )
        await log_channel.send(embed=embed)
    # Tempvoice creation
    if after.channel != None and after.channel.id == config.tempvoice_channel:
        await voice_create(member)
    #   Tempvoice deletion
    if before.channel != None and before.channel in temp_channels and before.channel.members == []:
        await before.channel.delete()
        embed:discord.Embed = await log_embed(
            title=f"{client.user.name}",
            description=f"<:red:1097244281816748072> tempvoice `#{before.channel.name}` was deleted",
            user=client.user
            )
        await log_channel.send(embed=embed)

@client.event
async def on_member_ban(guild: discord.Guild, user: discord.User):
    if guild.id != config.guild_id: return None
    channel = client.get_channel(config.ban_log)
    embed:discord.Embed = await log_embed(
        title=f"{user.name}#{user.discriminator}",
        description=f"<:red:1097244281816748072> <@{user.id}> was banned",
        user=user
    )
    await channel.send(embed=embed)

@client.event
async def on_member_unban(guild: discord.Guild, user: discord.User):
    if guild.id != config.guild_id: return None
    channel = client.get_channel(config.ban_log)
    embed:discord.Embed = await log_embed(
        title=f"{user.name}#{user.discriminator}",
        description=f"<:green:1097244269267402812> <@{user.id}> was unbanned",
        user=user
    )
    await channel.send(embed=embed)

@client.event
async def on_message_edit(before: discord.Message, after: discord.Message):
    if before.guild.id != config.guild_id: return None
    channel = client.get_channel(config.message_log)
    if before.content == after.content and len(after.attachments) < len(before.attachments):
        embed:discord.Embed = await log_embed(
            title=f"{before.author.name}#{before.author.discriminator}",
            description=f"<:red:1097244281816748072> <@{before.author.id}> removed attachment from {before.jump_url}\n",
            user=before.author
        )
        files = [item for item in before.attachments if item not in after.attachments]
        log = await channel.send(embed=embed)
        await log.reply(files=await get_attachments(files))
    elif before.content != after.content:
        embed:discord.Embed = await log_embed(
            title=f"{before.author.name}#{before.author.discriminator}",
            description=f"<:blue:1097244258043445309> **<@{before.author.id}> edited message {before.jump_url}**",
            user=before.author
        )
        embed.add_field(name="before",value=before.content,inline=False)
        embed.add_field(name="after",value=after.content,inline=False)
        await channel.send(embed=embed)

@client.event
async def on_message_delete(message: discord.Message):
    if message.author.id == client.user.id: return None
    if message.guild.id != config.guild_id: return None
    channel = client.get_channel(config.message_log)
    embed: discord.Embed = await log_embed(
        title=f"{message.author.name}#{message.author.discriminator}",
        description=f"<:red:1097244281816748072> **deleted message sent by <@{message.author.id}> in {message.jump_url}**\n{message.content}",
        user=message.author
    )
    log = await channel.send(embed=embed)
    if message.attachments != []:
        await log.reply(files=await get_attachments(message.attachments))

@client.event
async def on_member_join(member: discord.Member):
    if member.guild.id != config.guild_id: return None
    channel = client.get_channel(config.join_leave_log)
    embed: discord.Embed = await log_embed(
        title=f"{member.name}#{member.discriminator}",
        description=f"<:green:1097244269267402812> <@{member.id}> joined the server",
        user=member
    )
    await channel.send(embed=embed)

@client.event
async def on_member_remove(member: discord.Member):
    if member.guild.id != config.guild_id: return None
    channel = client.get_channel(config.join_leave_log)
    embed: discord.Embed = await log_embed(
        title=f"{member.name}#{member.discriminator}",
        description=f"<:red:1097244281816748072> <@{member.id}> left the server",
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