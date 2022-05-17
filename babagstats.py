import json, requests, time, argparse
from datetime import datetime

# args
parser = argparse.ArgumentParser(description='get forsen babag stats')
parser.add_argument('--datasource', type=str, required=False, help='pull from [file, web] (default: file)', default='file')
parser.add_argument('--showStats', type=bool, required=False, help='output stats during runtime (default: True)', default=True)
parser.add_argument('--genReadme', type=bool, required=False, help='generate readme (default: True)', default=True)
parser.add_argument('--earliestyear', type=int, required=False, help='earliest year cutoff (default: 2021)', default=2021)
parser.add_argument('--earliestmonth', type=int, required=False, help='earliest month cutoff (default: 1)', default=1)
parser.add_argument('--numgamesonmap', type=int, required=False, help='num games needed on a map to put in readme (default: 10)', default=10)
parser.add_argument('--requesttimeout', type=float, required=False, help='api request timeout (default: 0.1)', default=0.1)
args = parser.parse_args()


date_cutoff = datetime(args.earliestyear, args.earliestmonth, 1)
num_games_on_map_cutoff = args.numgamesonmap

requestTimeout = args.requesttimeout

date_fmt = '%Y-%m-%dT%H:%M:%S+0000'

mapNameTranslate = {
  "Baltic_Main": "Erangel (Remastered)",
  "Chimera_Main": "Paramo",
  "Desert_Main": "Miramar",
  "DihorOtok_Main": "Vikendi",
  "Erangel_Main": "Erangel",
  "Heaven_Main": "Haven",
  "Range_Main": "Camp Jackal",
  "Savage_Main": "Sanhok",
  "Summerland_Main": "Karakin",
  "Tiger_Main": "Taego"
}

mapImgTranslate = {
    "Baltic_Main": "Pubg_erangel_new.jpg",
    "Chimera_Main": "", # dont think this is used anymore
    "Desert_Main": "Miramar_EN.webp",
    "DihorOtok_Main": "Vikendi_Map.webp",
    "Erangel_Main": "Pubg_erangel_new.jpg", # looks the same 2 me
    "Heaven_Main": "Heaven_Minimap.webp",
    "Range_Main": "", # tutorial map
    "Savage_Main": "Sanhok-map.webp",
    "Summerland_Main": "Karakin_Map.webp",
    "Tiger_Main": "taego.jpg"
  }


def pullLatestStats():
    url = 'https://pubg.op.gg/api/users/59fe352b55aa60000188a0fb/matches/recent?queue_size=1&mode=fpp&type=official'
    after = '&after='
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.67 Safari/537.36',
    }
    all_games = json.loads(requests.get(url, headers=headers).content)['matches']['items']
    num_matches = len(all_games)
    last_match_offset = all_games[-1]['offset'] # base64 encoded str

    while num_matches == 20:
        response = json.loads(requests.get(url + after + last_match_offset, headers=headers).content)['matches']['items']
        all_games.extend(response)
        num_matches = len(response)
        last_match_offset = response[-1]['offset']
        time.sleep(requestTimeout) # just in case

    with open('fullGameData.json', 'w') as outfile:
        json.dump(all_games, outfile)

def getKillsPerMap(gameList):
    killsPerMap = {
        "Baltic_Main": [],
        "Chimera_Main": [],
        "Desert_Main": [],
        "DihorOtok_Main": [],
        "Erangel_Main": [],
        "Heaven_Main": [],
        "Range_Main": [],
        "Savage_Main": [],
        "Summerland_Main": [],
        "Tiger_Main": []
    }
    for game in gameList:
        killsPerMap[game['map_name']].append(
            game['participant']['stats']['combat']['kda']['kills'])
    return killsPerMap


