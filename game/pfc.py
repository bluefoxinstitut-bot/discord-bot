import discord
from discord.ext import commands
import random
import asyncio

CHOIX = {"pierre": "🪨", "feuille": "📄", "ciseaux": "✂️"}
GAGNE = {"pierre": "ciseaux", "feuille": "pierre", "ciseaux": "feuille"}

class PFC(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.duels = {}

    def determiner_gagnant(self, j1, j2):
        if j1 == j2:
            return "egalite"
        if GAGNE[j1] == j2:
            return "j1"
        return "j2"

    @commands.command(name="pfc", aliases=["rps", "chifoumi"])
    async def pfc(self, ctx, choix_joueur: str = None, adversaire: discord.Member = None):
        """Pierre Feuille Ciseaux ! !pfc <pierre/feuille/ciseaux> ou !pfc @adversaire"""

        # Mode multijoueur
        if adversaire and not adversaire.bot:
            await self.duel_pfc(ctx, adversaire)
            return

        # Mode solo contre le bot
        if not choix_joueur or choix_joueur.lower() not in CHOIX:
            embed = discord.Embed(
                title="✂️ Pierre Feuille Ciseaux",
                description="Choisis avec les réactions !",
                color=0xFF6B6B
            )
            msg = await ctx.send(embed=embed)
            for emoji in ["🪨", "📄", "✂️"]:
                await msg.add_reaction(emoji)

            emoji_to_choix = {"🪨": "pierre", "📄": "feuille", "✂️": "ciseaux"}

            def check(r, u):
                return u == ctx.author and str(r.emoji) in emoji_to_choix and r.message.id == msg.id

            try:
                reaction, _ = await self.bot.wait_for("reaction_add", check=check, timeout=30)
                choix_joueur = emoji_to_choix[str(reaction.emoji)]
            except asyncio.TimeoutError:
                await ctx.send("⏰ Temps écoulé !")
                return
        else:
            choix_joueur = choix_joueur.lower()

        choix_bot = random.choice(list(CHOIX.keys()))
        resultat = self.determiner_gagnant(choix_joueur, choix_bot)

        embed = discord.Embed(title="✂️ Pierre Feuille Ciseaux !", color=0xFF6B6B)
        embed.add_field(name=f"👤 {ctx.author.display_name}", value=f"{CHOIX[choix_joueur]} **{choix_joueur.capitalize()}**", inline=True)
        embed.add_field(name="🤖 Bot", value=f"{CHOIX[choix_bot]} **{choix_bot.capitalize()}**", inline=True)

        if resultat == "egalite":
            embed.add_field(name="🏆 Résultat", value="**Égalité !** 🤝", inline=False)
            embed.color = 0xFFFF00
        elif resultat == "j1":
            embed.add_field(name="🏆 Résultat", value=f"**{ctx.author.display_name}** gagne ! 🎉", inline=False)
            embed.color = 0x00FF00
        else:
            embed.add_field(name="🏆 Résultat", value="**Le Bot** gagne ! 😈", inline=False)
            embed.color = 0xFF0000

        await ctx.send(embed=embed)

    async def duel_pfc(self, ctx, adversaire):
        """Duel PFC entre deux joueurs"""
        if ctx.author.id in self.duels or adversaire.id in self.duels:
            await ctx.send("❌ Un des joueurs a déjà un duel en cours !")
            return

        embed = discord.Embed(
            title="✂️ Duel Pierre Feuille Ciseaux !",
            description=f"{adversaire.mention}, **{ctx.author.display_name}** te défie ! Tu acceptes ? (`oui` / `non`)",
            color=0xFF6B6B
        )
        await ctx.send(embed=embed)

        def check_accept(m):
            return m.author == adversaire and m.channel == ctx.channel and m.content.lower() in ["oui", "non"]

        try:
            msg = await self.bot.wait_for("message", check=check_accept, timeout=30)
        except asyncio.TimeoutError:
            await ctx.send("⏰ Pas de réponse, duel annulé !")
            return

        if msg.content.lower() == "non":
            await ctx.send(f"😢 {adversaire.display_name} a refusé !")
            return

        self.duels[ctx.author.id] = None
        self.duels[adversaire.id] = None

        emoji_to_choix = {"🪨": "pierre", "📄": "feuille", "✂️": "ciseaux"}

        async def demander_choix(joueur):
            try:
                dm = await joueur.send(f"✂️ **Duel contre {ctx.author.display_name if joueur == adversaire else adversaire.display_name}** — Choisis avec les réactions !")
                for emoji in ["🪨", "📄", "✂️"]:
                    await dm.add_reaction(emoji)

                def check_dm(r, u):
                    return u == joueur and str(r.emoji) in emoji_to_choix and r.message.id == dm.id

                reaction, _ = await self.bot.wait_for("reaction_add", check=check_dm, timeout=60)
                return emoji_to_choix[str(reaction.emoji)]
            except Exception:
                return random.choice(list(CHOIX.keys()))

        await ctx.send("📩 J'ai envoyé un MP à chacun pour votre choix secret ! Vous avez 60 secondes.")

        import asyncio
        resultats = await asyncio.gather(
            demander_choix(ctx.author),
            demander_choix(adversaire)
        )

        c1, c2 = resultats
        del self.duels[ctx.author.id]
        del self.duels[adversaire.id]

        resultat = self.determiner_gagnant(c1, c2)
        embed = discord.Embed(title="✂️ Résultat du Duel !", color=0xFF6B6B)
        embed.add_field(name=f"👤 {ctx.author.display_name}", value=f"{CHOIX[c1]} **{c1.capitalize()}**", inline=True)
        embed.add_field(name=f"👤 {adversaire.display_name}", value=f"{CHOIX[c2]} **{c2.capitalize()}**", inline=True)

        if resultat == "egalite":
            embed.add_field(name="🏆 Résultat", value="**Égalité !** 🤝", inline=False)
            embed.color = 0xFFFF00
        elif resultat == "j1":
            embed.add_field(name="🏆 Résultat", value=f"**{ctx.author.display_name}** gagne ! 🎉", inline=False)
            embed.color = 0x00FF00
        else:
            embed.add_field(name="🏆 Résultat", value=f"**{adversaire.display_name}** gagne ! 🎉", inline=False)
            embed.color = 0x00FF00

        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(PFC(bot))
