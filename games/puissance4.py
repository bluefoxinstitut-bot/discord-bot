import discord
from discord.ext import commands
import asyncio
import random

LIGNES = 6
COLONNES = 7

VIDE = "⚫"
ROUGE = "🔴"
JAUNE = "🟡"

NUMS = ["1️⃣","2️⃣","3️⃣","4️⃣","5️⃣","6️⃣","7️⃣"]

def creer_grille():
    return [[VIDE] * COLONNES for _ in range(LIGNES)]

def afficher_grille(grille):
    lignes = [" ".join(ligne) for ligne in grille]
    lignes.append(" ".join(NUMS))
    return "\n".join(lignes)

def placer_jeton(grille, col, jeton):
    for ligne in range(LIGNES - 1, -1, -1):
        if grille[ligne][col] == VIDE:
            grille[ligne][col] = jeton
            return ligne
    return -1

def verifier_victoire(grille, jeton):
    for l in range(LIGNES):
        for c in range(COLONNES - 3):
            if all(grille[l][c+i] == jeton for i in range(4)):
                return True
    for l in range(LIGNES - 3):
        for c in range(COLONNES):
            if all(grille[l+i][c] == jeton for i in range(4)):
                return True
    for l in range(LIGNES - 3):
        for c in range(COLONNES - 3):
            if all(grille[l+i][c+i] == jeton for i in range(4)):
                return True
    for l in range(3, LIGNES):
        for c in range(COLONNES - 3):
            if all(grille[l-i][c+i] == jeton for i in range(4)):
                return True
    return False

def grille_pleine(grille):
    return all(grille[0][c] != VIDE for c in range(COLONNES))

def coup_bot(grille):
    """IA simple : gagne si possible, bloque sinon, sinon aléatoire"""
    # Essaie de gagner
    for c in range(COLONNES):
        g = [ligne[:] for ligne in grille]
        if placer_jeton(g, c, JAUNE) != -1 and verifier_victoire(g, JAUNE):
            return c
    # Essaie de bloquer le joueur
    for c in range(COLONNES):
        g = [ligne[:] for ligne in grille]
        if placer_jeton(g, c, ROUGE) != -1 and verifier_victoire(g, ROUGE):
            return c
    # Préfère le centre
    colonnes_prio = [3, 2, 4, 1, 5, 0, 6]
    for c in colonnes_prio:
        if grille[0][c] == VIDE:
            return c
    return -1

