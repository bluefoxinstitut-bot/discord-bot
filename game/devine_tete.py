import discord
from discord.ext import commands
import random

PERSONNAGES = [
    {"nom": "Lionel Messi", "indices": ["Je suis footballeur", "Je suis argentin", "J'ai gagné la Coupe du Monde 2022", "Je jouais au FC Barcelone", "Je suis considéré comme l'un des meilleurs joueurs de tous les temps"]},
    {"nom": "Beyoncé", "indices": ["Je suis chanteuse", "Je suis américaine", "J'ai fait partie d'un girls group", "Mon mari est un rappeur célèbre", "J'ai sorti l'album 'Lemonade'"]},
    {"nom": "Elon Musk", "indices": ["Je suis entrepreneur", "J'ai fondé une entreprise de voitures électriques", "J'ai racheté un réseau social", "Je veux coloniser Mars", "Je suis l'une des personnes les plus riches du monde"]},
    {"nom": "Harry Potter", "indices": ["Je suis un personnage fictif", "Je suis sorcier", "J'ai une cicatrice en forme d'éclair", "Mon ennemi s'appelle Voldemort", "Je vais à l'école Poudlard"]},
    {"nom": "Marie Curie", "indices": ["Je suis scientifique", "Je suis une femme", "J'ai découvert deux éléments chimiques", "Je suis d'origine polonaise", "J'ai été la première femme à gagner un Prix Nobel"]},
    {"nom": "Cristiano Ronaldo", "indices": ["Je suis footballeur", "Je suis portugais", "Mon surnom est CR7", "J'ai joué à Manchester United et au Real Madrid", "Je suis rival d'un joueur argentin"]},
    {"nom": "Rihanna", "indices": ["Je suis chanteuse", "Je viens des Caraïbes", "J'ai une marque de cosmétiques", "J'ai chanté à la mi-temps du Super Bowl", "Mon vrai prénom est Robyn"]},
    {"nom": "Albert Einstein", "indices": ["Je suis scientifique", "Je suis mort", "J'ai une théorie sur la relativité", "Je suis né en Allemagne", "Ma photo avec la langue tirée est célèbre"]},
    {"nom": "Naruto Uzumaki", "indices": ["Je suis un personnage de manga", "Je suis un ninja", "J'ai un renard à 9 queues en moi", "Je mange des ramen tout le temps", "Mon rêve est de devenir Hokage"]},
    {"nom": "Adele", "indices": ["Je suis chanteuse", "Je suis britannique", "Mes albums sont numérotés selon mon âge", "Ma chanson 'Hello' est mondiale", "J'ai une voix très puissante"]},
    {"nom": "Barack Obama", "indices": ["Je suis politicien", "Je suis américain", "J'ai été président", "J'ai reçu le Prix Nobel de la Paix", "J'ai été le premier président afro-américain des États-Unis"]},
    {"nom": "Hermione Granger", "indices": ["Je suis un personnage fictif", "Je suis sorcière", "Je suis la meilleure élève de ma classe", "J'ai deux amis très proches", "Je suis dans le roman Harry Potter"]},
    {"nom": "Neymar Jr", "indices": ["Je suis footballeur", "Je suis brésilien", "J'ai joué au PSG", "Je suis connu pour mes dribbles", "J'ai été transféré pour 222 millions d'euros"]},
    {"nom": "Taylor Swift", "indices": ["Je suis chanteuse", "Je suis américaine", "Je suis connue pour mes ruptures en chanson", "Mes fans s'appellent les Swifties", "J'ai sorti l'album 'Folklore'"]},
    {"nom": "Mickey Mouse", "indices": ["Je suis un personnage fictif", "Je suis un animal", "Je porte des gants blancs", "J'ai de grandes oreilles rondes", "Je suis la mascotte de Disney"]},
    {"nom": "Leonardo DiCaprio", "indices": ["Je suis acteur", "Je suis américain", "J'ai mis longtemps à avoir un Oscar", "J'ai joué dans Titanic", "Je suis écologiste"]},
    {"nom": "Goku", "indices": ["Je suis un personnage de manga", "Je suis un guerrier extraterrestre", "Je peux transformer mes cheveux en doré", "Ma série s'appelle Dragon Ball", "Ma technique signature s'appelle le Kamehameha"]},
    {"nom": "Shakira", "indices": ["Je suis chanteuse", "Je suis colombienne", "Je suis connue pour ma danse du ventre", "J'ai été en couple avec un footballeur espagnol", "Ma chanson 'Waka Waka' était pour la Coupe du Monde"]},
    {"nom": "Steve Jobs", "indices": ["Je suis un entrepreneur", "Je suis décédé", "J'ai co-fondé une entreprise d'informatique très connue", "J'aimais porter des cols roulés noirs", "J'ai créé l'iPhone"]},
    {"nom": "Luffy", "indices": ["Je suis un personnage de manga", "Je suis pirate", "J'ai mangé un fruit du démon", "Mon rêve est de devenir Roi des Pirates", "Ma série s'appelle One Piece"]},
]

MAX_QUESTIONS = 10

