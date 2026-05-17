import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.dm_messages = True

bot = commands.Bot(command_prefix="!", intents=intents)

async def load_extensions():
    await bot.load_extension("games.action_verite")
    await bot.load_extension("games.puissance4")
    await bot.load_extension("games.devine_tete")

@bot.event
async def on_ready():
    print(f"✅ {bot.user} est connecté et prêt !")
    print(f"📋 Serveurs : {[g.name for g in bot.guilds]}")
    await bot.change_presence(activity=discord.Game(name="!aide pour les jeux 🎮"))

@bot.command(name="aide", aliases=["help_jeux"])
async def aide(ctx):
    embed = discord.Embed(
        title="🎮 Mini-Jeux disponibles",
        description="Fonctionne en serveur ET en MP 📩",
        color=0x5865F2
    )
    embed.add_field(
        name="🎭 Action ou Vérité",
        value="`!av` — Lance une partie\n`!action` — Tire une action\n`!verite` — Tire une vérité",
        inline=False
    )
    embed.add_field(
        name="🔴 Puissance 4",
        value="`!p4` — Solo contre le bot (MP)\n`!p4 @adversaire` — Contre quelqu'un (serveur)\n`!jouer <1-7>` — Place ton jeton\n`!abandon` — Abandonne",
        inline=False
    )
    embed.add_field(
        name="🤔 Devine la Tête",
        value="`!devine` — Lance une partie\n`!indice` — Demande un indice\n`!reponse <nom>` — Propose une réponse\n`!passedevine` — Abandonne",
        inline=False
    )
    embed.set_footer(text="Bot Mini-Jeux • Bonne chance ! 🍀")
    await ctx.send(embed=embed)

async def main():
    async with bot:
        await load_extensions()
        await bot.start(TOKEN)

import asyncio
asyncio.run(main())
