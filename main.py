import openai, gd, random, asyncio, time, colorama, os
import config as cfg

client = gd.Client()
gptclient = openai.OpenAI(
  api_key=cfg.gptkey,
  base_url=cfg.gptbase
)
isLogined = False
gdchars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789,.!?-#*()_ :;/" # Other characters will be removed
waitaftercomment = cfg.waitaftercomment
currpath = os.path.dirname(__file__)
validproxypath = currpath + "/valid_proxy.txt"
allproxypath = currpath + "/proxy.txt"

if cfg.useColors:
  inputClr = colorama.Fore.MAGENTA
  errClr = colorama.Fore.RED
  warnClr = colorama.Fore.YELLOW
  succClr = colorama.Fore.GREEN
  proxClr = colorama.Fore.CYAN
  reset = colorama.Style.RESET_ALL
else:
  inputClr = ""
  errClr = ""
  warnClr = ""
  succClr = ""
  proxClr = ""
  reset = ""

async def login():
  await getProxy()
  global isLogined
  while True:
    print("Logining...")
    isLogined = False
    try:
      await client.login(cfg.username, cfg.password)
      isLogined = True
      break  # Exit the loop if login is successful
    except Exception as Err:
      print(errClr + "Error while logging in: " + str(Err) + reset)
      print("Retrying...")
      await getProxy()

async def askGpt(prompt):
  try:
    req = gptclient.chat.completions.create(
      stream = False,
      model = cfg.gptmodel,
      messages=[
        {
          "role": "user",
          "content": prompt,
          }
      ]
    )
    return req.choices[0].message.content
  except Exception as Err:
    print(errClr + "Error while asking GPT: " + str(Err) + reset)
    return "error"

async def checkProxy(): # check if proxy is valid on boomlings
  print("Starting check...")
  with open(allproxypath, 'r') as file:
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
      await asyncio.wait_for(client.get_level(128), timeout=8)
      print(succClr + f"Proxy is valid: {proxy}")
      validCnt += 1
      print(f" ++++ {reset}Total valid is {validCnt} / {totalCnt} \n")
      valids.append(proxy)
    except Exception as err:
      print( errClr + f"Proxy is not valid: {proxy} Error: {err}")
      print(f" xxxx {reset}Valid {validCnt} / Total {totalCnt} / Checked {checkedCnt}  \n")
    elapsed_time = time.time() - startTime
    average_time = elapsed_time / checkedCnt
      
    print(f"Elapsed time: {elapsed_time:.2f} seconds\nAverage time per proxy: {average_time:.2f} seconds \nRemaining time: {average_time * (totalCnt - checkedCnt):.2f} seconds \n --------- \n")

  with open(validproxypath, 'w') as file:
    file.write('\n'.join(valids))

  print(f"Valid proxies: {valids}")
  input(inputClr + "Enter to exit" + reset)
    
async def getProxy():
  with open(validproxypath, "r") as file:
      proxies = file.readlines()
  randproxy = random.choice(proxies).strip()
  print(proxClr + "Using proxy: " + randproxy + reset)
  client.http.proxy = randproxy

async def commentLevel(lvlid, comment):
  isSucc = False
  for i in range(2):
    if not isLogined:
      await login()
    print("Commenting " + str(lvlid) + " with comment: " + comment)
    try:
      level = await client.get_level(lvlid)
      await asyncio.wait_for(client.comment_level(level, comment, random.randint(20, 85)), timeout=cfg.maxWaitTime)
      print(succClr + "Commented!" + reset)
      isSucc = True  
      return isSucc # Exit the loop if commenting is successful
    except gd.MissingAccess as Err:
      print(errClr + "GD Error! (Probably commenting too fast, empty comment or level delated) : " + str(Err) + "  Nothing to do.. Skipping" + reset)
      return isSucc
    except asyncio.TimeoutError:
      print(errClr + "Commenting timed out (proxy is " + client.http.proxy + ")")
      print("Retrying..." + reset)
      await getProxy()
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
      await asyncio.wait_for(client.get_level(lvlid), timeout=cfg.maxWaitTime)
      levelname = level.name
      leveldesc = level.description
      levelsongname = level.song.name
      levelsongid = level.song.id
      levelcreator = level.creator.name
      levellenght = level.length
      return {"level": level, "name": levelname, "desc": leveldesc, "song": levelsongname, "songid": levelsongid, "creator": levelcreator, "length": levellenght}
    except asyncio.TimeoutError:
      print(errClr + "Getting recent timed out (proxy is " + client.http.proxy + ")")
      print("Retrying..." + reset)
      await getProxy()
    except Exception as Err:
      print(errClr + "Error occurred on getting recent: " + str(Err))
      print("Retrying..." + reset)
      await getProxy()

