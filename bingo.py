import discord
from discord.ext import commands
import discord.utils 
import asyncio
from discord import app_commands
import requests
from minecraft_utils import minecraftSKin
import io
import requests
from datetime import datetime
import re
import json

def remove_minecraft_formatting(text):
    return re.sub(r'§[0-9a-fklmnor]', '', text)

class PaginationView(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.current_page = 1
        self.sept = 1 

    async def send(self, interaction: discord.Interaction):
        self.message = await interaction.response.send_message(embed=self.create_embed(), view=self, ephemeral = True)


    def create_embed(self):
        embed = discord.Embed(title="Bingo Goals")

        if self.data and 0 <= self.current_page - 1 < len(self.data):
            goal = self.data[self.current_page - 1]  # Get the current goal for this page

            goal_name = goal.get("name", "N/A")
            goal_lore = goal.get("lore")
            goal_tiers = goal.get("tiers", [])
            goal_progress = goal.get("progress")
            goal_requiredamount = goal.get("requiredAmount")
            embed.add_field(name="Goal Name:", value=goal_name, inline=False)

            if goal_lore:
                embed.add_field(name="Goal Lore:", value=remove_minecraft_formatting(goal_lore), inline=False)

            if goal_tiers:
                tiers_text = "\n".join(map(str, goal_tiers))
                embed.add_field(name="Goal Tiers:", value=tiers_text, inline=False)

            if goal_progress is not None:
                embed.add_field(name="Goal Progress:", value=goal_progress, inline=False)

            if goal_requiredamount is not None:
                embed.add_field(name="required amount:", value=goal_requiredamount, inline=False)
        else:
            embed.description = "No goals available."

        return embed



    @discord.ui.button(label="<<", style=discord.ButtonStyle.primary)
    async def first_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        self.current_page = 1
        await self.update_message(interaction)

    @discord.ui.button(label="<", style=discord.ButtonStyle.primary)
    async def prev_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        self.current_page -= 1
        if self.current_page < 1:
            self.current_page = 1
        await self.update_message(interaction)

    @discord.ui.button(label=">", style=discord.ButtonStyle.primary)
    async def next_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        self.current_page += 1
        if self.current_page > len(self.data):
            self.current_page = len(self.data)
        await self.update_message(interaction)

    @discord.ui.button(label=">>", style=discord.ButtonStyle.primary)
    async def last_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        last_page = (len(self.data) + self.sept - 1) // self.sept  # Calculate the last valid page
        if last_page < 1:
            last_page = 1
        self.current_page = last_page
        await self.update_message(interaction)

    async def update_message(self, interaction: discord.Interaction):
        self.update_buttons()
        await interaction.edit_original_response(embed=self.create_embed(), view=self)

    def update_buttons(self):
        if self.current_page == 1:
            self.first_button.disabled = True
            self.prev_button.disabled = True
        else:
            self.first_button.disabled = False
            self.prev_button.disabled = False

        if self.current_page == (len(self.data) + self.sept - 1) // self.sept:
            self.next_button.disabled = True
            self.last_button.disabled = True
        else:
            self.next_button.disabled = False
            self.last_button.disabled = False











class bingo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot



    @app_commands.command(
            name = "bin",
            description = "The current election"
            )
    

    async def paginate(self, interaction: discord.Interaction):
        url = "https://api.hypixel.net/resources/skyblock/bingo"
        data = self.get_info(url)
        self.data = data.get("goals", [])

        pagination_view = PaginationView()
        pagination_view.data = self.data
        await pagination_view.send(interaction)

    def get_info(self, call):
        response = requests.get(call)
        return response.json()


    





async def setup(bot):
    await bot.add_cog(bingo(bot))
