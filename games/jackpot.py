import discord
from discord.ext import commands
import random

SYMBOLES = ["🍒", "🍋", "🍊", "🍇", "⭐", "💎", "7️⃣"]

GAINS = {
    "💎💎💎": ("JACKPOT DIAMANT", 1000),
    "7️⃣7️⃣7️⃣": ("JACKPOT LUCKY 7", 777),
    "⭐⭐⭐": ("JACKPOT ÉTOILE", 500),
    "🍒🍒🍒": ("TRIO CERISE", 300),
    "🍇🍇🍇": ("TRIO RAISIN", 200),
    "🍊🍊🍊": ("TRIO ORANGE", 150),
    "🍋🍋🍋": ("TRIO CITRON", 100),
}

class Jackpot(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.coins = {}  # user_id -> coins

    def get_coins(self, user_id):
        return self.coins.get(user_id, 100)

    def set_coins(self, user_id, amount):
        self.coins[user_id] = max(0, amount)

    @commands.command(name="jackpot", aliases=["slot", "machine"])
    async def jackpot(self, ctx, mise: int = 10):
        """Lance la machine à sous ! !jackpot <mise>"""
        uid = ctx.author.id
        solde = self.get_coins(uid)

        if mise < 1:
            await ctx.send("❌ La mise minimum est de **1 coin** !")
            return
        if mise > solde:
            await ctx.send(f"❌ Tu n'as que **{solde} coins** ! Tape `!coins` pour voir ton solde.")
            return

        # Lancer les rouleaux
        rouleaux = [random.choice(SYMBOLES) for _ in range(3)]
        resultat = "".join(rouleaux)

        # Vérifier les gains
        gain = 0
        message_gain = ""
        for combo, (nom, multiplicateur) in GAINS.items():
            if resultat == combo:
                gain = mise * multiplicateur // 10
                message_gain = f"🎉 **{nom}** ! +{gain} coins !"
                break

        # Deux identiques
        if gain == 0:
            if rouleaux[0] == rouleaux[1] or rouleaux[1] == rouleaux[2] or rouleaux[0] == rouleaux[2]:
                gain = mise // 2
                message_gain = f"😊 Paire ! +{gain} coins !"
            else:
                gain = -mise
                message_gain = f"😢 Perdu ! -{mise} coins !"

        nouveau_solde = solde + gain
        self.set_coins(uid, nouveau_solde)

        couleur = 0x00FF00 if gain > 0 else 0xFF0000
        embed = discord.Embed(title="🎰 Machine à Sous", color=couleur)
        embed.add_field(name="Rouleaux", value=f"**{rouleaux[0]} | {rouleaux[1]} | {rouleaux[2]}**", inline=False)
        embed.add_field(name="Résultat", value=message_gain, inline=False)
        embed.add_field(name="💰 Solde", value=f"{nouveau_solde} coins", inline=False)
        embed.set_footer(text=f"Mise : {mise} coins • !jackpot <mise> pour rejouer")
        await ctx.send(embed=embed)

    @commands.command(name="coins", aliases=["solde", "balance"])
    async def voir_coins(self, ctx):
        """Voir ton solde de coins"""
        solde = self.get_coins(ctx.author.id)
        embed = discord.Embed(title="💰 Ton Solde", color=0xFFD700)
        embed.add_field(name=f"{ctx.author.display_name}", value=f"**{solde} coins**", inline=False)
        embed.set_footer(text="!jackpot <mise> pour jouer • !daily pour gagner des coins")
        await ctx.send(embed=embed)

    @commands.command(name="daily")
    async def daily(self, ctx):
        """Récupère tes coins quotidiens"""
        uid = ctx.author.id
        gain = random.randint(50, 150)
        solde = self.get_coins(uid) + gain
        self.set_coins(uid, solde)

        embed = discord.Embed(title="🎁 Coins Quotidiens !", color=0x00FF00)
        embed.add_field(name="Gain", value=f"+**{gain} coins** !", inline=False)
        embed.add_field(name="💰 Nouveau Solde", value=f"{solde} coins", inline=False)
        await ctx.send(embed=embed)

    @jackpot.error
    async def jackpot_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            await ctx.send("❌ Utilisation : `!jackpot <mise>` (ex: `!jackpot 50`)")

async def setup(bot):
    await bot.add_cog(Jackpot(bot))
