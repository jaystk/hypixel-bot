import discord
from discord.ext import commands
import discord.utils 
import asyncio
from discord import app_commands
import requests
from minecraft_utils import minecraftSKin
import io
import requests
from datetime import datetime, timedelta

api_key = "f1d8278e-47fd-4ee9-ab01-d78ce73087c9"


def getInfo(call):
    response = requests.get(call)
    return response.json()

def UsernameToID(username):
    mojang_url = f"https://api.mojang.com/users/profiles/minecraft/{username}"
    uuid = getInfo(mojang_url)
    return uuid['id']


def format_username(username):
    mojang_url = f"https://api.mojang.com/users/profiles/minecraft/{username}"
    formatted_username = getInfo(mojang_url)
    return formatted_username['name']





class Menu(discord.ui.View):
    skin_url = None

    def __init__(self, username):
        super().__init__()

        self.username = username
        self.online = False
        self.loop_task = None

    @discord.ui.button(label="Stop", style=discord.ButtonStyle.red)
    async def menu1(self, interaction: discord.Interaction, button: discord.ui.Button):
        
        if self.loop_task:
            self.loop_task.cancel()
            self.online = False
        embed = discord.Embed(title="Monitor Command",
                      description=f"*No longer tracking ``{self.username}``. Please reinitialize command to begin tracking again.*",
                      colour=0x00b0f4,
                      timestamp=datetime.now())
        
        embed.set_thumbnail(url=minecraftSKin(UsernameToID(self.username)))
        self.clear_items()
        await interaction.followup.send(embed=embed, view = self)
        
  

            



    @discord.ui.button(label="Start", style=discord.ButtonStyle.green)
    async def menu2(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not self.online:
            self.online = True
            button.disabled = True
            self.loop_task = asyncio.create_task(self.check_online_status(interaction))
        embed = discord.Embed(title="Monitor Command",
                      description=f"*``{self.username}`` is currently afk on Skyblock*",
                      colour=0x00b0f4,
                      timestamp=datetime.now())
        
        embed.set_thumbnail(url=minecraftSKin(UsernameToID(self.username)))
        embed.add_field(name = "Next Update", value = f"{(datetime.now() + timedelta(minutes = 10)).strftime('%I:%M%p').lstrip('0')}")
        await interaction.response.edit_message(embed = embed, view = self)

            
            

    async def check_online_status(self, interaction: discord.Interaction):
        while self.online:
            url = f"https://api.hypixel.net/status?key={api_key}&uuid={UsernameToID(self.username)}"
            data = getInfo(url)
            online = data.get("session", {}).get("gameType")
            if online == "SKYBLOCK":
                self.online = True
            else:
                self.online = False
                await self.not_online(interaction, online)

            embed = discord.Embed(title="Monitor Command",
                    description=f"*``{self.username}`` is currently afk on Skyblock*",
                    colour=0x00b0f4,
                    timestamp=datetime.now())
            embed.set_thumbnail(url=minecraftSKin(UsernameToID(self.username)))
            embed.insert_field_at(index = 0, name="Next Update", value=f"{(datetime.now() + timedelta(minutes = 10)).strftime('%I:%M%p').lstrip('0')}")
            message = await interaction.original_response()
            await message.edit(embed=embed)

            await asyncio.sleep(600)




    async def not_online(self, interaction: discord.Interaction, online):
        embed = discord.Embed(title="Monitor Command",
                      description=f"*``{self.username}``   is currently not online. Now tagging: ``{interaction.user}``. Click \"**Stop**\" when returned from AFK.*",
                      colour=0x00b0f4,
                      timestamp=datetime.now())
        embed.set_author(name=f"{interaction.user}")
        embed.set_thumbnail(url=minecraftSKin(UsernameToID(self.username)))
        message = await interaction.original_response()
        await message.edit(embed=embed)

        while not online:
            for _ in range(1):
                await interaction.channel.send(interaction.user.mention)
            await asyncio.sleep(600)
        




class afkchecks(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @app_commands.command(
            name = "monitor",
            description = "Monitors a specified user on Skyblock"
            )
    async def check_if_user_is_on(self, interaction: discord.Interaction, username: str):
        username = format_username(username)

        view = Menu(username)


        embed = discord.Embed(title="Command Info",
                      description=f"*Monitors ``{username}`` for AFK status in the \"skyblock\" at 10-minute intervals. If the user remains AFK in skyblock , no output will be generated. In the event that the user is not present in the skyblock during a monitoring cycle, the interacting user will be subject to receiving 10 spam tags every 5 minutes.*",
                      colour=0x00b0f4,
                      timestamp=datetime.now())
        
        embed.add_field(name="Start Monitoring", value=f"Click on \"**Start**\" to start monitoring ``{username}``")
        

        embed.set_author(name=f"{interaction.user}")
        embed.set_thumbnail(url=minecraftSKin(UsernameToID(username)))
        await interaction.response.send_message(embed=embed, view=view, ephemeral = True)







    





async def setup(bot):
    await bot.add_cog(afkchecks(bot))
