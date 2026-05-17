import discord
from discord.ext import commands
import random

class NombreMystere(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.parties = {}

    @commands.command(name="nombre", aliases=["mystery", "guess"])
    async def nombre(self, ctx, max_val: int = 100):
        """Devine le nombre mystère ! !nombre ou !nombre <max>"""
        uid = ctx.author.id

        if uid in self.parties:
            await ctx.send("❌ Tu as déjà une partie en cours ! Tape `!proposer <nombre>`.")
            return

        if max_val < 10 or max_val > 10000:
            await ctx.send("❌ Le maximum doit être entre 10 et 10000 !")
            return

        nombre = random.randint(1, max_val)
        self.parties[uid] = {
            "nombre": nombre,
            "max": max_val,
            "tentatives": 0,
            "max_tentatives": 7 if max_val <= 100 else 10,
        }

        embed = discord.Embed(
            title="🔢 Nombre Mystère !",
            description=f"J'ai choisi un nombre entre **1** et **{max_val}**.\nTu as **{self.parties[uid]['max_tentatives']} essais** pour le trouver !",
            color=0x3498DB
        )
        embed.set_footer(text="!proposer <nombre> pour deviner • !stopnombre pour abandonner")
        await ctx.send(embed=embed)

    @commands.command(name="proposer", aliases=["prop"])
    async def proposer(self, ctx, proposition: int):
        """Propose un nombre pour le jeu du nombre mystère"""
        uid = ctx.author.id

        if uid not in self.parties:
            await ctx.send("❌ Pas de partie en cours ! Lance-en une avec `!nombre`")
            return

        partie = self.parties[uid]
        partie["tentatives"] += 1
        nb = partie["nombre"]
        max_t = partie["max_tentatives"]
        restantes = max_t - partie["tentatives"]

        if proposition == nb:
            embed = discord.Embed(title="🎉 Bravo, tu as trouvé !", color=0x00FF00)
            embed.add_field(name="Le nombre était", value=f"**{nb}**", inline=False)
            embed.add_field(name="Tentatives", value=f"**{partie['tentatives']}** essai(s)", inline=False)

            # Évaluation
            if partie["tentatives"] <= 3:
                embed.add_field(name="⭐ Performance", value="Incroyable ! Tu lis dans les pensées ! 🔮", inline=False)
            elif partie["tentatives"] <= 5:
                embed.add_field(name="⭐ Performance", value="Très bien ! 👏", inline=False)
            else:
                embed.add_field(name="⭐ Performance", value="C'est trouvé ! 😊", inline=False)

            embed.set_footer(text="Rejoue avec !nombre !")
            await ctx.send(embed=embed)
            del self.parties[uid]
            return

        if restantes <= 0:
            embed = discord.Embed(title="💀 Plus d'essais !", color=0xFF0000)
            embed.add_field(name="Le nombre était", value=f"**{nb}**", inline=False)
            embed.set_footer(text="Rejoue avec !nombre !")
            await ctx.send(embed=embed)
            del self.parties[uid]
            return

        # Indice chaud/froid
        diff = abs(proposition - nb)
        if diff <= partie["max"] * 0.05:
            indice = "🔥🔥🔥 BRÛLANT !"
        elif diff <= partie["max"] * 0.10:
            indice = "🔥🔥 Très chaud !"
        elif diff <= partie["max"] * 0.20:
            indice = "🔥 Chaud !"
        elif diff <= partie["max"] * 0.35:
            indice = "😐 Tiède..."
        else:
            indice = "🧊 Froid !"

        direction = "📈 Plus grand !" if proposition < nb else "📉 Plus petit !"

        embed = discord.Embed(
            title=f"{'❌'} Raté !",
            color=0xFF6B35
        )
        embed.add_field(name="Direction", value=direction, inline=True)
        embed.add_field(name="Température", value=indice, inline=True)
        embed.add_field(name="Essais restants", value=f"**{restantes}**", inline=False)
        await ctx.send(embed=embed)

    @commands.command(name="stopnombre")
    async def stop_nombre(self, ctx):
        """Abandonne le jeu du nombre mystère"""
        uid = ctx.author.id
        if uid not in self.parties:
            await ctx.send("❌ Pas de partie en cours !")
            return
        nb = self.parties[uid]["nombre"]
        del self.parties[uid]
        await ctx.send(f"🏳️ Partie abandonnée ! Le nombre était **{nb}**.")

    @proposer.error
    async def proposer_error(self, ctx, error):
        if isinstance(error, (commands.MissingRequiredArgument, commands.BadArgument)):
            await ctx.send("❌ Utilisation : `!proposer <nombre>` (ex: `!proposer 42`)")

async def setup(bot):
    await bot.add_cog(NombreMystere(bot))
