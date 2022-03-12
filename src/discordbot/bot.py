import discord
from discord.ext import commands
from pymongo import MongoClient
from datetime import datetime
from os import getenv
from dotenv import load_dotenv
from json import load, dump


load_dotenv()

db_client = MongoClient(getenv('MONGO_URI'))
users = db_client.linksbase.users

class api:
    def get_u(username):
        u = users.find_one({'username': username})

        if not u:
            return { '_error': True, '_error_message': f'User {username} not found' }
        
        del u['password']
        del u['email']
        del u['_id']
        u['avatar'] = f'https://cdn.linksb.me/avatars/{username}'
        u['qr_code'] = f'https://cdn.linksb.me/qrcodes/{username}'

        return { '_error': False, '_error_message': '', **u }

    def get_qr(username):
        u = users.find_one({'username': username})

        if not u:
            return { '_error': False, '_error_message': '' }

        del u['password']
        del u['email']
        del u['_id']
        del u['avatar']
        del u['data']
        del u['registered_in']
        u['qr_code'] = f'https://cdn.linksb.me/qrcodes/{username}'

        return { '_error': False, '_error_message': '', **u }

api_link = 'https://api.linksb.me'
client = commands.Bot(command_prefix='!')


# with open('auth.json', 'r') as authFile:
#     authData = load(authFile)

@client.event
async def on_ready():
    await client.change_presence(activity=discord.Game(name='LinksBase | Under Development!!'))
    print(f'Logged in as {client.user}')

# @client.event
# async def on_message(message):
#     if message.author.bot:
#         return

#     if message.content.lower() == '!ping':
#         await message.reply(f'{round(client.latency * 1000)}ms')

#     if message.content.lower().startswith('!user'):
#         u = message.content.lower().strip().split(' ')

#         print(f'{u=}')

#         if len(u) == 1:
#             return await message.reply('Usage: !user {username}')

#         user = api.get_u(u[1])
#         qrcode = api.get_qr(u[1])
        
#         if user.get('_error') == True:
#             return await message.reply('Error: User Does Not Exist!')

#         embed = discord.Embed(title=f'LinksBase | {user["username"]}', url=f'{user["data"]["url"]}', description=f'{user["data"]["description"]}', color=0x0057c0)
#         embed.set_thumbnail(url=user['avatar'])
#         embed.set_image(url=qrcode['qr_code'])
#         embed.timestamp = datetime.now()
#         embed.set_footer(text='api.linksb.me', icon_url=client.user.display_avatar)

#         view = discord.ui.View()
#         visit_profile_button = discord.ui.Button(label='Visit Profile!', url=user['data']['url'], emoji='🔗')

#         view.add_item(visit_profile_button)

#         return await message.channel.send(embed=embed, view=view)

    
    # if message.content.lower() == '!help':
    #     return await message.reply('ما عملتها😔')

@client.slash_command(guild_ids=[930807810659319868], name='user', description="Get user's profile and QR Code.")
async def user(ctx, user):
    # await ctx.defer()

    u = user.strip().lower()

    user = api.get_u(u)
    qrcode = api.get_qr(u)

    if user.get('_error') == True:
            await ctx.followup.send('Error: User Does Not Exist!', ephemeral=True)
    else:
        embed = discord.Embed(title=f'LinksBase | {user["username"]}', url=f'{user["data"]["url"]}', description=f'{user["data"]["description"]}', color=0x0057c0)
        embed.set_thumbnail(url=user['avatar'])
        embed.set_image(url=qrcode['qr_code'])
        embed.timestamp = datetime.now()
        embed.set_footer(text='api.linksb.me', icon_url=client.user.display_avatar)

        view = discord.ui.View()
        visit_profile_button = discord.ui.Button(label='Visit Profile!', url=user['data']['url'], emoji='🔗')

        view.add_item(visit_profile_button)

        await ctx.followup.send(embed=embed, view=view)

@client.slash_command(guild_ids=[930807810659319868], name='ping', description="Get the latency of the bot.")
async def ping(ctx):
    await ctx.defer()

    await ctx.followup.send(f'{round(client.latency * 1000)}ms')

# @client.slash_command(guilds_ids=[930807810659319868], name='auth', description='Set your linksbase account to your discord id')
# async def auth(ctx, linksbase_username):
#     ctx.defer()
#     linksbase_username = linksbase_username.strip().lower()

#     u = api.get_u(linksbase_username)

#     if u.get('_error') == True:
#         await ctx.followup.send('Error: Invalid Username', ephemeral=True)
#     else:
#         authData[ctx.user.id] = linksbase_username
#         with open('auth.json', 'w') as authFile:
#             dump(authData, authFile, indent=3)
#         await ctx.followup.send(f'You are authenticated to {linksbase_username}')
    
@interClient.user_command(guild_ids=[930807810659319868])
async def profile(ctx):
    await ctx.respond('test')

client.run(getenv('BOT_TOKEN'))