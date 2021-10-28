import discord
import requests
import os
import json
from datetime import datetime, timezone, timedelta
from keep_alive import keep_alive

client = discord.Client()
bot_secret = os.environ['TOKEN']
f = open('cmp.json',)
data = json.load(f)
enhanceDict = {
  "1": "PRI",
  "2": "DUO",
  "3": "TRI",
  "4": "TET",
  "5": "PEN",
  "20": "PEN",
}


def convertToItem(item):
  itemName = ""
  tz = timezone(+timedelta(hours=7))
  for items in data:
    if item[0] == items[0]:
      itemName = items[1]
      break
  itemStr = f"{enhanceDict[item[1]]}:{itemName} (Price: {item[2]}) will be registered at {datetime.fromtimestamp(int(item[3]), tz).strftime('%H:%M:%S')}"
  return itemStr  

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

  # track market listing
  if msg.startswith('$trackMP'):
    resp = requests.post("https://trade.sea.playblackdesert.com/Trademarket/GetWorldMarketWaitList")
    res = json.loads(resp.text)
    resultMsg = res["resultMsg"]
    arrItem = []
    if '|' in resultMsg and resultMsg != '0':
      items = resultMsg.split('|')[:-1]
      for item in items:
        arrItem.append(item.split('-'))
      for item in arrItem:
        await message.channel.send(convertToItem(item))
    else:
      await message.channel.send("No item(s) on queue")

keep_alive()
client.run(bot_secret)