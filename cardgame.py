#Imports I am using
import datetime
import time
import discord
import random
import asyncio
import ast
import re
import pandas
import math
from os.path import exists
from pickle import load, dump

#Data files
store = 'cardgamestore.pk'
carddata = 'memecard.xlsx'

#Setup discord
TOKEN = 'NjMxMzE4NjQxODI4MTY3NzA0.XZ5Odw.942_9faHEwDR5MxgSDC2Q16g9_k'
GUILD = 'DISCORD_GUILD'
intents = discord.Intents.all()
client = discord.Client(intents=intents)
@client.event
async def on_ready():
  print(f'{client.user} has connected to Discord!')

#card class
class Card:
  def __init__(self, name, description, attack, maxattack, health, maxhealth, rate, maxrate, attackbuff, ratebuff, specialcost, status, statustimer, slot, row, identity, cooldown, quality, category, specialmode, spiritcost):
    self.name = name
    self.description = description
    self.attack = attack
    self.maxattack = maxattack
    self.health = health
    self.maxhealth = maxhealth
    self.rate = rate
    self.maxrate = maxrate
    self.attackbuff = attackbuff
    self.ratebuff = ratebuff
    self.specialcost = specialcost
    self.status = status
    self.statustimer = statustimer
    self.slot = slot
    self.row = row
    self.identity = identity
    self.cooldown = cooldown
    self.quality = quality
    self.category = category
    self.specialmode = specialmode
    self.spiritcost = spiritcost

#tempgames stored here
tempgames = {}
allowgame = True

#Inventory vars includes all basic items which exist in the game and the order they will display in your inventory
inventory = {"hstat:loottimer": 0, "hstat:passive": None, "stat:gameid": 0, "hstat:deck": [], "stat:ingame": False, "quartz": 0, "opal": 0, "ruby": 0, "sapphire": 0, "pearl": 0, "diamond": 0, "amethyst": 0, "aquamarine": 0, "emerald": 0, "onyx": 0, "amber": 0, "gold": 0, "resin": 0, "stardust": 0, "shadow": 0, "butterfly": 0}
loottable = {"quartz": [1,4,100], "opal": [1,2,25]}






#Turn this on to automatically delete values from player data which do not exist anymore
deletesautoload = False
#Keep this on to add values which you implemented into the player database
addsautoload = True






#Card data reader
card_descriptions = {}

#Card data
#0 Description
#1 Attack
#2 Health
#3 Rate
#4 Special Glitter Cost
#5 Category
#6 Special mode
#7 Id
#8 Spirit Cost

rawdict = pandas.read_excel(carddata).to_dict()

for i in rawdict:
  for j in rawdict[i]:
    if rawdict[i][j] != rawdict[i][j]:
      rawdict[i][j] = "0"

namepart = []
statuspart = []
typepart = []
#normaldescriptionpart = []
descriptionpart = []
#obtaindescriptionpart = []
spiritcostpart = []
attackpart = []
healthpart = []
ratepart = []
specialcostpart = []
modepart = []
idpart = []

for i in rawdict["Name"]:
  value = rawdict["Name"][i]
  namepart.append(value.lower().replace(' ', '_'))
for i in rawdict["Production status"]:
  value = rawdict["Production status"][i]
  statuspart.append(value)
for i in rawdict["Type"]:
  value = rawdict["Type"][i]
  typepart.append(value.lower())
for i in rawdict["Gameplay Description"]:
  value = rawdict["Gameplay Description"][i]
  descriptionpart.append(value)
for i in rawdict["Spirit Cost"]:
  value = rawdict["Spirit Cost"][i]
  if value == "0":
    spiritcostpart.append("none")
  else:
    value = value.lower().split()
    spiritcostpart.append({"red": value.count("red"), "blue": value.count("blue"), "green": value.count("green"), "black": value.count("black"), "any": value.count("any")})
for i in rawdict["Atk"]:
  value = rawdict["Atk"][i]
  attackpart.append(int(value))
for i in rawdict["Hp"]:
  value = rawdict["Hp"][i]
  healthpart.append(int(value))
for i in rawdict["Rate"]:
  value = rawdict["Rate"][i]
  ratepart.append(float(value))
for i in rawdict["Special ability cost"]:
  value = rawdict["Special ability cost"][i]
  specialcostpart.append(int(value))
for i in rawdict["Special mode"]:
  value = rawdict["Special mode"][i]
  modepart.append(value.lower())
for i in rawdict["Id"]:
  value = rawdict["Id"][i]
  idpart.append(int(value))

for name, valid, category, description, attack, health, rate, specialcost, specialmode, idnumber, spiritcost in zip(namepart, statuspart, typepart, descriptionpart, attackpart, healthpart, ratepart, specialcostpart, modepart, idpart, spiritcostpart):
  if valid == "In game":
    card_descriptions[name] = [description, attack, health, rate, specialcost, category, specialmode, idnumber, spiritcost]

#Add cards to inventory automatically
for i in card_descriptions:
  inventory[i] = 2
  inventory[i+"-i"] = 2
  inventory[i+"-p"] = 2






#creating the main functional card list
cardlist = []
for i in card_descriptions:
  data = card_descriptions[i]
  cardtomake = Card(i, data[0], data[1], data[1], data[2], data[2], data[3], data[3], 1, 1, data[4], "none", 0, 0, 0, i, 1, "n", data[5], data[6], data[8])
  cardlist.append(cardtomake)






#This section of code automatically adds and removes values from player databases with your changes to the code, runs everytime you refresh the program

#LOAD (PART 1/4)
with open(store, 'rb') as i:
  master = load(i)
#debug line i added here, hard resets player database
#master = {}
#TAKE AWAY (PART 2/4)
if deletesautoload == True:
  for i in master:
    valuestokill = []
    for key in master[i]:
      if key not in inventory.keys():
        valuestokill.append(key)
    for j in valuestokill:
      del master[i][j]
#ADD (PART 3/4)
if addsautoload == True:
  for i in master:
    for bruh in inventory.keys():
      if bruh not in master[i]:
        master[i][bruh] = inventory[bruh]
#UPDATE INGAME STATS (PART 3.5/4)
for i in master:
  master[i]["stat:ingame"] = False
  master[i]["stat:gameid"] = 0
#SAVE (PART 4/4)
with open(store, 'wb') as i:
  dump(master,i)

