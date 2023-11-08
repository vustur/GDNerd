import openai, json, gd, os, random, asyncio, time, colorama

openai.api_key = "???"
openai.api_base = "???"
client = gd.Client()
isLogined = False
gdchars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789,.!?-#*()_ :;/"
waitaftercomment = 15 # how much time in seconds to wait after comment (use if your api limited)

inputClr = colorama.Fore.MAGENTA
errClr = colorama.Fore.RED
warnClr = colorama.Fore.YELLOW
succClr = colorama.Fore.GREEN
proxClr = colorama.Fore.CYAN
reset = colorama.Style.RESET_ALL

# EiRk29wk 

async def login():
  await getProxy()
  global isLogined
  while True:
    print("Logining...")
    isLogined = False
    try:
      await client.login("???", "???")
      isLogined = True
      break  # Exit the loop if login is successful
    except Exception as Err:
      print(errClr + "Error while logging in: " + str(Err) + reset)
      print("Retrying...")
      await getProxy()

async def askGpt(prompt):
  try:
    req = openai.ChatCompletion.create(
      stream = False,
      model = "gpt-3.5",
      messages=[
        {
          "role": "user",
          "content": prompt,
          }
      ]
    )
    rp = req.choices[0].message.content
    return rp
  except Exception as Err:
    print(errClr + "Error while asking GPT: " + str(Err) + reset)
    return "error"

async def checkProxy(): # check if proxy is valid on boomlings
  print("Starting check...")
  with open('proxy.txt', 'r') as file:
    allprox = [line.strip() for line in file]
    
  valids = []
  validCnt = 0
  totalCnt = len(allprox)
  startTime = time.time()
  checkedCnt = 0
  
  for proxy in allprox:
    checkedCnt += 1
    print(f" --------- \nChecking proxy: " + proxClr + f"{proxy}" + reset)
    try:
      client.http.proxy = proxy
      level = await client.get_level(128)
      print(succClr + f"Proxy is valid: {proxy} ({level.name} should be 1st level)")
      validCnt += 1
      print(f" ++++ {reset}Total valid is {validCnt} / {totalCnt} \n")
      valids.append(proxy)
    except Exception as err:
      print( errClr + f"Proxy is not valid: {proxy} Error: {err}")
      print(f" xxxx {reset}Valid {validCnt} / Total {totalCnt} / Checked {checkedCnt}  \n")
    elapsed_time = time.time() - startTime
    average_time = elapsed_time / checkedCnt
      
    print(f"Elapsed time: {elapsed_time:.2f} seconds\nAverage time per proxy: {average_time:.2f} seconds \nRemaining time: {average_time * (totalCnt - checkedCnt):.2f} seconds \n --------- \n")

  with open('valid_proxy.txt', 'w') as file:
    file.write('\n'.join(valids))

  print(f"Valid proxies: {valids}")
    
async def getProxy():
  with open("valid_proxy.txt", "r") as file:
      proxies = file.readlines()
  randproxy = random.choice(proxies).strip()
  print(proxClr + "Using proxy: " + randproxy + reset)
  client.http.proxy = randproxy

async def commentLevel(lvlid, comment):
  for i in range(5):
    if not isLogined:
      await login()
    print("Commenting " + str(lvlid) + " with comment: " + comment)
    try:
      level = await client.get_level(lvlid)
      await client.comment_level(level, comment, random.randint(20, 85))
      print(succClr + "Commented!" + reset)
      break  # Exit the loop if commenting is successful
    except Exception as Err:
      print(errClr + "Error while commenting: " + str(Err))
      print("Retrying..." + reset)
      await getProxy()

async def getRecent():
  while True:
    try:
      print("Getting recents")
      recentlvls = await client.search_levels(filters=gd.Filters(strategy=4))
      print(succClr + "Got recents" + reset)
      if recentlvls == []:
        raise Exception("Resents returned empty!")
      lvlid = recentlvls[0].id
      print(succClr + "Getting level: " + str(lvlid) + reset)
      level = await client.get_level(lvlid)
      levelname = level.name
      leveldesc = level.description
      levelsongname = level.song.name
      levelsongid = level.song.id
      levelcreator = level.creator.name
      levellenght = level.length
      return {"level": level, "name": levelname, "desc": leveldesc, "song": levelsongname, "songid": levelsongid, "creator": levelcreator, "length": levellenght}
    except Exception as Err:
      print(errClr + "Error occurred on getting recent: " + str(Err))
      print("Retrying..." + reset)
      await getProxy()

async def main():
  loopcount = input(inputClr + "Enter loop count: " + colorama.Style.RESET_ALL)
  if not loopcount.isdigit():
    print(errClr + "Not int" + reset)
    time.sleep(3)
    return
  loopcount = int(loopcount)
  for i in range(loopcount):
    print(inputClr + "Loop: " + str(i + 1) + " / " + str(loopcount) + reset)
    lvl = await getRecent()
    print(" ------------\n Data: \n - Name: " + lvl['name'] + "\n - Creator: " + lvl['creator'] + "\n - Description: " + lvl['desc'] + "\n - Length: " + str(lvl['length']) + "\n - Song: " + lvl['song'] + " (" + str(lvl['songid']) + ")\n ")
    prompt = f"You are going to comment geometry dash (game) level! You should write a very funny and ORIGINAL (it should not look like your other comments!) joke or comment about the level with name {lvl['name']} created by {lvl['creator']} with description '{lvl['desc']}' and song {lvl['song']} like you are beginner player. REMEMBER: your joke or comment should be not longer than 100 characters, so it should be very short (geometry dash limit)! Your joke or comment also should be funny, include something about name, description or song and not look like it was written by chat gpt. You can use some of this words (NOT ALL IN ONE joke or comment): ship, ball, cube, wave, ufo, hardest part, straightfly, spikes, blockdesign, deco, GD (short name of game), other players, robtop(gd developer), rate(process when gd level get stars by moderators). Example: 'Actually good level! Ball part was so cool' REMEMBER: your joke or comment should be not longer than 100 chars, so it should be very short (geometry dash limit), include something about name, description or song and it should be original(not like 'wild ride' or 'rollercoaster')! MOST IMPORTANT RULE: YOU SHOULD JUST RETURN A joke or comment WITHOUT CONTEXT"
    response = await askGpt(prompt)
    if response == "error":
      print(errClr + "Error with response. Level skipped" + reset)
      continue
    print("Response: " + response)
    response = ''.join(char for char in response if char in gdchars)
    if len(response) > 100:  # gd comment limit is 100 chars :(
      lastspace = response.rfind(" ", 0, 97)
      response = response[:lastspace] + "..."
    if response.startswith("Comment: "):
      response = response[9:]
    print("Response (for GD): " + response)
    await commentLevel(lvl['level'].id, response)
    if waitaftercomment > 0 and i != loopcount:
      print(" ------------ \n Waiting " + str(waitaftercomment) + " seconds to continue...")
      time.sleep(waitaftercomment)
    
  print(succClr + "\n Done! \n Thanks for using GDNerd :) " + reset)
  time.sleep(5)
  
async def modeSwitcher():
  while True:
    print("Choose option")
    print("[1] Start GDNerd")
    print("[2] Check proxies\n")
    choose = input(inputClr + "Mode: " + reset)
    if choose == "2":
      await checkProxy()
    elif choose == "1":
      await login()
      await main()
    else:
      print(errClr + "Invalid option" + reset)

asyncio.run(modeSwitcher())

# ftp test!!