async def main():
  succLoops = 0
  if cfg.username == "none" or cfg.password == "none" or cfg.gptkey == "none" or cfg.gptbase == "none":
    print(f"{errClr}Configure config.py ({inputClr}username, password, gptkey, gptbase{errClr} is required){reset}")
    time.sleep(3)
    return
  await login()
  loopcount = input(inputClr + "Enter loop count: " + reset)
  if not loopcount.isdigit():
    print(errClr + "Not int" + reset)
    time.sleep(3)
    return
  loopcount = int(loopcount)
  for i in range(loopcount):
    print(inputClr + "Loop: " + str(i + 1) + " / Succ: " + str(succLoops) + " / " + str(loopcount) + reset)
    lvl = await getRecent()
    print(" ------------\n Data: \n - Name: " + lvl['name'] + "\n - Creator: " + lvl['creator'] + "\n - Description: " + lvl['desc'] + "\n - Length: " + str(lvl['length']) + "\n - Song: " + lvl['song'] + " (" + str(lvl['songid']) + ")\n ")
    prompt = f"You are going to comment geometry dash (game) level! You should write a very funny and ORIGINAL (it should not look like your other comments!) joke or comment about the level with name {lvl['name']} created by {lvl['creator']} with description '{lvl['desc']}' and song {lvl['song']} like you are beginner player. REMEMBER: your joke or comment should be not longer than 100 characters, so it should be very short (geometry dash limit)! Your joke or comment also should be funny, include something about name, description or song and not look like it was written by chat gpt. You can use some of this words (NOT ALL IN ONE joke or comment): ship, ball, cube, wave, ufo, hardest part, straightfly, spikes, blockdesign, deco, GD (short name of game), other players, robtop(gd developer), rate(process when gd level get stars by moderators), touch grass, vsc (hardest wave level), stereo madness(first main geometry dash level), back on track(second main geometry dash level), version 2.2(upcoming geometry dash version, not releasing in 8 years). Example: 'Actually good level! Ball part was so cool' REMEMBER: your joke or comment should be not longer than 100 chars, so it should be very short (geometry dash limit), include something about name, description or song and it should be original(not like 'wild ride' or 'rollercoaster')! MOST IMPORTANT RULE: YOU SHOULD JUST RETURN A joke or comment WITHOUT CONTEXT"
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
    isCommented = await commentLevel(lvl['level'].id, response)
    if isCommented:
      print(succClr + "Look like everything is fine.." + reset)
      succLoops += 1
    else:
      print(errClr + "Something went wrong with commenting.." + reset)
    if waitaftercomment > 0 and i != loopcount and isCommented:
      print(" ------------ \n Waiting " + str(waitaftercomment) + " seconds to continue...")
      time.sleep(waitaftercomment)
    elif waitaftercomment > 0 and i != loopcount and not isCommented:
      print(" ------------ \n Comment not posted, so no need to wait...")
    
  print(succClr + "\n Done! \n Thanks for using GDNerd :) " + reset)
  input(inputClr + "Enter to exit" + reset)
  
def clearConsole():
  os.system('cls' if os.name == 'nt' else 'clear')
  
async def modeSwitcher():
  while True:
    clearConsole()
    print(f"\n\n{succClr}Welcome to GDNerd, made by Vustur. {reset}\nChoose mode:")
    print("[1] Start GDNerd on recents")
    print("[9] Check proxies\n")
    choose = input(inputClr + "Mode: " + reset)
    match choose:
      case "1":
        await main()
      case "9":
        await checkProxy()
      case _:
        print(errClr + "Wrong mode" + reset)
        time.sleep(1.5)

asyncio.run(modeSwitcher())
