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
tz = timezone(+timedelta(hours=7))


def convertToItem(item):
  itemName = ""
  for items in data:
    if item[0] == items[0]:
      itemName = items[1]
      break
  price = '{:,d}'.format(int(item[2]))
  itemStr = f"{enhanceDict[item[1]]}:{itemName} (Price: {price}) will be registered at {datetime.fromtimestamp(int(item[3]), tz).strftime('%H:%M:%S')}"
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
  
  content = message.content.lower()
  words = content.split()
  if 'crot' in words:
    imgUrl = "https://images-ext-1.discordapp.net/external/XOEBSA2JdVvXiiwOzzVK5SyRBc3FKIZInhOaynfARkg/%3Fsize%3D96/https/cdn.discordapp.com/emojis/887198281594179594.png"
    for word in words:
      if 'crot' in word:
        await message.channel.send(imgUrl)

  #show member profile on specific guild
  if msg.startswith('$profile'):
    resp = msg.split()
    memberObj = object()
    if len(resp) > 1:
      id = resp[1]
      disallowed_characters = "<@!>"
      for char in disallowed_characters:
        id = id.replace(char,"")
      memberObj = await message.guild.fetch_member(int(id))
    else:
      memberObj = message.author  
    now = datetime.now(tz)
    embed = discord.Embed(
      title=memberObj.name,
      timestamp=now,
      color=memberObj.color
    )
    embed.set_image(url=memberObj.avatar_url)
    embed.add_field(name="Created at", value=memberObj.created_at.strftime('%d-%b-%Y (%H:%M:%S)'))
    embed.add_field(name=f"Joined {message.guild.name} at", value=memberObj.joined_at.strftime('%d-%b-%Y (%H:%M:%S)'))
    await message.channel.send(embed=embed)

keep_alive()
client.run(bot_secret)