#This is the code which runs on each message
@client.event
async def on_message(message):
  #The bot cannot respond to itself on accident
  if message.author.id == client.user.id:
    return
  #open up the pk storage file. It contains a list called newmaster, holding all player data.
  global master
  with open(store, 'rb') as i:
    master = load(i)
  #save command, used near the end of the code. This stores values back into the pickle file, which is the reloaded on the next message.
  async def save():
    with open(store, 'wb') as i:
      dump(master,i)
    print("saved")
  #automatically add people who send a message to the master list.
  check = True
  for i in master:
    if i == message.author.id:
      check = False
  if check == True:
    master[message.author.id] = inventory
    print("you've been added to the master list ya")
  
  #USEFUL VARIABLES TO DEFINE
  #The text which will be sent back via discord bot
  response = ""
  #The user id of the person who sent the command
  author = message.author.id
  #Shortcuts
  m = message.content
  ml = len(m.split())
  ms = m.split()
  inv = master[author]
  currenttime = time.time()/3600
  #When somebody calls a game command and doesnt specify a number, it gets defaulted to one.
  amount = 1

  #birthday reminder
  c1 = ["jayc", "jacob", "j", "jaco", "jaycs", "jacobs", "js", "jacos","jayc's", "jacob's", "j's", "jaco's"]
  c2 = ["when's", "whens", "when", "wat", "wats", "what", "whats", "wat's", "what's"]
  c3 = ["bday", "birthday", "birth"]
  for i in c1:
    if i in m.lower().split():
      for j in c2:
        if j in m.lower().split():
          for h in c3:
            if h in m.lower().split():
              response = "JULY 8 REEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEE"
              break
          break
      break
  
  #The if statement runs if a command was used, valid or not.
  if message.content.split()[0] == "d" or response == "JULY 8 REEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEE":
    
    #D HELP
    if m == 'd help':
      response = "lol i haven't updated this in forever"
    
    #D Version
    if m == 'd version':
      response = "Yaybot Watermelon (indev)"
    
    #D SET
    if "d set" in m:
      master = ast.literal_eval(m.replace("d set ",""))
      response = "done"

    #NSET
    if "d nset" in m:
      tempmaster = master.copy()
      preauthor = ms[2]
      if ms[2] != "@e":
        authorid = int(re.sub('\D','',ms[2]))
      target = ms[3]
      ms = ms[4:]
      value = ast.literal_eval(" ".join(ms))
      for i in master:
        if preauthor == "@e":
          tempmaster[i][target] = value
          master = tempmaster
        elif i == authorid:
          tempmaster[i][target] = value
          master = tempmaster
          break
      response = "done"

    #D MASTER
    if m == 'd master':
      print(master)
      response = str(master)
    
    ##############################################
    ##############################################
    #all commands after here are actual game commands
    if author in master:
      
      #INVENTORY
      if "d inv" in m:
        listofitems = ""
        listofcards = ""
        name = await client.fetch_user(author)
        name = str(name)[:-5]
        for key in inv:
          if "stat" not in key:
            if inv[key] > 0:
              basename = key
              itemname = key.replace("_", " ").capitalize()
              if "-i" in itemname:
                basename = basename.replace("-i", "")
                itemname = itemname.replace("-i", " (Infernal)")
              elif "-p" in itemname:
                basename = basename.replace("-p", "")
                itemname = itemname.replace("-p", " (Prismatic)")
              if basename in card_descriptions:
                listofcards += itemname + ": " + str(inv[key]) + '\n'
              else:
                listofitems += itemname + ": " + str(inv[key]) + '\n'
        if listofitems == "":
          listofitems = "nothing!\n"
        if listofcards == "":
          listofcards = "nothing!\n"
        response = str(name) + "'s material cards:\n" + listofitems + "\n" + str(name) + "'s playable cards:\n" + listofcards
      
      #STAT
      if "d stat" in m:
        listofstats = ""
        name = await client.fetch_user(author)
        name = str(name)[:-5]
        for key in inv:
          if "stat" in key:
            if "hstat" not in key:
              listofstats+=(key[5:].replace('\'',"") + ": " + str(inv[key])) + '\n'
        if listofstats == "":
          listofstats = "nothing!"
        response = str(name) + "'s stats:\n" + listofstats

      #LOOT
      if m == "d loot":
        td = currenttime - inv["hstat:loottimer"]
        time_left = round((4-td)*60)
        if td > 4:
          response = "You found:"
          inv["hstat:loottimer"] = currenttime
          for i in loottable:
            arnd = random.randint(loottable[i][0],loottable[i][1])
            xrnd = random.randint(0,99)
            chance = loottable[i][2]
            if xrnd < chance:
              inv[i] += arnd
              response+= "\n" + str(arnd) + " " + i
        else:
          response = "still some time left on the clock, looks like around " + str(time_left) + " minutes to wait."

      #GIVE
      if "d give" in m:
        #holy variables
        isint = True
        isuser = True
        if int(re.sub('\D','',ms[2])) in master:
          user = int(re.sub('\D','',ms[2]))
        else:
          isuser = False
        itemname = ms[3]
        if ml == 5:
          if ms[4].isdigit() == True:
            amount = int(ms[4])
          elif "-" in ms[4]:
            if re.sub('-','',ms[4]).isdigit() == True:
              amount = int(ms[4])
          else:
            isint =  False
        if isuser == False:
          response = "er thats not a user, or they haven\'t joined"
        elif isint == False:
          response = "that's not a valid number for your amount, or you switched up your item and amount!"
        elif amount < 0:
          response = "uh thats called stealing and its frowned upon in most cultures - elli"
        elif itemname not in inventory or "stat" in itemname:
          response = "i don't think that item exists"
        elif amount > inv[itemname]:
          response = "lol do you have that much of that"
        elif user in master:
          inv[itemname] -= amount
          for i in master:
            if user == i:
              master[i][itemname] += amount
              response = "your items have successfully been given"
              break
        else:
          response = "user has not joined!"
      
      #USE
      if "d use" in m:
        if ml == 4:
          amount = int(ms[3])
        if amount < 1:
          response = "you know let's just not ok"
        elif ms[2] not in inventory:
          response = "i don't think that item exists"
        elif amount > inv[ms[2]]:
          response = "lol do you have that much of that"
        elif ms[2] == "item":
          pass
        else:
          response = "this item can't be used with this command."

      #CATALOG
      if m == "d catalog":
        subresponses = ["Producer:\n","Defense:\n","Offense:\n","Spell:\n","Passive:\n"]
        unsorted_tuples = [(i, card_descriptions[i][7]) for i in card_descriptions]
        sorted_tuples = sorted(unsorted_tuples, key=lambda item: item[1])
        card_descriptions_sorted = {key: value for key, value in sorted_tuples}
        for sortorder in card_descriptions_sorted:
          for i in cardlist:
            if i.name == sortorder:
              text = "(" + str(card_descriptions_sorted[i.name]) + ") " + i.name.replace("_", " ").capitalize() + "\n"
              if i.category == "producer":
                subresponses[0] += text
              elif i.category == "defense":
                subresponses[1] += text
              elif i.category == "offense":
                subresponses[2] += text
              elif i.category == "spell":
                subresponses[3] += text
              elif i.category == "passive":
                subresponses[4] += text
              break
        for i in subresponses:
          response += i + "\n"

      #INSPECT
      if "d inspect" in m:
        stampname = ms[2]
        basename = ms[2].replace("-i", "")
        refinedname = ""
        if "-i" in stampname:
          refinedname = stampname.replace("_", " ").replace("-i", " (Iridescent)").capitalize()
        else:
          refinedname = stampname.replace("_", " ").capitalize()
        if basename in card_descriptions:
          filename = stampname+'.png'
          if exists(filename):
            await message.channel.send(file=discord.File(filename))
          stats = card_descriptions[basename]
          response = refinedname + "\nType: " + stats[5].capitalize() + "\n"
          if stats[2] != 0:
            response += "\nAttack: " + str(stats[1]) + "\nHealth: " + str(stats[2]) + "\nRate: " + str(stats[3])
          if stats[4] != 0:
            response += "\nSpecial ability cost: " + str(stats[4]) + " Glitter"
          if stats[8] != "none":
            spiritpart = []
            for i in stats[8]:
              for n in range(stats[8][i]):
                spiritpart.append(i.capitalize())
            response += "\nSpirit cost: " + ", ".join(spiritpart)
          response += "\nDescription: " + stats[0]
    
      #DECK
      if m == "d deck":
        listofitems = ""
        passive = ""
        name = await client.fetch_user(author)
        name = str(name)[:-5]
        #Regular cards
        cardstoprintdata = []
        for item in inv["hstat:deck"]:
          quality = ""
          if item.quality == "i":
            quality = " (Infernal)"
          if item.quality == "p":
            quality = " (Prismatic)"
          cardtoadd = item.name.replace("_", " ").capitalize() + quality + '\n'
          if cardtoadd in cardstoprintdata:
            cardstoprintdata.insert(cardstoprintdata.index(cardtoadd), cardtoadd)
          else:
            cardstoprintdata.append(cardtoadd)
        for i in cardstoprintdata:
          listofitems += i
        #Passive card
        if inv["hstat:passive"] != None:
          quality = ""
          if inv["hstat:passive"].quality == "i":
            quality = " (Infernal)"
          elif inv["hstat:passive"].quality == "p":
            quality = " (Prismatic)"
          passive = "Passive - " + inv["hstat:passive"].name.replace("_", " ").capitalize() + quality + '\n'
        #If nothing
        if passive == "" and listofitems == "":
          listofitems = "nothing!"
        #Response
        response = str(name) + "'s deck:\n" + passive + listofitems

      #DECK ADD
      if "d deck add" in m:
        if len(master[author]["hstat:deck"]) < 30:
          cardname = ms[3]
          basename = cardname.replace("-i", "").replace("-p", "")
          if basename in card_descriptions:
            if inv[cardname] > 0:
              for i in cardlist:
                if i.name == basename:
                  cardcount = 0
                  for j in inv["hstat:deck"]:
                    if j.name == basename:
                      cardcount += 1
                  if cardcount < 2:
                    cardtoadd = i
                    if i.category == "passive":
                      if inv["hstat:passive"] == None:
                        if "-i" in cardname:
                          cardtoadd.quality = "i"
                        if "-p" in cardname:
                          cardtoadd.quality = "p"
                        inv["hstat:passive"] = cardtoadd
                        inv[cardname] -= 1
                        response = "card added"
                        break
                      else:
                        response = "You already have a passive card in deck"
                    else:
                      if "-i" in cardname:
                        cardtoadd.quality = "i"
                      if "-p" in cardname:
                        cardtoadd.quality = "p"
                      inv["hstat:deck"].append(cardtoadd)
                      inv[cardname] -= 1
                      response = "card added"
                      break
                  else:
                    response = "You already have 2 of this card in your deck"
            else:
              response = "card doesn't exist or you don't have any"
          else:
            response = "that's not a playable card"
        else:
          response = "You can only have up to 30 cards in your deck"

      #DECK REMOVE
      if "d deck remove" in m:
        cardname = ms[3]
        joint_deck = inv["hstat:deck"].copy()
        if inv["hstat:passive"] != None:
          joint_deck += [inv["hstat:passive"]]
        for i in joint_deck:
          if i.name == cardname.replace("-i", "").replace("-p", ""):
            if ("-i" in cardname and i.quality != "i") or ("-p" in cardname and i.quality != "p"):
              response = "that card isn't in your deck"
            else:
              if i.category == "passive":
                inv["hstat:passive"] = None
              else:
                inv["hstat:deck"].remove(i)
              inv[cardname] += 1
              response = "card removed"
              break
        else:
          response = "that card isn't in your deck"

      #DECK CLEAR
      if m in ("d deck clear", "d deck remove all"):
        joint_deck = inv["hstat:deck"].copy()
        if inv["hstat:passive"] != None:
          joint_deck += [inv["hstat:passive"]]
        for i in joint_deck:
          if i.category == "passive":
            inv["hstat:passive"] = None
          else:
            inv["hstat:deck"].remove(i)
          if i.quality == "i":
            inv[i.name+"-i"] += 1
          elif i.quality == "p":
            inv[i.name+"-p"] += 1
          else:
            inv[i.name] += 1
        response = "All cards were removed and put back in inventory"

      #MATCH
      if "d match" in m:
        opponent = int(re.sub('\D','',ms[2]))
        if opponent not in master:
          response = "The person you're trying to match with isn't in the database. They should send at least one message of any kind to be included."
        elif author == opponent:
          response = "you know let's not ok"
        elif len(master[author]["hstat:deck"]) < 10:
          response = "You need at least 10 cards in your deck"
        elif len(master[opponent]["hstat:deck"]) < 10:
          response = "The person you're trying to match with does not have at least 10 cards in their deck"
        elif inv["stat:ingame"] == False and master[opponent]["stat:ingame"] == False:
          gameid = author
          master[author]["stat:ingame"] = True
          master[author]["stat:gameid"] = gameid
          master[opponent]["stat:ingame"] = True
          master[opponent]["stat:gameid"] = gameid
          p1deck = []
          p2deck = []
          for i in master[author]["hstat:deck"]:
            data = card_descriptions[i.name]
            cardtomake = Card(i.name, data[0], data[1], data[1], data[2], data[2], data[3], data[3], 1, 1, data[4], "none", 0, 0, 0, i.name, 1, "n", data[5], data[6], data[8])
            cardtomake.quality = i.quality
            p1deck.append(cardtomake)
          for i in master[opponent]["hstat:deck"]:
            data = card_descriptions[i.name]
            cardtomake = Card(i.name, data[0], data[1], data[1], data[2], data[2], data[3], data[3], 1, 1, data[4], "none", 0, 0, 0, i.name, 1, "n", data[5], data[6], data[8])
            cardtomake.quality = i.quality
            p2deck.append(cardtomake)
          p1passive = master[author]["hstat:passive"]
          p2passive = master[opponent]["hstat:passive"]
          p1hand = []
          p2hand = []
          for i in range(5):
            randomcard = random.choice(p1deck)
            p1deck.remove(randomcard)
            p1hand.append(randomcard)
            randomcard = random.choice(p2deck)
            p2deck.remove(randomcard)
            p2hand.append(randomcard)
          
          tempgames[gameid] = {"turn": author, "author": author, "opponent": opponent, "actioncounter": 2, "point": [0, 0], "bag": [[],[]], "glitter": [0, 0], "rate": [0, 0], "passive": [p1passive, p2passive], "event": "none", "eventtimer": 0, "deck": [p1deck, p2deck], "hand": [p1hand, p2hand], "graveyard": [[], []], "board": [], "interact_allowed": [False, False]}
          
          asyncio.create_task(save())

          name = await client.fetch_user(author)
          name = str(name)[:-5]
          
          await message.channel.send("You two are now in a game together. " + name + " goes first.")
          return
        elif inv["stat:ingame"] == True or master[opponent]["stat:ingame"] == True:
          response = "You or they are already in a match!"

      #QUIT
      if "d quit" in m:
        for i in tempgames:
          if i == inv["stat:gameid"]:
            tempgames.pop(i)
            
            for user in master:
              if master[user]["stat:gameid"] == i:
                master[user]["stat:gameid"] = 0
                master[user]["stat:ingame"] = False
              response = "You have deleted your current game."
            
            break
        else:
          response = "You're not in a game"

      #COROUTINE MIMICKING ------------------------------------------
      
      if inv["stat:ingame"] == True and allowgame == True:
        #1.0 Shortcuts
        game = tempgames[inv["stat:gameid"]]
        rng = random.random()
        activeboard = game["board"].copy()
        for i in activeboard:
          if i.name == "hidden":
            activeboard.remove(i)
        activeboardcopy = activeboard.copy()
        if author == game["author"]:
          player = 0
          enemy = 1
          validrow = (1,2)
        else:
          player = 1
          enemy = 0
          validrow = (3,4)

        #Card reset command
        def newcard(name, quality):
          data = card_descriptions[name]
          cardtomake = Card(name, data[0], data[1], data[1], data[2], data[2], data[3], data[3], 1, 1, data[4], "none", 0, 0, 0, name, 1, "n", data[5], data[6], data[8])
          cardtomake.quality = quality
          return cardtomake

        #1.1 Stat buffs before a call
        for i in activeboard:
          i.attackbuff = 1
          i.ratebuff = 1
          
          #Maturity seed
          for test in activeboard:
            if test.row in validrow and test.name == "maturity_seed":
              i.ratebuff *= 1.35

          #Automated lunacy
          for test in activeboard:
            if test.row in validrow and test.name == "automated_lunacy":
              testdistance = abs(i.slot-test.slot)+abs(i.row-test.row)
              if testdistance == 1:
                i.ratebuff *= 0.75
                i.attackbuff *= 1.35
        
        #2.0 Your Hand Only
        if m == "d hand":
          response = "Your hand:\n"
          counter = 1
          for i in game["hand"][player]:
            response += "(" + str(counter) + ") " + i.name + "\n"
            counter += 1
          if response == "Your hand:\n":
            response = "Your hand is empty"

        #2.1 General info
        if m == "d info":
          passivename = ""
          if game["passive"][player] == None:
            passivename = "None"
          else:
            passivename = game["passive"][player].name
            if passivename == "hiding_is_fun":
              passivename += " (" + str(game["passive"][player].health) + " stealth)"
          response += "Passive: " + passivename + "\n"
          response += "Cards left in deck: " + str(len(game["deck"][player])) + "\n"
          response += "Points: " + str(game["point"][player]) + "\n"
          response += "Rate: " + str(round(game["rate"][player],1)) + "\n"
          response += "Glitter: " + str(game["glitter"][player]) + "\n"
        elif m in ("d enemy info", "d opponent info", "d info enemy", "d info opponent"):
          passivename = ""
          if game["passive"][enemy] == None:
            passivename = "None"
          else:
            passivename = game["passive"][enemy].name
            if passivename == "hiding_is_fun":
              passivename += " (" + str(game["passive"][enemy].health) + " stealth)"
          response += "Passive: " + passivename + "\n"
          response += "Cards left in deck: " + str(len(game["deck"][enemy])) + "\n"
          response += "Points: " + str(game["point"][enemy]) + "\n"
          response += "Rate: " + str(round(game["rate"][enemy],1)) + "\n"
          response += "Glitter: " + str(game["glitter"][enemy]) + "\n"

        #2.2 Graveyard info
        if m == "d graveyard":
          response = "Your graveyard:\n"
          counter = 1
          for i in game["graveyard"][player]:
            response += "(" + str(counter) + ") " + i.name + "\n"
            counter += 1
          if response == "Your graveyard:\n":
            response = "Your graveyard is empty"
        elif m in ("d enemy graveyard", "d opponent graveyard", "d graveyard enemy", "d graveyard opponent"):
          response = "Their graveyard:\n"
          counter = 1
          for i in game["graveyard"][enemy]:
            response += "(" + str(counter) + ") " + i.name + "\n"
            counter += 1
          if response == "Their graveyard:\n":
            response = "Their graveyard is empty"

        #2.3 Spirit bag info
        if m in ("d bag", "d spirit", "d spirit bag", "d spiritbag"):
          response = "Your spirit bag:\n"
          counter = 1
          for i in game["bag"][player]:
            response += "(" + str(counter) + ") " + i + " spirit\n"
            counter += 1
          if response == "Your spirit bag:\n":
            response = "Your spirit bag is empty"
        elif ("d" in ms) and ("enemy" in ms or "opponent" in ms) and ("bag" in ms or "spirit" in ms or "spiritbag" in ms):
          response = "Their spirit bag:\n"
          counter = 1
          for i in game["bag"][enemy]:
            response += "(" + str(counter) + ") " + i + " spirit\n"
            counter += 1
          if response == "Their spirit bag:\n":
            response = "Their spirit bag is empty"

        #2.4 Board Info
        if m == "d board info" or m == "d info board":
          response = "Event - " + game["event"] + " (" + str(game["eventtimer"]) + ")\n\n"
          bottomside = "Bottom side:"
          topside = "Top side:"
          indexedboard = {3 * (card.row - 1) + card.slot: card for card in game["board"]}
          organizedboard = sorted(indexedboard.items())
          finalboard = [i[1] for i in organizedboard]
          for i in finalboard:
            slotname = chr(i.slot+96)+str(i.row)
            if i.name != "hidden":
              linetoadd = "\n(" + slotname + ") " + i.name + ": " + str(round(i.attack * i.attackbuff)) + " ATK, " + str(i.health) + " HP, " + str(round(i.rate * i.ratebuff, 1)) + " Rate"
              if i.status != "none":
                linetoadd += ", " + status + " status (" + str(i.statustimer) + ")"
              if i.name == "luminous_tree":
                linetoadd += " (" + str(i.cooldown) + " Fruit)"
            else:
              linetoadd = "\n(" + slotname + ") Hidden"
            if i.row in (1,2):
              bottomside += linetoadd
            else:
              topside += linetoadd
          if bottomside == "Bottom side:":
            bottomside += "\nThis side is empty!"
          if topside == "Top side:":
            topside += "\nThis side is empty!"
          response += topside + "\n\n" + bottomside
        
        if game["turn"] == author:
          #3.0 Attack range utility function
          def attackrange(cardfrom, cardto, special = False):
            nonlocal game, rng, player, enemy, validrow, response, m, ms, ml

            if cardto == "direct":
              if game["turn"] == game["author"]:
                direct_location = 5
              else:
                direct_location = 0
              distance = abs(cardfrom.row-direct_location)
            else:
              distance = abs(cardfrom.slot-cardto.slot)+abs(cardfrom.row-cardto.row)
            
            if game["event"] == "calm night":
              distance += 1

            for test in activeboard:
              if test.row in validrow and test.name == "friendly_alien_glasses":
                testdistance = abs(i.slot-test.slot)+abs(i.row-test.row)
                if testdistance == 1:
                  distance -= 1

            if special and cardfrom.name == "ballista":
              distance -= 1

            return distance
            
          #3.1 Draw function
          def drawevent(callcase = "normal", data = None):
            nonlocal game, rng, player, enemy, validrow, response, m, ms, ml
            
            if callcase == "other":
              if game["deck"][enemy] == []:
                response += "The opponent's totem activated, but they have no cards left to draw\n"
              else:
                randomcard = random.choice(game["deck"][enemy])
                game["deck"][enemy].remove(randomcard)
                game["hand"][enemy].append(randomcard)
                response += "The opponent's totem activated, making them draw a card\n"
                response += "They have " + str(len(game["deck"][enemy])) + " cards left in their deck\n"
            else:
              if game["deck"][player] == []:
                response += "You have no cards left to draw\n"
              else:
                game["actioncounter"] -= 1
                randomcard = random.choice(game["deck"][player])
                game["deck"][player].remove(randomcard)
                game["hand"][player].append(randomcard)
                response += "You drew a card\n"
                response += "You have " + str(len(game["deck"][player])) + " cards left in your deck\n"

          #3.2 Pull function
          def pullevent(callcase = "normal", data = None):
            nonlocal game, rng, player, enemy, validrow, response, m, ms, ml
            game["actioncounter"] -= 1
            if rng < game["rate"][player]/100:
              game["point"][player] += 1
              response += "You sucessfully pulled a point\n"
            else:
              response += "You failed to pull a point\n"

          #3.3 Spell function
          def playspellevent(callcase = "normal", data = None):
            nonlocal game, rng, player, enemy, validrow, response, m, ms, ml, card
            owner = game["turn"]

            spirit = True

            if callcase == "normal":
              if card.spiritcost != "none":
                value = game["bag"][player]
                sorted_bag = {"red": value.count("red"), "blue": value.count("blue"), "green": value.count("green"), "black": value.count("black"), "any": 0}
                bagcopy = game["bag"][player].copy()
                for i, j in zip(sorted_bag, card.spiritcost):
                  if i == "any":
                    if len(bagcopy) < card.spiritcost[j]:
                      spirit = False
                  else:
                    if sorted_bag[i] < card.spiritcost[j]:
                      spirit = False
                      break
                    else:
                      for n in range(card.spiritcost[j]):
                        bagcopy.remove(j)

            if spirit:
              if callcase == "reveal":
                card = data

                if author == game["author"]:
                  owner = game["opponent"]
                else:
                  owner = game["author"]

                if game["passive"][owner].name == "hiding_is_fun":
                  game["passive"][owner].health -= 1

              if callcase == "normal":
                response += "Played " + card.name + "\n"

                if card.spiritcost != "none" and callcase == "normal":
                  game["bag"][player] = []
                  response += "Your spirit bag was emptied to play this card\n"

                game["hand"][player].remove(card)
                cardtoadd = newcard(card.name, card.quality)
                game["graveyard"][player].append(cardtoadd)
                game["actioncounter"] -= 1
              elif callcase == "reveal":
                response += "The revealed spellcard played itself\n"

              if card.name == "fresh_nights_on_a_distant_world":
                game["event"] = "calm night"
                game["eventtimer"] = 4
                response += "The calm night event has started\n"

              if card.name == "merciless_gale":
                if owner == game["author"]:
                  for targetcard in game["board"].copy():
                    targetcard.row += 1
                    print(targetcard.name + " " + str(targetcard.row))
                    if targetcard.row == 3:
                      game["board"].remove(targetcard)
                      cardtoadd = newcard(targetcard.identity, targetcard.quality)
                      game["graveyard"][1].append(cardtoadd)
                      if callcase == "reveal":
                        response += targetcard.name + " was blown into your board and destroyed\n"
                      else:
                        response += targetcard.name + " was blown into the enemy board and destroyed\n"
                    elif targetcard.row == 5:
                      cardtoadd = newcard(targetcard.identity, targetcard.quality)
                      game["hand"][1].append(cardtoadd)
                      game["board"].remove(targetcard)
                      if callcase == "reveal":
                        response += targetcard.name + " was blown off your board and returned to your hand\n"
                      else:
                        response += targetcard.name + " was blown off the enemy board and returned to the opponent's hand\n"
                else:
                  for targetcard in game["board"].copy():
                    targetcard.row -= 1
                    if targetcard.row == 2:
                      game["board"].remove(targetcard)
                      cardtoadd = newcard(targetcard.identity, targetcard.quality)
                      game["graveyard"][0].append(cardtoadd)
                      if callcase == "reveal":
                        response += targetcard.name + " was blown into your board and destroyed\n"
                      else:
                        response += targetcard.name + " was blown into the enemy board and destroyed\n"
                    elif targetcard.row == 0:
                      cardtoadd = newcard(targetcard.identity, targetcard.quality)
                      game["hand"][0].append(cardtoadd)
                      game["board"].remove(targetcard)
                      if callcase == "reveal":
                        response += targetcard.name + " was blown off your board and returned to your hand\n"
                      else:
                        response += targetcard.name + " was blown off the enemy board and returned to the opponent's hand\n"
            else:
              response += "You don't have the proper spirits to play that card\n"

          #3.4 Play unit function         
          def playunitevent(callcase = "normal", data = None):
            nonlocal game, rng, player, enemy, validrow, response, m, ms, ml, card

            spirit = True
            if card.spiritcost != "none":
              value = game["bag"][player]
              sorted_bag = {"red": value.count("red"), "blue": value.count("blue"), "green": value.count("green"), "black": value.count("black"), "any": 0}
              bagcopy = game["bag"][player].copy()
              for i, j in zip(sorted_bag, card.spiritcost):
                if i == "any":
                  if len(bagcopy) < card.spiritcost[j]:
                    spirit = False
                else:
                  if sorted_bag[i] < card.spiritcost[j]:
                    spirit = False
                    break
                  else:
                    for n in range(card.spiritcost[j]):
                      bagcopy.remove(j)
            
            if spirit:
              targetslot = ord(ms[3][0])-96
              targetrow = int(ms[3][1])
              if targetrow in validrow and targetslot in (1,2,3):
                for i in game["board"]:
                  if i.slot == targetslot and i.row == targetrow:
                    response = "There is already a card on that slot"
                    break
                else:
                  if card.name == "penguin" and targetrow in (2,3):
                    response = "The card can't be played there"
                  else:
                    if card.name == "luminous_tree":
                      card.cooldown = 0
                    cardname = card.name
                    card.slot = targetslot
                    card.row = targetrow
                    if ml == 5:
                      if ms[4] == "hidden":
                        card.name = "hidden"
                        cardname = "hidden card"

                        if game["passive"][player].name == "hiding_is_fun":
                          game["passive"][player].health += 1
                    game["board"].append(card)
                    game["hand"][player].remove(card)
                    game["actioncounter"] -= 1
                    response += "Played " + cardname + " on " + ms[3] + "\n"

                    if card.spiritcost != "none":
                      game["bag"][player] = []
                      response += "Your spirit bag was emptied to play this card\n"

                    if card.name == "hidden":
                      for enemycard in activeboard:
                        if enemycard.row not in validrow:
                          if enemycard.name == "amethyst_charm":
                            if rng < 3*(game["rate"][enemy]/100):
                              response += "Amethyst charm revealed the card's identity: " + card.name + "\n"
                            break
              else:
                response += "You can only play cards on your board\n"
            else:
              response += "You don't have the proper spirits to play that card\n"

          #3.5 Flip function
          def flipevent(callcase = "normal", data = None):
            nonlocal game, rng, player, enemy, validrow, response, m, ms, ml

            targetslot = ord(ms[2][0])-96
            targetrow = int(ms[2][1])
            if targetrow in validrow and targetslot in (1,2,3):
              for i in game["board"]:
                if i.slot == targetslot and i.row == targetrow:
                  if i.name == "hidden":
                    i.name = i.identity
                    response += "Flipped up " + i.name + " on " + ms[2] + "\n"

                    #Veil of blindness
                    for test in activeboard:
                      if test.row in validrow and test.name == "veil_of_blindness":
                        testdistance = abs(i.slot-test.slot)+abs(i.row-test.row)
                        if testdistance == 1:
                          game["actioncounter"] += 1
                          response += "An action was not used because of veil of blindness"
                  else:
                    response += "Flipped down " + i.name + " on " + ms[2] + "\n"
                    i.name = "hidden"

                    if i.category == "spell":
                      playspellevent("reveal", i)
                      game["board"].remove(i)
                  
                  game["actioncounter"] -= 1
                  break
              else:
                response = "You don't have a card on that slot"
            else:
              response = "You can only flip cards on your board"
          
          #3.6 Destroy function
          def destroyevent(callcase = "normal", data = None):
            nonlocal game, rng, player, enemy, validrow, response, m, ms, ml

            targetslot = ord(ms[2][0])-96
            targetrow = int(ms[2][1])
            if targetrow in validrow and targetslot in (1,2,3):
              for i in game["board"]:
                if i.slot == targetslot and i.row == targetrow:
                  game["actioncounter"] -= 1
                  game["board"].remove(i)
                  cardtoadd = newcard(i.identity, i.quality)
                  game["graveyard"][player].append(cardtoadd)
                  categorytocolor = {"offense": "red", "defense": "blue", "producer": "green", "spell": "black"}
                  game["bag"][player].append(categorytocolor[i.category])
                  if len(game["bag"][player]) > 3:
                    game["bag"][player].pop(0)
                  response += "You destroyed that card, releasing a " + categorytocolor[i.category] + " spirit\n"

                  if game["passive"][player].name == "hiding_is_fun":
                    game["passive"][player].health -= 1
                  
                  if i.identity == "abandoned_marketplace":
                    response += "The destroyed card was a marketplace, making you lose 3.0 rate\n"
                    game["rate"][player] -= 3
                  
                  break
              else:
                response = "You don't have a card on that slot"
            else:
              response = "You can only destroy cards on your board"

          #3.7 Direct attack function (A special branch of targeted interact)
          def directattackevent(callcase = "normal", data = None):
            nonlocal game, rng, player, enemy, validrow, response, m, ms, ml, i
            
            if i.attack > 0:
              if special == False:
                cards_all_gone = True
                for j in game["board"]:
                  if j.row not in validrow:
                    cards_all_gone = False
                    break
                if cards_all_gone:
                  distance = attackrange(i, "direct")
                  
                  if distance <= 1:
                    damage_multiplier = 1
                  elif distance == 2:
                    damage_multiplier = 0.5
                  elif distance == 3:
                    damage_multiplier = 0.25
                  else:
                    damage_multiplier = 0

                  damage_multiplier *= i.attackbuff
                  
                  damage = round(i.attack * damage_multiplier, 1)
                  
                  if damage == 0:
                    response = "Either you lack attack range or can't deal damage to that unit"
                  else:
                    game["rate"][player] += damage
                    game["rate"][enemy] -= damage

                    i.cooldown = 0

                    response += "You hit a direct attack, stealing " + str(damage) + " rate from them\n" 
                else:
                  response = "The enemy still has units on their board"
              else:
                response = "Direct attacks cannot be special attacks"
            else:
              response = "This card can't attack"

          #3.8 Attack function (A special branch of targeted interact)
          def attackevent(callcase = "normal", data = None):
            nonlocal game, rng, player, enemy, validrow, response, m, ms, ml, i, j

            if callcase != "normal":
              j = data
            
            if i.attack > 0:
              defended = False
              if j.row in (1,4):
                for h in game["board"]:
                  if h.row not in validrow and h.slot == j.slot and h.row in (2,3):
                    defended = True
                    break
              if i.name == "ballista" and i.slot != j.slot:
                response = "Ballista can only attack in the same column"
              elif defended == False or i.name == "ballista":
                can_afford = True
                
                if special and i.specialmode not in ("target", "both"):
                  response = "This unit doesn't have a targeted special ability"
                else:
                  if special:
                    if game["glitter"][player] < i.specialcost:
                      can_afford = False
                      response = "You don't have enough glitter to do a special attack with this unit"
                  if can_afford:
                    if j.name == "hidden":
                      distance = attackrange(i, j, special)
                      if distance < 4:
                        j.name = j.identity
                        if special:
                          response += "Special attacking a hidden card wouldn't do anything special, so a normal attack was done instead\n"
                        response += i.name + " hits a hidden card, flipping it and revealing it was " + j.name + "\n"
                        if j.category == "spell":
                          game["board"].remove(j)
                          cardtoadd = newcard(j.name, j.quality)
                          game["graveyard"][enemy].append(cardtoadd)
                          playspellevent("reveal", j)
                      else:
                        response += "That hidden card is too far away\n"
                    else:
                      distance = attackrange(i, j, special)
                      
                      if distance <= 1:
                        damage_multiplier = 1
                      elif distance == 2:
                        damage_multiplier = 0.5
                      elif distance == 3:
                        damage_multiplier = 0.25
                      else:
                        damage_multiplier = 0

                      damage_multiplier *= i.attackbuff

                      #Hiding is fun
                      if game["passive"][enemy].name == "hiding_is_fun":
                        damage_multiplier *= 0.92 - (0.04 * game["passive"][enemy].health)

                      damage = round(i.attack * damage_multiplier)

                      if damage == 0:
                        response = "Either you lack attack range or can't deal damage to that unit"
                      else:
                        #Special attacks (Before calculation)
                        rngevent = False
                        if special:
                          game["glitter"][player] -= i.specialcost
                          baserate = game["rate"][player]/100
                          
                          if i.name == "king_cobra":
                            if rng < 3*baserate:
                              damage = j.health
                              rngevent = True
                        
                        #Base damage calculation and cooldown
                        j.health -= damage
                        response += i.name + " hits " + j.name + " and deals " + str(damage) + " damage\n"
                        i.cooldown = 0
                        
                        #Special attacks (After calculation)
                        if special:
                          if i.name == "penguin":
                            if rng < 3*baserate:
                              j.status = "freeze"
                              j.statustimer = 2
                              response += "The attacked card has been frozen!\n"
                          
                          if i.name == "earthen_mess":
                            i.health += damage
                            response += "Your unit has healed by lifesteal\n"

                          if i.name == "king_cobra" and rngevent:
                            response += "You dealt a fatal hit\n"

                        #Forgotten totem
                        if j.name == "forgotten_totem":
                          if rng < 2*(game["rate"][enemy]/100):
                            drawevent("other")
                        
                        #Luminous tree
                        if j.name == "luminous_tree":
                          j.cooldown = 0

                        #Automated lunacy
                        if j.name == "automated_lunacy":
                          response += "Both players lost 1.0 rate\n"
                          game["rate"][player] -= 1
                          game["rate"][enemy] -= 1                   

                        #Card death
                        if j.health <= 0:
                          #Sturdy wall
                          if j.name == "sturdy_wall" and rng < game["rate"][enemy]/100:
                            j.health = 1
                            response += "The attacked card has endured and been left with 1 health\n"
                          else:
                            game["board"].remove(j)
                            cardtoadd = newcard(j.name, j.quality)
                            game["graveyard"][enemy].append(cardtoadd)
                            response += j.name + " has been destroyed\n"

                            #Abandoned marketplace
                            for test in activeboard:
                              if test.name == "abandoned_marketplace":
                                if rng < test.health / test.maxhealth:
                                  if test.row in validrow:
                                    game["glitter"][player] += 3
                                    response += "A marketplace on your side gave you 3 glitter\n"
                                  else:
                                    game["glitter"][enemy] += 3
                                    response += "A marketplace on enemy side gave them 3 glitter\n"
                                else:
                                  if test.row in validrow:
                                    game["rate"][player] -= 0.5
                                    response += "A marketplace on your side made you lose 0.5 rate\n"
                                  else:
                                    game["rate"][enemy] -= 0.5
                                    response += "A marketplace on enemy side made them lose 0.5 rate\n"

                            #Void grass
                            if j.name == "void_grass":
                              game["deck"][enemy].append(cardtoadd)
                              response += "The card has been returned to their deck\n"

                            #Decoy servant
                            if j.name == "decoy_servant":
                              for card in game["deck"][enemy]:
                                if card.category == "offense":
                                  game["hand"][enemy].append(card)
                                  game["deck"][enemy].remove(card)
                                  response += "An offense card from the enemy's deck has been added to their hand\n"
                                  break
                              else:
                                response += "The enemy has no offense cards left in their deck, so decoy servant's ability cannot activate\n"

                            #Hiding is fun
                            if game["passive"][enemy].name == "hiding_is_fun":
                              game["passive"][enemy].health -= 1
              else:
                response = "This unit is defended by another unit in front of it"
            else:
              response = "This card can't attack"

          #3.9 Interact function (Use callcase to change between target and targetless)
          def interactevent(callcase = "normal", data = None):
            nonlocal game, rng, player, enemy, validrow, response, m, ms, ml, i
            interacted = True
            validmodes = ("targetless", "both")
            
            if callcase == "target":
              validmodes = ("target", "both")
            
            if special and i.specialmode not in validmodes:
              if callcase == "target":
                response = "This unit doesn't have a targeted special ability"
              else:
                response = "This unit doesn't have a targetless special ability"
            else:
              can_afford = True

              if special:
                if game["glitter"][player] < i.specialcost:
                  can_afford = False
                  response = "You don't have enough glitter to do a special ability with this unit"
              if can_afford:
                if special:
                  game["glitter"][player] -= i.specialcost
                  baserate = game["rate"][player]/100

                  if i.name == "sugar_mine":
                    response += "Sugar mine has detonated\n"
                    hitsomething = False
                    for enemycard in game["board"]:
                      if enemycard.row not in validrow and enemycard.row in (2,3):
                        attackevent("sugar_mine", enemycard)
                        hitsomething = True
                    if hitsomething == False:
                      response += "Huh, but it didn't hit anything\n"
                    game["board"].remove(i)
                    cardtoadd = newcard(i.name, i.quality)
                    game["graveyard"][player].append(cardtoadd)
                  elif i.name == "automated_lunacy":
                    i.slot = data[0]
                    i.row = data[1]
                    response += "Automated lunacy has moved to that slot\n"
                else:
                  if i.name == "luminous_tree":
                    luminous_tree_data = {1: [0.3, 0], 2: [0.6, 1], 3: [1.0, 3], 4: [1.8, 5], 5: [3.5, 8]}
                    rate_gained = luminous_tree_data[i.cooldown][0]
                    glitter_gained = luminous_tree_data[i.cooldown][1]
                    game["rate"][player] += rate_gained
                    game["glitter"][player] += glitter_gained
                    response += "You harvest all the fruit, gaining " + str(rate_gained) + " rate and " + str(glitter_gained) + " glitter\n"
                  else:
                    interacted = False
                    response = "You can't interact with this card in this way"
                if interacted == True:
                  i.cooldown = 0

          #4.0 Call actions
          if game["actioncounter"] > 0:
            
            #Draw a card
            if m == "d draw":
              drawevent()
            
            #Pull a point
            if m == "d pull":
              pullevent()

            #Play a card
            if "d play" in m:
              handslot = int(ms[2])
              card = game["hand"][player][handslot-1]
              
              if card.category == "spell" and ml == 3:
                playspellevent()
              else:
                playunitevent()

            #Flip a card
            if "d flip" in m:
              flipevent()

            #Destroy a card
            if "d destroy" in m:
              destroyevent()
            
          elif "d pull" in m or "d play" in m or "d flip" in m or "d draw" in m or "d destroy" in m:
            response = "You already did 2 actions"

          #4.1 Call interactions
          if "d interact" in m or "d special" in m:
            if game["interact_allowed"][player]:
              special = False
              if ms[1] == "special":
                special = True
              
              targetslot = ord(ms[2][0])-96
              targetrow = int(ms[2][1])

              if targetrow in validrow and targetslot in (1,2,3):
                for i in game["board"]:
                  if i.slot == targetslot and i.row == targetrow:
                    if i.name != "hidden":
                      if i.cooldown != 0:
                        if i.status != "freeze":
                          if ml == 4:
                            if ms[3] == "direct":
                              directattackevent()
                            else:
                              enemyslot = ord(ms[3][0])-96
                              enemyrow = int(ms[3][1])
                              moveabilities = ("automated_lunacy")
                              if i.name in moveabilities and special:
                                if enemyrow in validrow and enemyslot in (1,2,3):
                                  testdistance = abs(i.slot-enemyslot)+abs(i.row-enemyrow)
                                  cardthere = False
                                  for test in game["board"]:
                                    if test.row == enemyrow and test.slot == enemyslot:
                                      cardthere = True
                                      break
                                  if testdistance == 1 and cardthere == False:
                                    interactevent("target", [enemyslot, enemyrow])
                                  else:
                                    response = "You tried moving it to a space too far away, or there's something already there"
                                else:
                                  response = "This card's special ability only lets it move to a space on your board"
                              elif enemyrow not in validrow and enemyslot in (1,2,3):
                                for j in game["board"]:
                                  if j.slot == enemyslot and j.row == enemyrow:
                                    attackevent()
                                    break
                                else:
                                  response = "There's no card on the slot you're trying to attack"
                              else:
                                repsonse = "You can only attack a card on the enemy board"
                          else:
                            interactevent()
                        else:
                          response = "This card is frozen"
                      else:
                        response = "You already interacted with this card this turn"
                    else:
                      response = "This is a hidden card that can't do anything"
                    break
                else:
                  response = "You don't have a card on that slot"
              else:
                response = "You can only interact with a card on your board"
            else:
              response = "You can't interact with cards on your first turn"

          #5.0 End turn
          if m == "d end turn":
            rategain = 0
            glitteramount = 0
            glittergain = 0
            
            #Reset action counter
            game["actioncounter"] = 2

            #Count down events
            if game["event"] != "none":
              game["eventtimer"] -= 1
              if game["eventtimer"] <= 0:
                game["eventtimer"] = 0
                game["event"] = "none"

            #Remove first turn restrictions
            if game["interact_allowed"][player] == False:
              game["interact_allowed"][player] = True

            #Maturity seed
            for i in activeboardcopy:
              if i.row in validrow and i.name == "maturity_seed":
                glitteramount += 1

            #Go through every card, calculate rate, count down debuffs, etc
            for i in activeboard:
              if i.row in validrow:
                #Luminous tree
                if i.name == "luminous_tree":
                  if i.cooldown < 5:
                    i.cooldown += 1
                else:
                  i.cooldown = 1
                
                #Blueberry oatmeal
                if game["passive"][player].name == "blueberry_oatmeal":
                  i.health += 1

                #Maturity seed
                if i.category == "producer":
                  glittergain += glitteramount

                rategain += i.rate * i.ratebuff

                if i.status != "none":
                  i.statustimer -= 1
                  if i.statustimer <= 0:
                    i.statustimer = 0
                    i.status = "none"
            
            #Blueberry oatmeal
            if game["passive"][player].name == "blueberry_oatmeal":
              rategain += 1

            game["rate"][player] += rategain
            game["glitter"][player] += glittergain

            #Change who has turn
            if game["turn"] == game["author"]:
              game["turn"] = game["opponent"]
            else:
              game["turn"] = game["author"]

            #Response
            response = "You ended your turn\n"
            response += "Your cards have earned you " + str(round(rategain, 1)) + " rate and " + str(glittergain) + " glitter on the end of this turn\n"
            response += "<@" + str(game["turn"]) + ">" + " it's your turn now\n"
            
        else:
          for i in ["d destroy", "d draw", "d pull", "d play", "d flip", "d interact", "d special", "d end"]:
            if i in m:
              response = "It's not your turn yet"
              break

        #6.0 Rate reset
        index = 0
        for rate in game["rate"]:
          if rate > 100:
            game["rate"][index] = 100
          elif rate < 0:
            game["rate"][index] = 0
          index += 1

        #6.1 Hiding is fun reset
        index = 0
        for passive in game["passive"]:
          if passive.name == "hiding_is_fun" and passive.health < 0:
            game["passive"][index].health = 0
          index += 1
        
        #7.0 Save game and check if it ends
        tempgames[inv["stat:gameid"]] = game
        
        if game["point"][0] >= 5 or game["point"][1] >= 5:
          for i in tempgames:
            if i == inv["stat:gameid"]:
              tempgames.pop(i)
              
              for user in master:
                if master[user]["stat:gameid"] == i:
                  master[user]["stat:gameid"] = 0
                  master[user]["stat:ingame"] = False    
              break
          if game["point"][0] >= 5:
            name = await client.fetch_user(game["author"])
            name = str(name)[:-5]
            response += "\nThe game is over, " + name + " has won"
          else:
            name = await client.fetch_user(game["opponent"])
            name = str(name)[:-5]
            response += "\nThe game is over, " + name + " has won"

    #general error branch
    elif response == "":
      response = "if you tried using a game command, make sure you have joined. otherwise, your command is invalid!"
    if response == "":
      response = "command invalid! you wrote something wrong or tried to reference a user who has not joined. also check to see if you are using the command correctly with the right amount of terms."
    await message.channel.send(response)
  
  #save everything
  asyncio.create_task(save())

#This is the last line, which actually runs the bot.
client.run(TOKEN)