class DevineTete(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.parties = {}  # user_id -> état de la partie

    def get_player_id(self, ctx):
        """Retourne un ID unique pour suivre la partie (fonctionne en MP et serveur)"""
        return ctx.author.id

    @commands.command(name="devine", aliases=["devinelatete", "whoisit"])
    async def devine(self, ctx, membre: discord.Member = None):
        """Lance une partie de Devine la Tête"""
        # En MP, impossible de mentionner quelqu'un, donc toujours solo
        devineur = (membre if membre and ctx.guild else None) or ctx.author
        pid = devineur.id

        if pid in self.parties:
            await ctx.send(f"❌ **{devineur.display_name}** a déjà une partie en cours ! Tape `!reponse <nom>` ou `!passedevine`.")
            return

        perso = random.choice(PERSONNAGES)

        self.parties[pid] = {
            "personnage": perso,
            "indice_actuel": 1,
            "questions": 0,
            "channel_id": ctx.channel.id,
            "devineur_id": devineur.id,
        }

        embed = discord.Embed(
            title="🤔 Devine la Tête !",
            description=f"**{devineur.display_name}** doit deviner le personnage mystère !",
            color=0x9B59B6
        )
        embed.add_field(
            name="📋 Règles",
            value=f"• Tu as **{MAX_QUESTIONS} tentatives** max\n• `!indice` → indice supplémentaire\n• `!reponse <nom>` → tenter une réponse\n• `!passedevine` → abandonner",
            inline=False
        )
        embed.add_field(
            name="🔍 Indice 1",
            value=f"*{perso['indices'][0]}*",
            inline=False
        )
        embed.set_footer(text=f"0/{MAX_QUESTIONS} tentatives utilisées")
        await ctx.send(embed=embed)

    @commands.command(name="indice")
    async def indice(self, ctx):
        """Demande un indice supplémentaire"""
        pid = self.get_player_id(ctx)

        if pid not in self.parties:
            await ctx.send("❌ Tu n'as pas de partie en cours ! Lance-en une avec `!devine`")
            return

        partie = self.parties[pid]
        i = partie["indice_actuel"]
        perso = partie["personnage"]

        if i >= len(perso["indices"]):
            await ctx.send("💡 Tu as déjà tous les indices ! Tente ta chance avec `!reponse <nom>`")
            return

        partie["indice_actuel"] += 1
        partie["questions"] += 1

        embed = discord.Embed(
            title=f"💡 Indice {i + 1}/{len(perso['indices'])}",
            description=f"*{perso['indices'][i]}*",
            color=0xF39C12
        )
        embed.set_footer(text=f"{partie['questions']}/{MAX_QUESTIONS} tentatives utilisées")
        await ctx.send(embed=embed)

        if partie["questions"] >= MAX_QUESTIONS:
            await ctx.send(f"⏰ Plus de tentatives ! C'était **{perso['nom']}**. Dommage ! 😢\nRetente avec `!devine` !")
            del self.parties[pid]

    @commands.command(name="reponse", aliases=["guess"])
    async def reponse(self, ctx, *, proposition: str):
        """Propose une réponse pour Devine la Tête"""
        pid = self.get_player_id(ctx)

        if pid not in self.parties:
            await ctx.send("❌ Tu n'as pas de partie en cours ! Lance-en une avec `!devine`")
            return

        partie = self.parties[pid]
        perso = partie["personnage"]
        bonne_reponse = perso["nom"].lower().strip()
        tentative = proposition.lower().strip()

        # Vérification flexible : prénom OU nom complet
        mots_reponse = bonne_reponse.split()
        if tentative == bonne_reponse or tentative in mots_reponse:
            embed = discord.Embed(
                title="🎉 BRAVO, tu as trouvé !",
                description=f"C'était bien **{perso['nom']}** !",
                color=0x00FF00
            )
            embed.add_field(
                name="📊 Stats",
                value=f"Indices utilisés : {partie['indice_actuel']}/{len(perso['indices'])}\nTentatives : {partie['questions']}/{MAX_QUESTIONS}",
                inline=False
            )
            embed.set_footer(text="Rejoue avec !devine !")
            await ctx.send(embed=embed)
            del self.parties[pid]
        else:
            partie["questions"] += 1
            restantes = MAX_QUESTIONS - partie["questions"]

            embed = discord.Embed(
                title="❌ Raté !",
                description=f"Ce n'est pas **{proposition}**...",
                color=0xFF0000
            )

            if restantes <= 0:
                embed.add_field(name="💀 Game Over", value=f"C'était **{perso['nom']}** ! Rejoue avec `!devine` !", inline=False)
                await ctx.send(embed=embed)
                del self.parties[pid]
            else:
                embed.set_footer(text=f"Il te reste {restantes} tentative(s). Tape !indice pour un indice !")
                await ctx.send(embed=embed)

    @commands.command(name="passedevine")
    async def passe(self, ctx):
        """Abandonne la partie Devine la Tête"""
        pid = self.get_player_id(ctx)

        if pid not in self.parties:
            await ctx.send("❌ Tu n'as pas de partie en cours !")
            return

        perso = self.parties[pid]["personnage"]
        del self.parties[pid]
        await ctx.send(f"🏳️ Partie abandonnée ! C'était **{perso['nom']}**.\nRetente avec `!devine` !")

    @reponse.error
    async def reponse_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("❌ Utilisation : `!reponse <nom du personnage>`")

async def setup(bot):
    await bot.add_cog(DevineTete(bot))
