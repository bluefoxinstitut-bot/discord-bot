import discord
from discord.ext import commands
import asyncio

VIDE = "⬜"
X = "❌"
O = "⭕"

POSITIONS = ["1️⃣","2️⃣","3️⃣","4️⃣","5️⃣","6️⃣","7️⃣","8️⃣","9️⃣"]

def creer_grille():
    return [VIDE] * 9

def afficher_grille(grille):
    lignes = []
    for i in range(0, 9, 3):
        lignes.append("".join(grille[i:i+3]))
    return "\n".join(lignes)

def verifier_victoire(grille, symbole):
    combos = [
        [0,1,2],[3,4,5],[6,7,8],  # lignes
        [0,3,6],[1,4,7],[2,5,8],  # colonnes
        [0,4,8],[2,4,6]           # diagonales
    ]
    return any(all(grille[i] == symbole for i in combo) for combo in combos)

def grille_pleine(grille):
    return all(c != VIDE for c in grille)

def coup_bot(grille):
    """IA simple pour le morpion"""
    # Gagner
    for i in range(9):
        if grille[i] == VIDE:
            grille[i] = O
            if verifier_victoire(grille, O):
                grille[i] = VIDE
                return i
            grille[i] = VIDE
    # Bloquer
    for i in range(9):
        if grille[i] == VIDE:
            grille[i] = X
            if verifier_victoire(grille, X):
                grille[i] = VIDE
                return i
            grille[i] = VIDE
    # Centre
    if grille[4] == VIDE:
        return 4
    # Coin
    for i in [0, 2, 6, 8]:
        if grille[i] == VIDE:
            return i
    # N'importe
    for i in range(9):
        if grille[i] == VIDE:
            return i

class Morpion(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.parties = {}

    def get_id(self, ctx):
        return ctx.channel.id if ctx.guild else ctx.author.id

    @commands.command(name="morpion", aliases=["ttt", "tictactoe"])
    async def morpion(self, ctx, adversaire: discord.Member = None):
        """Lance une partie de Morpion ! !morpion ou !morpion @adversaire"""
        cid = self.get_id(ctx)

        if cid in self.parties:
            await ctx.send("❌ Une partie est déjà en cours ! Utilise `!stopmorpion` pour l'arrêter.")
            return

        solo = adversaire is None or adversaire.bot

        if not solo:
            if adversaire == ctx.author:
                await ctx.send("❌ Tu ne peux pas jouer contre toi-même !")
                return

            embed = discord.Embed(
                title="❌⭕ Morpion !",
                description=f"{adversaire.mention}, **{ctx.author.display_name}** te défie ! (`oui` / `non`)",
                color=0x9B59B6
            )
            await ctx.send(embed=embed)

            def check(m):
                return m.author == adversaire and m.channel == ctx.channel and m.content.lower() in ["oui", "non"]

            try:
                msg = await self.bot.wait_for("message", check=check, timeout=30)
                if msg.content.lower() == "non":
                    await ctx.send(f"😢 {adversaire.display_name} a refusé !")
                    return
            except asyncio.TimeoutError:
                await ctx.send("⏰ Pas de réponse, partie annulée !")
                return

        self.parties[cid] = {
            "grille": creer_grille(),
            "joueurs": [ctx.author, adversaire],
            "symboles": [X, O],
            "tour": 0,
            "solo": solo,
        }

        await self.afficher_tour(ctx)

    async def afficher_tour(self, ctx):
        cid = self.get_id(ctx)
        partie = self.parties.get(cid)
        if not partie:
            return

        tour = partie["tour"] % 2
        joueur = partie["joueurs"][tour]
        symbole = partie["symboles"][tour]
        grille = partie["grille"]

        # Remplacer les cases vides par les numéros
        affichage = []
        num = 0
        for case in grille:
            if case == VIDE:
                affichage.append(POSITIONS[num])
                num += 1
            else:
                affichage.append(case)
                num += 1

        lignes = []
        for i in range(0, 9, 3):
            lignes.append("".join(affichage[i:i+3]))
        grille_str = "\n".join(lignes)

        nom = joueur.display_name if joueur else "Bot"
        embed = discord.Embed(title="❌⭕ Morpion", description=grille_str, color=0x9B59B6)
        embed.add_field(name=f"Tour de {symbole} {nom}", value="Tape `!case <1-9>` pour jouer", inline=False)
        embed.set_footer(text="!stopmorpion pour abandonner")
        await ctx.send(embed=embed)

        # Tour du bot
        if partie["solo"] and tour == 1:
            import asyncio
            await asyncio.sleep(1)
            coup = coup_bot(grille)
            grille[coup] = O
            partie["tour"] += 1

            if verifier_victoire(grille, O):
                await ctx.send(f"❌⭕\n{afficher_grille(grille)}\n\n🤖 **Le Bot gagne !** Dommage ! Retente avec `!morpion` !")
                del self.parties[cid]
                return
            if grille_pleine(grille):
                await ctx.send(f"❌⭕\n{afficher_grille(grille)}\n\n🤝 **Match nul !**")
                del self.parties[cid]
                return

            await self.afficher_tour(ctx)

    @commands.command(name="case")
    async def jouer_case(self, ctx, position: int):
        """Joue sur une case du morpion (1-9)"""
        cid = self.get_id(ctx)

        if cid not in self.parties:
            await ctx.send("❌ Pas de partie en cours ! Lance-en une avec `!morpion`")
            return

        partie = self.parties[cid]
        tour = partie["tour"] % 2
        joueur_actuel = partie["joueurs"][tour]

        if ctx.guild and not partie["solo"] and ctx.author != joueur_actuel:
            await ctx.send(f"⛔ C'est au tour de **{joueur_actuel.display_name}** !", delete_after=5)
            return

        if not (1 <= position <= 9):
            await ctx.send("❌ Choisis une case entre 1 et 9 !", delete_after=5)
            return

        idx = position - 1
        grille = partie["grille"]

        if grille[idx] != VIDE:
            await ctx.send("❌ Cette case est déjà prise !", delete_after=5)
            return

        symbole = partie["symboles"][tour]
        grille[idx] = symbole
        partie["tour"] += 1
        nom = ctx.author.display_name

        if verifier_victoire(grille, symbole):
            embed = discord.Embed(
                title=f"🏆 {nom} gagne !",
                description=afficher_grille(grille),
                color=0x00FF00
            )
            embed.set_footer(text="Rejoue avec !morpion !")
            await ctx.send(embed=embed)
            del self.parties[cid]
            return

        if grille_pleine(grille):
            embed = discord.Embed(title="🤝 Match nul !", description=afficher_grille(grille), color=0x888888)
            await ctx.send(embed=embed)
            del self.parties[cid]
            return

        await self.afficher_tour(ctx)

    @commands.command(name="stopmorpion")
    async def stop(self, ctx):
        """Arrête la partie de morpion"""
        cid = self.get_id(ctx)
        if cid not in self.parties:
            await ctx.send("❌ Pas de partie en cours !")
            return
        del self.parties[cid]
        await ctx.send(f"🏳️ Partie arrêtée par **{ctx.author.display_name}**.")

    @jouer_case.error
    async def case_error(self, ctx, error):
        if isinstance(error, (commands.MissingRequiredArgument, commands.BadArgument)):
            await ctx.send("❌ Utilisation : `!case <1-9>` (ex: `!case 5`)")

async def setup(bot):
    await bot.add_cog(Morpion(bot))
