import discord
import requests
import os
import asyncio
import json
from datetime import datetime, timezone, timedelta
from keep_alive import keep_alive
from replit import db

client = discord.Client()
bot_secret = os.environ['TOKEN']
f = open('cmp.json',)
data = json.load(f)
enhanceDict = {
  "0": "BASE",
  "1": "PRI",
  "2": "DUO",
  "3": "TRI",
  "4": "TET",
  "5": "PEN",
  "20": "PEN",
}
tz = timezone(+timedelta(hours=7))
FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}

async def call_api(channel, member):
  resp = requests.post("https://trade.sea.playblackdesert.com/Trademarket/GetWorldMarketWaitList")
  res = json.loads(resp.text)
  resultMsg = res["resultMsg"]
  arrItem = []
  if '|' in resultMsg and resultMsg != '0':
    items = resultMsg.split('|')[:-1]
    for item in items:
      arrItem.append(item.split('-'))
    for item in arrItem:
      if item[0] in db.keys():
        if not item[3] in db[item[0]]:
            await channel.send(convertToItem(item))
            db[item[0]].append(item[3])
      else:
        arr = [item[3]]
        db[item[0]] = arr
        await channel.send(convertToItem(item))

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
  for key in db.keys():
    del db[key]
  channel = client.get_channel(903284981621739551)
  member = 190091162189561856
  
  while not client.is_closed():
    await call_api(channel, member)
    await asyncio.sleep(10)

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
  if 'crot' in str(words):
    imgUrl = "https://images-ext-1.discordapp.net/external/XOEBSA2JdVvXiiwOzzVK5SyRBc3FKIZInhOaynfARkg/%3Fsize%3D96/https/cdn.discordapp.com/emojis/887198281594179594.png"
    for word in words:
      if word.find('crot') != -1:
        await message.channel.send(imgUrl)

  #show member profile on specific guild
  if msg.startswith('$profile'):
    resp = msg.split()
    memberObj = object()
    if len(resp) > 1:
      id = resp[1].strip("<@!>")
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
  
  #clear message
  if msg.startswith('$clear'):
    resp = msg.split()
    if len(resp) > 1 and resp[1].isnumeric:
      limit = resp[1]
      await message.channel.purge(limit=int(limit)+1)
    else:
      await message.channel.send("Wrong syntax")

  #honk your vc
  if msg.startswith('$honk'):
    voice_channel = message.author.voice
    if voice_channel != None:
      vc = await voice_channel.channel.connect()
      source = discord.FFmpegPCMAudio("https://content.videvo.net/videvo_files/audio/premium/audio0121/originalContent/JeepChrkeHornHonks%20PE894601.mp3", **FFMPEG_OPTIONS)
      vc.play(source)
      while vc.is_playing():
        await asyncio.sleep(1)
      else:  
        await vc.disconnect()
    else:
      await message.channel.send("You're not on any voice channel")

  #anyink your vc
  if msg.startswith('$anyink'):
    voice_channel = message.author.voice
    if voice_channel != None:
      vc = await voice_channel.channel.connect()
      source = discord.FFmpegPCMAudio("https://cdn.discordapp.com/attachments/409882874154844160/904012329111412836/anying_anying_anying_II_SOUND_EFFECT.wav", **FFMPEG_OPTIONS)
      vc.play(source)
      while vc.is_playing():
        await asyncio.sleep(1)
      else:  
        await vc.disconnect()
    else:
      await message.channel.send("You're not on any voice channel")
      
# track users when join or leave voice channel
# @client.event 
# async def on_voice_state_update(member, before, after):
#   if not member.bot:
#     if not before.channel and after.channel:
#       guildSysChannel = after.channel.guild.system_channel
#       await guildSysChannel.send(f'{member} joined {after.channel} on {after.channel.guild}')
#     elif before.channel and not after.channel:
#       guildSysChannel = before.channel.guild.system_channel
#       await guildSysChannel.send(f'{member} left {before.channel} on {before.channel.guild}')

keep_alive()
client.run(bot_secret)

