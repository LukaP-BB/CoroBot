#!/usr/bin/env python3
#-*- coding:utf-8 -*-
import discord
from discord.ext import commands

import interface as itf

"""
Bot discord basé sur les données hospitalieres du covid disponibles sur data.gouv.fr

exemples d'utilisation :
    +Coro Indre 08-2020 09-2020
    +Coro Indre 08-2020
    +Coro 36
    +Coro Île-de-France
    +Coro help
    +Coro départements (départements/dep)
"""

bot = commands.Bot(command_prefix='!')

@bot.event
async def on_ready():
    print("CoroBot connecté")
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="!coro help"))

@bot.command(hidden=True)
async def exit(ctx):
    if ctx.author.id == 404395089389944832 :
        await ctx.send("Fermeture du CoroBot...")
        print("CoroBot fermé avec succès")
        await bot.close()
    else :
        await ctx.send("nope")


#******************************************************************************
@bot.command()
async def aide(ctx):
    await ctx.send(itf.help_message)

@commands.cooldown(1, 5, commands.BucketType.guild)
@bot.command(help="Pour tous les détails de cette commande, utilise !aide")
async def coro(ctx, *args):
    args = itf.parseArgs(args)

    if args["type"] == "help" :
        await ctx.send(itf.help_message)

    elif args["type"] == "dep" :
        await ctx.message.author.send(itf.sendDeps())
        await ctx.send(f"Je t'ai envoyé la liste des département en message privé {ctx.author.mention}")

    elif args["type"] == "plot" :
        async with ctx.channel.typing():
            infos = itf.plotFromArgs(args)
            file = discord.File("fig.jpg")
            embed = discord.Embed(
                title=infos["Titre"],
                description=infos["Description"],
                colour=discord.Colour.magenta())
            embed.set_image(url="attachment://fig.jpg")
            if len(infos["Erreurs"]) > 0 :
                for info in infos["Erreurs"] :
                    embed.add_field(name="Information : ", value=info)
            await ctx.send(file=file, embed=embed)

@coro.error
async def coro_error(ctx, error):
    if isinstance(error, commands.errors.CommandOnCooldown) :
        await ctx.send(f"Minute papillon, laisses moi quelques secondes ! :rage: {ctx.author.mention}")
    else :
        with open("id.txt", "r") as idtxt :
            id = int(idtxt.read())
        MYSELF = bot.get_user(id)
        await MYSELF.send(f"Une erreur non anticipée est advenue : \n'{error}'\n\
Serv : {ctx.guild.name}\n\
Salon : {ctx.channel.mention}")

#******************************************************************************
with open("token.txt", "r") as token :
    t = token.read()
bot.run(t)
