import discord
import discord.utils
from discord.ext import commands
import config
import asyncio

from tempvoice import tempvoice
from logs import logs
from verification import verification

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

client.add_cog(tempvoice(client))
client.add_cog(logs(client))
client.add_cog(verification(client))

client.loop.create_task(start_http_server())

@client.check
async def guild_only(ctx: discord.Interaction):
    if not ctx.guild:
        await ctx.response.send_message("this command cannot be used in private messages")
        raise commands.NoPrivateMessage
    return True

@client.slash_command(name="give_unverified")
async def give_unverified(ctx: discord.Interaction):
    unverified_role = discord.utils.get(ctx.guild.roles, id=config.unverified_role)
    verified_role = discord.utils.get(ctx.guild.roles, id=config.default_role)
    count = 0
    for member in ctx.guild.members:
        if not member.bot and verified_role not in member.roles and unverified_role not in member.roles:
            await member.add_roles(unverified_role)
            count += 1
    await ctx.response.send_message(f"done. successfully assigned role to {count} members", ephemeral=True)

client.run(config.token)