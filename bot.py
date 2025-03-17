
import os

import discord
from discord.ext import commands
import random
import re
from discord.app_commands import CommandOnCooldown
import time
import requests
from discord.app_commands import tree
from datetime import datetime, timedelta
from discord.ui import View, Select
import asyncio
import webserver

import webserver


DISCORD_TOKEN = os.environ['discordkey']
bot = commands.Bot(command_prefix="$", intents=discord.Intents.all())

@bot.event 
async def on_ready():
    await bot.change_presence(status=discord.Status.online, activity=discord.Activity(type=discord.ActivityType.watching, name="BHC server"))
    print("Bot is up and ready!")
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} commands(s)")
    except Exception as e:
        print(e)

    
@bot.event
async def on_command(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        msg = "** still on cooldown** please try again in {:.2f}".format(error.retry_after)
        await ctx.send(msg)



@bot.tree.command(name="ban", description="Bans a member")
@commands.has_permissions(ban_members=True)
async def ban(interaction: discord.Interaction, member: discord.Member, reason: str):
    try:
        await member.ban(reason=reason)

        embed = discord.Embed(
            title=f"{member.name} has been banned",
            description=f"{member.mention} has been banned from the server",
            color=discord.Color.red()
        )

        embed.add_field(name="Reason:", value=reason, inline=True)
        embed.add_field(name="Banned By:", value=interaction.user.name, inline=True)
        embed.set_thumbnail(url=member.avatar.url)
        embed.set_footer(text=f"User Id: {member.id}")

        await interaction.response.send_message(embed=embed, ephemeral=True)

    except discord.Forbidden:
        await interaction.response.send_message("I dont have permission to ban this member")
    except discord.HTTPException as e:
        await interaction.response.send_message(f"An error occured: {e}")


@bot.tree.context_menu(name="membercount")
async def member_count(interaction: discord.Interaction, target: discord.Member):
    embed = discord.Embed(
        title="Member Count:",
        description=f"Total members in the server: {interaction.guild.member_count}",
        color=discord.Color.blue()
    )

    await interaction.response.send_message(embed=embed)


afk_users = {}

@bot.tree.command(name="afk", description="Set your afk status")
async def afk(interaction: discord.Interaction, *, reason: str):
    afk_users[interaction.user.id] = reason
    await interaction.response.send_message(f"Hey {interaction.user.mention} I set your afk to: {reason}", ephemeral=True)


@bot.event
async def on_message(message):
    if message.author.bot:
        return
    

    back_phrases = ["Back", "back"]

    for user in message.mentions:
        if user.id in afk_users:
            reason = afk_users[user.id]
            await message.channel.send(
                f"{message.author.mention}, {user.mention} is currently AFK for: {reason}"
            )

            
        
    if message.content.lower() in back_phrases:
        if message.author.id in afk_users:
            del afk_users[message.author.id]
            await message.channel.send(f"Welcome back, {message.author.mention}")
        else:
            await message.channel.send(f"{message.author.mention} you are not afk.")


@bot.tree.command(name="avatar", description="Shows your pfp")
async def avatar(interaction: discord.Interaction, member: discord.Member):
    embed = discord.Embed(
        title=f"{member.name} Avatar",
        color=discord.Color.red()
    )

    embed.set_image(url=interaction.user.avatar.url)

    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="serverinfo", description="Gives you server info")
async def serverinfo(interaction: discord.Interaction):
    embed = discord.Embed(
        title=f"{interaction.guild.name} Server Info",
        description="Welcome to the official server of BrownHill County",
        color=discord.Color.green()
    )

    guild = interaction.guild
    role_count = len(guild.roles)
    channel_count = len(guild.channels)
    text_channels = len(guild.text_channels)
    owner_name = interaction.guild.owner


    embed.add_field(name="Total Channels:", value=channel_count, inline=False)
    embed.add_field(name="Role Count:", value=role_count, inline=False)
    embed.add_field(name="text channels:", value=text_channels, inline=False)
    embed.add_field(name="Official Owner:", value=owner_name, inline=False)
    embed.set_image(url=interaction.guild.icon)

    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="unban", description="Unbans a member")
@commands.has_permissions(ban_members=True)
async def unban(interaction: discord.Interaction, member: discord.Member, reason:str):
    
    await member.unban(reason=reason)

    embed = discord.Embed(
        title=f"{member.name} has been unbanned",
        description=f"{interaction.user.name} has been unbanned from the server",
        color=discord.Color.green()
    )

    embed.add_field(name="Reason:", value=reason, inline=True)
    embed.add_field(name="unbanned by:", value=interaction.user.name, inline=True)
    embed.set_thumbnail(url=interaction.user.avatar.url)
    embed.set_footer(icon_url=interaction.user.avatar.url, text=f"{interaction.user.id}")

    await interaction.response.send_message(embed=embed, ephemeral=True)

webserver.keep_alive()
