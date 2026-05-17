import discord
from discord.ext import commands
import random
import asyncio

class Des(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def lancer_des(self, nb=2):
        return [random.randint(1, 6) for _ in range(nb)]

    def afficher_de(self, valeur):
        faces = {1:"1️⃣", 2:"2️⃣", 3:"3️⃣", 4:"4️⃣", 5:"5️⃣", 6:"6️⃣"}
        return faces[valeur]

    @commands.command(name="des", aliases=["dice", "roll"])
    async def lancer(self, ctx, nb: int = 2):
        """Lance des dés ! !des <nombre>"""
        if nb < 1 or nb > 10:
            await ctx.send("❌ Lance entre 1 et 10 dés !")
            return

        des = self.lancer_des(nb)
        total = sum(des)
        affichage = " ".join(self.afficher_de(d) for d in des)

        embed = discord.Embed(title="🎲 Lancer de Dés", color=0x9B59B6)
        embed.add_field(name=f"{ctx.author.display_name} lance {nb} dé(s)", value=affichage, inline=False)
        embed.add_field(name="Total", value=f"**{total}**", inline=False)
        await ctx.send(embed=embed)

    @commands.command(name="duel", aliases=["desduel"])
    async def duel_des(self, ctx, adversaire: discord.Member = None):
        """Duel de dés contre quelqu'un ou le bot !"""
        joueur1 = ctx.author

        if adversaire is None or adversaire.bot:
            # Solo contre le bot
            des1 = self.lancer_des()
            des2 = self.lancer_des()
            total1 = sum(des1)
            total2 = sum(des2)

            aff1 = " ".join(self.afficher_de(d) for d in des1)
            aff2 = " ".join(self.afficher_de(d) for d in des2)

            embed = discord.Embed(title="🎲 Duel de Dés !", color=0xFF6B6B)
            embed.add_field(name=f"🎮 {joueur1.display_name}", value=f"{aff1} = **{total1}**", inline=True)
            embed.add_field(name="🤖 Bot", value=f"{aff2} = **{total2}**", inline=True)

            if total1 > total2:
                embed.add_field(name="🏆 Résultat", value=f"**{joueur1.display_name}** gagne !", inline=False)
                embed.color = 0x00FF00
            elif total2 > total1:
                embed.add_field(name="🏆 Résultat", value="**Le Bot** gagne !", inline=False)
                embed.color = 0xFF0000
            else:
                embed.add_field(name="🏆 Résultat", value="**Égalité !** 🤝", inline=False)
                embed.color = 0xFFFF00

            await ctx.send(embed=embed)
            return

        if adversaire == joueur1:
            await ctx.send("❌ Tu ne peux pas te défier toi-même !")
            return

        # Défi multijoueur
        embed = discord.Embed(
            title="🎲 Duel de Dés !",
            description=f"{adversaire.mention}, {joueur1.display_name} te défie ! Tu acceptes ? (`oui` / `non`)",
            color=0xFF6B6B
        )
        await ctx.send(embed=embed)

        def check(m):
            return m.author == adversaire and m.channel == ctx.channel and m.content.lower() in ["oui", "non"]

        try:
            msg = await self.bot.wait_for("message", check=check, timeout=30)
        except asyncio.TimeoutError:
            await ctx.send("⏰ Pas de réponse, duel annulé !")
            return

        if msg.content.lower() == "non":
            await ctx.send(f"😢 {adversaire.display_name} a refusé !")
            return

        des1 = self.lancer_des()
        des2 = self.lancer_des()
        total1 = sum(des1)
        total2 = sum(des2)

        aff1 = " ".join(self.afficher_de(d) for d in des1)
        aff2 = " ".join(self.afficher_de(d) for d in des2)

        embed = discord.Embed(title="🎲 Duel de Dés !", color=0xFF6B6B)
        embed.add_field(name=f"🎮 {joueur1.display_name}", value=f"{aff1} = **{total1}**", inline=True)
        embed.add_field(name=f"🎮 {adversaire.display_name}", value=f"{aff2} = **{total2}**", inline=True)

        if total1 > total2:
            embed.add_field(name="🏆 Gagnant", value=f"**{joueur1.display_name}** gagne !", inline=False)
            embed.color = 0x00FF00
        elif total2 > total1:
            embed.add_field(name="🏆 Gagnant", value=f"**{adversaire.display_name}** gagne !", inline=False)
            embed.color = 0x00FF00
        else:
            embed.add_field(name="🏆 Résultat", value="**Égalité !** 🤝", inline=False)
            embed.color = 0xFFFF00

        await ctx.send(embed=embed)

    @lancer.error
    async def lancer_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            await ctx.send("❌ Utilisation : `!des <nombre>` (ex: `!des 3`)")

async def setup(bot):
    await bot.add_cog(Des(bot))
