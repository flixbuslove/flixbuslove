import discord
from discord.ext import commands
import json
import os

intents = discord.Intents.default()
intents.message_content = True
intents.members = True  # Potrzebne do wysyłania DM-ów oraz zarządzania użytkownikami

bot = commands.Bot(command_prefix='!', intents=intents)

# Sprawdzenie, czy plik z ekonomią istnieje, jeśli nie, to go tworzy
if not os.path.exists('economy.json'):
    with open('economy.json', 'w') as f:
        json.dump({}, f)

if not os.path.exists('shop.json'):
    with open('shop.json', 'w') as f:
        json.dump({}, f)

def get_balance(user_id):
    with open('economy.json', 'r') as f:
        users = json.load(f)

    if str(user_id) in users:
        return users[str(user_id)]['balance']
    else:
        return 0

def update_balance(user_id, amount):
    with open('economy.json', 'r') as f:
        users = json.load(f)

    if str(user_id) in users:
        users[str(user_id)]['balance'] += amount
    else:
        users[str(user_id)] = {'balance': amount}

    with open('economy.json', 'w') as f:
        json.dump(users, f)

def add_item_to_shop(item_name, price, seller_id):
    with open('shop.json', 'r') as f:
        shop = json.load(f)

    shop[item_name] = {'price': price, 'seller_id': seller_id}

    with open('shop.json', 'w') as f:
        json.dump(shop, f)

def get_shop():
    with open('shop.json', 'r') as f:
        return json.load(f)

@bot.event
async def on_ready():
    print(f'Bot {bot.user} jest online!')

@bot.command()
async def balance(ctx):
    """Sprawdza balans użytkownika."""
    bal = get_balance(ctx.author.id)
    await ctx.send(f'{ctx.author.mention}, twój balans wynosi: {bal} monet.')

@bot.command()
async def earn(ctx, amount: int):
    """Zarabia określoną ilość monet."""
    if amount < 0:
        await ctx.send('Nie można zarobić ujemnych monet!')
        return

    update_balance(ctx.author.id, amount)
    await ctx.send(f'{ctx.author.mention}, zarobiłeś {amount} monet.')

@bot.command()
async def spend(ctx, amount: int):
    """Wydaje określoną ilość monet."""
    bal = get_balance(ctx.author.id)

    if amount > bal:
        await ctx.send(f'{ctx.author.mention}, nie masz wystarczającej ilości monet!')
    elif amount < 0:
        await ctx.send('Nie można wydać ujemnych monet!')
    else:
        update_balance(ctx.author.id, -amount)
        await ctx.send(f'{ctx.author.mention}, wydałeś {amount} monet.')

@bot.command()
async def shop(ctx):
    """Wyświetla dostępne przedmioty w sklepie."""
    shop_items = get_shop()

    if not shop_items:
        await ctx.send("Sklep jest pusty!")
        return

    shop_message = "Sklep:\n"
    for item, details in shop_items.items():
        shop_message += f"{item}: {details['price']} monet (Sprzedawca: <@{details['seller_id']}>)\n"

    await ctx.send(shop_message)

@bot.command()
async def additem(ctx, item_name: str, price: int):
    """Dodaje przedmiot do sklepu."""
    add_item_to_shop(item_name, price, ctx.author.id)
    await ctx.send(f'{ctx.author.mention}, dodałeś przedmiot {item_name} do sklepu za {price} monet.')

@bot.command()
async def buy(ctx, item_name: str):
    """Pozwala na zakup przedmiotu ze sklepu."""
    shop_items = get_shop()

    if item_name in shop_items:
        item_details = shop_items[item_name]
        item_price = item_details['price']
        seller_id = item_details['seller_id']
        bal = get_balance(ctx.author.id)

        if bal >= item_price:
            update_balance(ctx.author.id, -item_price)
            update_balance(seller_id, item_price)

            # Wysyłanie wiadomości do sprzedawcy
            seller = await bot.fetch_user(seller_id)
            await seller.send(f'Ktoś kupił twój przedmiot: {item_name} za {item_price} monet.')

            await ctx.send(f'{ctx.author.mention}, kupiłeś {item_name} za {item_price} monet.')
        else:
            await ctx.send(f'{ctx.author.mention}, nie masz wystarczającej ilości monet, aby kupić {item_name}.')
    else:
        await ctx.send(f'{ctx.author.mention}, przedmiot {item_name} nie istnieje w sklepie.')

@bot.command()
@commands.has_permissions(administrator=True)
async def announce(ctx, channel: discord.TextChannel, *, message):
    """Wysyła ogłoszenie na wybranym kanale."""
    await channel.send(message)
    await ctx.send(f'Ogłoszenie zostało wysłane na {channel.mention}.')

@bot.command()
async def dm(ctx, member: discord.Member, *, message):
    """Wysyła prywatną wiadomość do użytkownika."""
    try:
        await member.send(message)
        await ctx.send(f'Wysłano wiadomość do {member.mention}.')
    except discord.Forbidden:
        await ctx.send(f'Nie można wysłać wiadomości do {member.mention}.')

@bot.event
async def on_message(message):
    """Automatyczna odpowiedź na DM z reakcją 'x'."""
    if isinstance(message.channel, discord.DMChannel) and message.author != bot.user:
        await message.add_reaction('❌')
        await message.channel.send('Dziękuję za wiadomość!')

    await bot.process_commands(message)

# Uruchomienie bota z tokenem
bot.run('MTI2ODIwODc3MjEyNDI1MDExNA.GlkG-_.HEsqwdaDYgvm3Ekw1JLrZIW98cCfQFJ74pAMvc')
