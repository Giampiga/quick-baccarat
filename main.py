import discord
from discord.ext import commands
import random
import time
import os 
from dotenv import load_dotenv

load_dotenv()
bot_token= os.getenv('DISCORD_BOT_TOKEN')

intents = discord.Intents.default()
intents.all()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

user_balances = {}
user_time = {}

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')

@bot.command(name='bet')
async def bet(ctx, hand_bet: str, amount: int):
    user_id = str(ctx.author.id)
    user = ctx.author.display_name

    if amount < 1 or amount > user_balances[user_id] or amount is None or user_id not in user_balances:
        await ctx.send("Please enter a valid amount! You can claim 1000 units every 24hrs.")
        return

    if user_id not in user_balances or user_balances[user_id] < amount:
        await ctx.send("You don't have enough units to place this bet. 🤥")

    suits = ['♠️','♥️','♣️','♦️']

    #Simulating a Baccarat hand
    p_card1 = random.randint(1,13)
    p_card2 = random.randint(1,13)
    b_card1 = random.randint(1,13)
    b_card2 = random.randint(1,13)

    p_hand = '| ' + str(valueToCard(p_card1)) + suits[random.randint(0,3)] + ' |  | ' + str(valueToCard(p_card2)) + suits[random.randint(0,3)] +' |' # for a total of: ' + str(p_value)
    b_hand = '| ' + str(valueToCard(b_card1)) + suits[random.randint(0,3)] + ' |  | ' + str(valueToCard(b_card2)) + suits[random.randint(0,3)] +' |' #for a total of: ' + str(b_value)

    if  p_card1 > 10:
        p_card1 = 10
    if p_card2 > 10:
        p_card2 = 10
    if b_card1 > 10:
        b_card1 = 10
    if b_card2 > 10:
        b_card2 = 10

    p_value = (p_card1 + p_card2) % 10
    b_value = (b_card1 + b_card2) % 10

    #Check for third card
    if p_value <= 5:
        p_card3 = random.randint(1, 13)
        p_hand = '| ' + str(valueToCard(p_card1)) + suits[random.randint(0, 3)] + ' |  | ' + str(
            valueToCard(p_card2)) + suits[random.randint(0, 3)] + ' | | ' + str(valueToCard(p_card3)) + suits[
                     random.randint(0, 3)] + ' |'
        if p_card3 > 10:
            p_card3 = 10
        p_value = (p_value + p_card3) % 10
    else:
        p_hand = '| ' + str(valueToCard(p_card1)) + suits[random.randint(0, 3)] + ' |  | ' + str(
            valueToCard(p_card2)) + suits[random.randint(0, 3)] + ' |'

    if b_value <= 5:
        b_card3 = random.randint(1, 13)
        b_hand = '| ' + str(valueToCard(b_card1)) + suits[random.randint(0, 3)] + ' |  | ' + str(
            valueToCard(b_card2)) + suits[random.randint(0, 3)] + ' | | ' + str(valueToCard(b_card3)) + suits[
                     random.randint(0, 3)] + ' |'
        if b_card3 > 10:
            b_card3 = 10
        b_value = (b_value + b_card3) % 10
    else:
        b_hand = '| ' + str(valueToCard(b_card1)) + suits[random.randint(0, 3)] + ' |  | ' + str(
            valueToCard(b_card2)) + suits[random.randint(0, 3)] + ' |'


    await ctx.send('PLAYER: ' + str(p_hand) + '\t' + 'BANKER: ' + str(b_hand) +
                    '\n\t\t\t\t' + 'Total: ' + '\t **' + str(p_value) + '** \t\t\t\t\t\t **' + str(b_value) + '**')

    # Game logic
    if (p_value > b_value) and (hand_bet == 'p' or hand_bet == 'player'):
        user_balances[user_id] += amount
        await ctx.send('Congratulations ' + str(user) + '! You won ' + str(amount) + ' this hand. Your total is now: ' + str(user_balances[user_id]))
    elif (p_value < b_value) and (hand_bet == 'b' or hand_bet == 'banker'):
        #Super 6 testcase
        if (b_value == 6):
            await ctx.send('Super 6! ' + str(user) + ' wins 50% of the bet. Your total is now: ' + str(user_balances[user_id]))
            user_balances[user_id] += amount / 2
            return
        user_balances[user_id] += amount
        await ctx.send('Congratulations! You won ' + str(amount) + ' this hand. Your total is now: ' + str(user_balances[user_id]))
    elif (p_value == b_value) and (hand_bet != 't' or hand_bet != 'tie'):
        await ctx.send('Tie! You did not win or lose.')
    elif (p_value == b_value) and (hand_bet == 't' or hand_bet == 'tie'):
        user_balances[user_id] += (amount * 8)
        await ctx.send('NICE WIN!' + str(user) + 'You won ' + str(amount * 8) + ' units! Your total is now: ' + str(user_balances[user_id]))
    else:
        user_balances[user_id] -= amount
        await ctx.send(':( You lost ' + str(amount) + ' units. Your total is now: ' + str(user_balances[user_id]))


def valueToCard(card):
    if card == 1:
        card = 'A'
    elif card == 11:
        card = 'J'
    elif card == 12:
        card = 'Q'
    elif card == 13:
        card = 'K'

    return card

@bot.command(name='daily')
async def daily(ctx):
    user_id = str(ctx.author.id)
    curr_time = time.time()

    if user_id not in user_balances:
        user_balances[user_id] = 1000
        user_time[user_id] = curr_time
        await ctx.send('You\'ve received 1000 units for this 24 hours period! New balance: ' + str(user_balances[user_id]))
    else:
        elapsed_time = curr_time - user_time[user_id]
        period = 24 * 60 * 60

        if elapsed_time > period:  
          user_balances[user_id] += 1000
          user_time[user_id] = time.time()
          await ctx.send('You\'ve received 1000 units for this 24 hours period! New balance: ' + str(user_balances[user_id]))
        else:
          await ctx.send('You\'ve already claimed your daily units')

@bot.command(name='balance')
async def balance(ctx):
    user_id = str(ctx.author.id)
    user = ctx.author.display_name

    if user_id not in user_balances:
        await ctx.send(str(user) + ' you have not played before.')
        return
    await ctx.send('' + str(user) + ', your balance is: ' + str(user_balances[user_id]))          

@bot.command(name='info')
async def info(ctx):
    await ctx.send('Use !daily to claim your daily units and start playing Baccarat.\nYou will be receiving 1000 units daily.\nTo place a bet, just do !bet followed by who you place your bet on and the amount, for example: sending "!bet player 100" will place a bet of 100 towards the player, you can also use !bet b X to bet for banker and !bet tie X. \nWhoever gets closest to 9 mod 10 wins. You are able to bet towards a tie for a sweet 8x.')

bot.run(bot_token)