def genReadme(gameList):
    killsPerMap = getKillsPerMap(gameList)
    print(" == Generating Readme == ")
    readme = open("README.md", "w")
    readme.write("# Forsen BabaG Stats\n")
    readme.write("##### " + str(len(gameList)) + " Games (" + datetime.strptime(getOldestGame(gameList)['started_at'], date_fmt).strftime('%b %d %Y') + " - " + datetime.strptime(getNewestGame(gameList)['started_at'], date_fmt).strftime('%b %d %Y') + ")\n")
    for gameMap in killsPerMap:
        gameMapData = killsPerMap[gameMap]
        if (len(gameMapData) < num_games_on_map_cutoff):
            continue
        zeroToFive = 0
        SixToTen = 0
        ElevenPlus = 0
        for game in gameMapData:
            if game <= 5:
                zeroToFive += 1
            elif game <= 10:
                SixToTen += 1
            else:
                ElevenPlus += 1
        readme.write("## " + mapNameTranslate[gameMap] + " (" +
                    str(len(gameMapData)) + " games)" + "\n")
        readme.write("![](img/" + mapImgTranslate[gameMap] + ")" + "\n")
        readme.write("```" + "\n")
        readme.write("0-5: " +
                    str(int(100 *
                            round(zeroToFive / len(gameMapData), 2))) +
                    "%" + "\n")
        readme.write("6-10: " +
                    str(int(100 *
                            round(SixToTen / len(gameMapData), 2))) +
                    "%" + "\n")
        readme.write("11+: " +
                    str(int(100 *
                            round(ElevenPlus / len(gameMapData), 2))) +
                    "%" + "\n")
        readme.write("```" + "\n")
    readme.close()
    print("============================================================")


def getNewestGame(gameList):
    currNewest = gameList[0]
    for game in gameList:
        if datetime.strptime(game['started_at'], date_fmt) > datetime.strptime(currNewest['started_at'], date_fmt):
            currNewest = game
    return currNewest

def getOldestGame(gameList):
    currOldest = gameList[0]
    for game in gameList:
        if datetime.strptime(game['started_at'], date_fmt) < datetime.strptime(currOldest['started_at'], date_fmt):
            currOldest = game
    return currOldest

def filterGames(gameList):
    num_games_cutoff_date = 0
    num_games_malformed = 0
    filteredGames = []
    for game in gameData:
        # malformed filter
        if 'map_name' not in game:
            num_games_malformed += 1
            continue
        # date filter
        curr_game_date = datetime.strptime(game['started_at'], date_fmt)
        if curr_game_date < date_cutoff:
            num_games_cutoff_date += 1
            continue
        filteredGames.append(game)
    print(" == Filtering Games == ")
    print("Total games: ", len(gameData))
    print("Filtered games: " + str(len(filteredGames)) + "\n")
    print("Number of games before cutoff date: " +
          str(len(gameData) - num_games_cutoff_date))
    print("Number of malformed games: " + str(num_games_malformed))
    print("============================================================")
    return filteredGames

def loadSavedGameData():
    try:
        with open('fullGameData.json', 'r') as infile:
            return json.load(infile)
    except:
        print("Error opening fullGameData.json, use --datasource=api to get new data")
        exit()
        
def printStats(gameList):
    killsPerMap = getKillsPerMap(gameList)
    print(" == Stats == ")
    print("Total games: ", len(gameList))
    print("Oldest game: ", datetime.strptime(getOldestGame(gameList)['started_at'], date_fmt).strftime('%b %d %Y'))
    print("Newest game: ", datetime.strptime(getNewestGame(gameList)['started_at'], date_fmt).strftime('%b %d %Y'))
    print("============================================================")





print("=====================Forsen BabaG Stats=====================")
print("Date Cutoff: " + date_cutoff.strftime('%b %d %Y'))
print("Number of games on map cutoff: " + str(num_games_on_map_cutoff))
print("")
print("Data Source: " + args.datasource)
print("Generating readme: " + str(args.genReadme))
print("============================================================")


gameData = []
if (args.datasource == 'file'):
    gameData = loadSavedGameData()
elif (args.datasource == 'web'):
    pullLatestStats()
    gameData = loadSavedGameData()

gameData = filterGames(gameData)

if (args.showStats):
    printStats(gameData)

if (args.genReadme):
    genReadme(gameData)