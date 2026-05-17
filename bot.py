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
    await bot.load_extension("games.jackpot")
    await bot.load_extension("games.des")
    await bot.load_extension("games.quiz")
    await bot.load_extension("games.pfc")
    await bot.load_extension("games.morpion")
    await bot.load_extension("games.pendu")
    await bot.load_extension("games.nombre_mystere")

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
        value="`!av` `!action` `!verite`",
        inline=True
    )
    embed.add_field(
        name="🔴 Puissance 4",
        value="`!p4` `!p4 @pseudo` `!jouer <1-7>` `!abandon`",
        inline=True
    )
    embed.add_field(
        name="🤔 Devine la Tête",
        value="`!devine` `!indice` `!reponse <nom>` `!passedevine`",
        inline=True
    )
    embed.add_field(
        name="🎰 Jackpot",
        value="`!jackpot <mise>` `!coins` `!daily`",
        inline=True
    )
    embed.add_field(
        name="🎲 Dés",
        value="`!des <nb>` `!duel @pseudo`",
        inline=True
    )
    embed.add_field(
        name="❓ Quiz",
        value="`!quiz` `!quiz <cat>` `!quizcats` `!quizscore`",
        inline=True
    )
    embed.add_field(
        name="✂️ Pierre Feuille Ciseaux",
        value="`!pfc` `!pfc @pseudo`",
        inline=True
    )
    embed.add_field(
        name="❌⭕ Morpion",
        value="`!morpion` `!morpion @pseudo` `!case <1-9>` `!stopmorpion`",
        inline=True
    )
    embed.add_field(
        name="🪢 Pendu",
        value="`!pendu` `!lettre <a-z>` `!motentier <mot>` `!stoppendu`",
        inline=True
    )
    embed.add_field(
        name="🔢 Nombre Mystère",
        value="`!nombre` `!nombre <max>` `!proposer <nb>` `!stopnombre`",
        inline=True
    )
    embed.set_footer(text="Bot Mini-Jeux • Bonne chance ! 🍀")
    await ctx.send(embed=embed)

async def main():
    async with bot:
        await load_extensions()
        await bot.start(TOKEN)

import asyncio
asyncio.run(main())
