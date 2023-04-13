import discord
import discord.utils
from discord.ui import Button, View
from discord.ext import commands
import config
import asyncio

intents = discord.Intents.default()
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
    embed = await create_embed()
    await client.get_channel(1095390051829030972).send(view=view, embed=embed)
    print("ready")

async def create_button():
    view = View(timeout=None)
    button_start = Button(label="verification", style=discord.ButtonStyle.green)
    button_start.callback = give_role
    view.add_item(button_start)
    return view

async def create_embed():
    embed = discord.Embed(title="verification", description=f"please use the button below to verify that you are not a robot", color=2829617)
    return embed

async def give_role(ctx: discord.Interaction):
    role = discord.utils.get(ctx.guild.roles, name="Dudes")
    await ctx.user.add_roles(role)
    await ctx.response.send_message("done", ephemeral=True)
    await asyncio.sleep(5)
    await ctx.delete_original_response()

client.run(config.token)