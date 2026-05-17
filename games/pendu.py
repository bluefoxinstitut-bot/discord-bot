import discord
from discord.ext import commands
import random

MOTS = {
    "Animaux": ["elephant", "girafe", "crocodile", "pingouin", "kangourou", "hippopotame", "rhinoceros", "chameleon", "perroquet", "dauphin"],
    "Pays": ["france", "allemagne", "australie", "bresil", "argentine", "japon", "mexique", "portugal", "egypte", "turquie"],
    "Fruits": ["framboise", "pastèque", "mangue", "ananas", "cerise", "grenade", "papaye", "litchi", "abricot", "prune"],
    "Sports": ["basketball", "volleyball", "natation", "cyclisme", "escrime", "handball", "badminton", "karate", "baseball", "rugby"],
    "Manga": ["naruto", "sasuke", "goku", "luffy", "ichigo", "edward", "lelouch", "gintoki", "killua", "meliodas"],
}

DESSINS = [
    "```\n  +---+\n  |   |\n      |\n      |\n      |\n      |\n=========```",
    "```\n  +---+\n  |   |\n  O   |\n      |\n      |\n      |\n=========```",
    "```\n  +---+\n  |   |\n  O   |\n  |   |\n      |\n      |\n=========```",
    "```\n  +---+\n  |   |\n  O   |\n /|   |\n      |\n      |\n=========```",
    "```\n  +---+\n  |   |\n  O   |\n /|\\  |\n      |\n      |\n=========```",
    "```\n  +---+\n  |   |\n  O   |\n /|\\  |\n /    |\n      |\n=========```",
    "```\n  +---+\n  |   |\n  O   |\n /|\\  |\n / \\  |\n      |\n=========```",
]

MAX_ERREURS = len(DESSINS) - 1

class Pendu(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.parties = {}

    @commands.command(name="pendu", aliases=["hangman"])
    async def pendu(self, ctx, categorie: str = None):
        """Lance une partie de Pendu ! !pendu ou !pendu <categorie>"""
        uid = ctx.author.id

        if uid in self.parties:
            await ctx.send("❌ Tu as déjà une partie en cours ! Tape `!lettre <lettre>` ou `!motentier <mot>`.")
            return

        if categorie:
            cat = next((c for c in MOTS if categorie.lower() in c.lower()), None)
            if not cat:
                cats = ", ".join(MOTS.keys())
                await ctx.send(f"❌ Catégorie introuvable ! Choisis parmi : **{cats}**")
                return
        else:
            cat = random.choice(list(MOTS.keys()))

        mot = random.choice(MOTS[cat])

        self.parties[uid] = {
            "mot": mot,
            "categorie": cat,
            "lettres_trouvees": set(),
            "mauvaises_lettres": set(),
            "erreurs": 0,
        }

        await self.afficher_pendu(ctx)

    async def afficher_pendu(self, ctx):
        uid = ctx.author.id
        partie = self.parties.get(uid)
        if not partie:
            return

        mot = partie["mot"]
        trouvees = partie["lettres_trouvees"]
        mauvaises = partie["mauvaises_lettres"]
        erreurs = partie["erreurs"]

        # Afficher le mot avec les lettres trouvées
        mot_affiche = " ".join(l if l in trouvees else "\_" for l in mot)

        embed = discord.Embed(
            title=f"🪢 Pendu — {partie['categorie']}",
            description=DESSINS[erreurs],
            color=0xFF6B35
        )
        embed.add_field(name="Mot", value=f"**{mot_affiche}**", inline=False)

        if mauvaises:
            embed.add_field(name="❌ Mauvaises lettres", value=" ".join(sorted(mauvaises)), inline=False)

        embed.add_field(name="Vies restantes", value=f"{'❤️' * (MAX_ERREURS - erreurs)}{'🖤' * erreurs}", inline=False)
        embed.set_footer(text="!lettre <a-z> pour proposer une lettre • !motentier <mot> pour deviner le mot")
        await ctx.send(embed=embed)

    @commands.command(name="lettre")
    async def lettre(self, ctx, lettre: str):
        """Propose une lettre pour le pendu"""
        uid = ctx.author.id

        if uid not in self.parties:
            await ctx.send("❌ Pas de partie en cours ! Lance-en une avec `!pendu`")
            return

        lettre = lettre.lower()[0]
        partie = self.parties[uid]
        mot = partie["mot"]

        if lettre in partie["lettres_trouvees"] or lettre in partie["mauvaises_lettres"]:
            await ctx.send(f"❌ Tu as déjà proposé la lettre **{lettre}** !", delete_after=5)
            return

        if lettre in mot:
            partie["lettres_trouvees"].add(lettre)
            # Vérifier si le mot est complet
            if all(l in partie["lettres_trouvees"] for l in mot):
                embed = discord.Embed(title="🎉 Bravo, tu as gagné !", color=0x00FF00)
                embed.add_field(name="Le mot était", value=f"**{mot.upper()}**", inline=False)
                embed.set_footer(text="Rejoue avec !pendu !")
                await ctx.send(embed=embed)
                del self.parties[uid]
                return
        else:
            partie["mauvaises_lettres"].add(lettre)
            partie["erreurs"] += 1

            if partie["erreurs"] >= MAX_ERREURS:
                embed = discord.Embed(title="💀 Tu as perdu !", description=DESSINS[-1], color=0xFF0000)
                embed.add_field(name="Le mot était", value=f"**{mot.upper()}**", inline=False)
                embed.set_footer(text="Rejoue avec !pendu !")
                await ctx.send(embed=embed)
                del self.parties[uid]
                return

        await self.afficher_pendu(ctx)

    @commands.command(name="motentier")
    async def mot_entier(self, ctx, *, mot: str):
        """Devine le mot entier pour le pendu"""
        uid = ctx.author.id

        if uid not in self.parties:
            await ctx.send("❌ Pas de partie en cours ! Lance-en une avec `!pendu`")
            return

        partie = self.parties[uid]
        if mot.lower() == partie["mot"]:
            embed = discord.Embed(title="🎉 Bravo, tu as trouvé !", color=0x00FF00)
            embed.add_field(name="Le mot était", value=f"**{partie['mot'].upper()}**", inline=False)
            embed.set_footer(text="Rejoue avec !pendu !")
            await ctx.send(embed=embed)
            del self.parties[uid]
        else:
            partie["erreurs"] += 1
            if partie["erreurs"] >= MAX_ERREURS:
                embed = discord.Embed(title="💀 Tu as perdu !", description=DESSINS[-1], color=0xFF0000)
                embed.add_field(name="Le mot était", value=f"**{partie['mot'].upper()}**", inline=False)
                await ctx.send(embed=embed)
                del self.parties[uid]
            else:
                await ctx.send(f"❌ Ce n'est pas **{mot}** ! Tu perds une vie.")
                await self.afficher_pendu(ctx)

    @commands.command(name="stoppendu")
    async def stop_pendu(self, ctx):
        """Abandonne la partie de pendu"""
        uid = ctx.author.id
        if uid not in self.parties:
            await ctx.send("❌ Pas de partie en cours !")
            return
        mot = self.parties[uid]["mot"]
        del self.parties[uid]
        await ctx.send(f"🏳️ Partie abandonnée ! Le mot était **{mot.upper()}**.")

async def setup(bot):
    await bot.add_cog(Pendu(bot))
