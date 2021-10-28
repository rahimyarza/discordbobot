import discord
import os

client = discord.Client()
bot_secret = os.environ['TOKEN']

def convert(sentence):
  return sentence.split('$check', 1) [1]

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
  if message.author == client.user:
        return

  msg = message.content

  # check market price
  if msg.startswith('$check'):
    tax = 0.65
    item = msg.split()
    price = int(item[1])
    qty = int(item[2])
    totalWithoutTax = price * qty
    totalWithoutVP = totalWithoutTax - (totalWithoutTax - (totalWithoutTax * tax))
    totalWithVP = totalWithoutVP * 1.3
    totalWoTax = '{:,d}'.format(totalWithoutTax)
    totalWoVP = '{:,d}'.format(int(totalWithoutVP))
    totalVP = '{:,d}'.format(int(totalWithVP))
    response = f'**Total Without Tax** = {totalWoTax} \n**Total Without VP** = {totalWoVP} \n**Total With VP** = {totalVP}'
    await message.channel.send(response)

client.run(bot_secret)