class Puissance4(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.parties = {}  # channel_id -> état de la partie

    def get_channel_id(self, ctx):
        """Retourne un ID unique pour MP ou salon serveur"""
        if ctx.guild:
            return ctx.channel.id
        return ctx.author.id  # En MP, on utilise l'ID de l'utilisateur

    @commands.command(name="p4", aliases=["puissance4", "connect4"])
    async def lancer_p4(self, ctx, adversaire: discord.Member = None):
        """Lance une partie de Puissance 4"""
        cid = self.get_channel_id(ctx)

        if cid in self.parties:
            await ctx.send("❌ Tu as déjà une partie en cours ! Utilise `!abandon` pour l'arrêter.")
            return

        # Mode MP ou solo : pas d'adversaire → jouer contre le bot
        if not ctx.guild or adversaire is None:
            self.parties[cid] = {
                "grille": creer_grille(),
                "joueurs": [ctx.author, None],  # None = bot
                "jetons": [ROUGE, JAUNE],
                "tour": 0,
                "solo": True,
                "channel": ctx.channel,
            }
            embed = discord.Embed(
                title="🔴🟡 Puissance 4 — Solo contre le Bot !",
                description=f"**{ctx.author.display_name}** 🔴 vs 🟡 **Bot**\n\nTape `!jouer <1-7>` pour placer ton jeton !",
                color=0xFFD700
            )
            await ctx.send(embed=embed)
            await self.afficher_tour(ctx)
            return

        # Mode serveur : adversaire humain
        if adversaire.bot or adversaire == ctx.author:
            await ctx.send("❌ Choisis un vrai joueur ! (ou tape `!p4` sans mentionner pour jouer contre le bot)")
            return

        embed = discord.Embed(
            title="🔴🟡 Puissance 4 !",
            description=f"**{ctx.author.display_name}** défie **{adversaire.display_name}** !\n\n{adversaire.mention}, tu acceptes ? (`oui` / `non` dans 30 secondes)",
            color=0xFFD700
        )
        await ctx.send(embed=embed)

        def check_confirm(m):
            return m.author == adversaire and m.channel == ctx.channel and m.content.lower() in ["oui", "non"]

        try:
            msg = await self.bot.wait_for("message", check=check_confirm, timeout=30)
        except asyncio.TimeoutError:
            await ctx.send(f"⏰ {adversaire.display_name} n'a pas répondu. Partie annulée.")
            return

        if msg.content.lower() == "non":
            await ctx.send(f"😢 {adversaire.display_name} a refusé la partie.")
            return

        self.parties[cid] = {
            "grille": creer_grille(),
            "joueurs": [ctx.author, adversaire],
            "jetons": [ROUGE, JAUNE],
            "tour": 0,
            "solo": False,
            "channel": ctx.channel,
        }
        await self.afficher_tour(ctx)

    async def afficher_tour(self, ctx):
        cid = self.get_channel_id(ctx)
        partie = self.parties.get(cid)
        if not partie:
            return

        tour = partie["tour"] % 2
        joueur = partie["joueurs"][tour]
        jeton = partie["jetons"][tour]
        grille_str = afficher_grille(partie["grille"])

        # Tour du bot (solo)
        if partie["solo"] and joueur is None:
            col = coup_bot(partie["grille"])
            placer_jeton(partie["grille"], col, JAUNE)

            if verifier_victoire(partie["grille"], JAUNE):
                embed = discord.Embed(title="😅 Le Bot a gagné !", description=afficher_grille(partie["grille"]), color=0xFF8800)
                embed.add_field(name="💀", value="Le bot t'a battu ! Retente avec `!p4` !", inline=False)
                await ctx.send(embed=embed)
                del self.parties[cid]
                return

            if grille_pleine(partie["grille"]):
                embed = discord.Embed(title="🤝 Match nul !", description=afficher_grille(partie["grille"]), color=0x888888)
                await ctx.send(embed=embed)
                del self.parties[cid]
                return

            partie["tour"] += 1
            # Réafficher pour le joueur humain
            grille_str = afficher_grille(partie["grille"])
            embed = discord.Embed(title="🔴🟡 Puissance 4", description=grille_str, color=0xFF0000)
            embed.add_field(name="Ton tour 🔴", value="Tape `!jouer <1-7>` pour placer ton jeton", inline=False)
            await ctx.send(embed=embed)
            return

        nom = joueur.display_name if joueur else "Bot"
        couleur = 0xFF0000 if jeton == ROUGE else 0xFFD700

        embed = discord.Embed(title="🔴🟡 Puissance 4", description=grille_str, color=couleur)
        embed.add_field(
            name=f"Tour de {jeton} {nom}",
            value="Tape `!jouer <1-7>` pour placer ton jeton",
            inline=False
        )
        embed.set_footer(text="!abandon pour arrêter la partie")
        await ctx.send(embed=embed)

    @commands.command(name="jouer")
    async def jouer(self, ctx, colonne: int):
        """Place un jeton dans la colonne choisie (1-7)"""
        cid = self.get_channel_id(ctx)

        if cid not in self.parties:
            await ctx.send("❌ Pas de partie en cours ! Lance-en une avec `!p4`")
            return

        partie = self.parties[cid]
        tour = partie["tour"] % 2
        joueur_actuel = partie["joueurs"][tour]

        # Vérifier que c'est bien le bon joueur (en serveur)
        if ctx.guild and not partie["solo"] and ctx.author != joueur_actuel:
            await ctx.send(f"⛔ C'est au tour de **{joueur_actuel.display_name}** !", delete_after=5)
            return

        col = colonne - 1
        if not (0 <= col < COLONNES):
            await ctx.send("❌ Colonne invalide ! Choisis entre 1 et 7.", delete_after=5)
            return

        jeton = partie["jetons"][tour]
        ligne = placer_jeton(partie["grille"], col, jeton)

        if ligne == -1:
            await ctx.send("❌ Cette colonne est pleine ! Choisis-en une autre.", delete_after=5)
            return

        partie["tour"] += 1
        nom = ctx.author.display_name

        if verifier_victoire(partie["grille"], jeton):
            embed = discord.Embed(
                title=f"🏆 {nom} a gagné !",
                description=afficher_grille(partie["grille"]),
                color=0x00FF00
            )
            embed.add_field(name="🎉 Bravo !", value=f"{jeton} **{nom}** remporte la partie !", inline=False)
            await ctx.send(embed=embed)
            del self.parties[cid]
            return

        if grille_pleine(partie["grille"]):
            embed = discord.Embed(title="🤝 Match nul !", description=afficher_grille(partie["grille"]), color=0x888888)
            await ctx.send(embed=embed)
            del self.parties[cid]
            return

        await self.afficher_tour(ctx)

    @commands.command(name="abandon")
    async def abandon(self, ctx):
        """Abandonne la partie de Puissance 4 en cours"""
        cid = self.get_channel_id(ctx)

        if cid not in self.parties:
            await ctx.send("❌ Pas de partie en cours ici.")
            return

        partie = self.parties[cid]
        if ctx.guild and ctx.author not in partie["joueurs"]:
            await ctx.send("❌ Tu ne participes pas à cette partie !")
            return

        del self.parties[cid]
        await ctx.send(f"🏳️ **{ctx.author.display_name}** a abandonné. Partie terminée.")

    @jouer.error
    async def jouer_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("❌ Utilisation : `!jouer <colonne>` (ex: `!jouer 4`)")
        elif isinstance(error, commands.BadArgument):
            await ctx.send("❌ La colonne doit être un nombre entre 1 et 7.")

async def setup(bot):
    await bot.add_cog(Puissance4(bot))
