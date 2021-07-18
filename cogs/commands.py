import discord
from discord.ext import commands

from main import client


class Example(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.command()
    async def ping(self, ctx):
        await ctx.send(f'Pong! {round(client.latency*1000)}ms')


def setup(client):
    client.add_cog(Example(client))
