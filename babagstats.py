import json, requests, time, argparse
from datetime import datetime

import matplotlib.pyplot as plt
from mpl_interactions import ipyplot as iplt
import numpy as np
import seaborn as sns

# args
parser = argparse.ArgumentParser(description='get forsen babag stats')
parser.add_argument('--datasource',
                    type=str,
                    required=False,
                    help='pull from [file, api] (default: file)',
                    default='file')
parser.add_argument('--showStats',
                    type=bool,
                    required=False,
                    help='output stats during runtime (default: True)',
                    default=True)
parser.add_argument('--genReadme',
                    type=bool,
                    required=False,
                    help='generate readme (default: False)',
                    default=False)
parser.add_argument('--genKillsPerHour',
                    type=bool,
                    required=False,
                    help='generate KillsPerHour (default: False)',
                    default=False)
parser.add_argument('--genKillsPerWeekday',
                    type=bool,
                    required=False,
                    help='generate KillsPerWeekday (default: False)',
                    default=False)
parser.add_argument('--genAllKills',
                    type=bool,
                    required=False,
                    help='generate all kills histogram (default: False)',
                    default=False)
parser.add_argument('--earliestyear',
                    type=int,
                    required=False,
                    help='earliest year cutoff (default: 2021)',
                    default=2021)
parser.add_argument('--earliestmonth',
                    type=int,
                    required=False,
                    help='earliest month cutoff (default: 1)',
                    default=1)
parser.add_argument('--dpi',
                    type=int,
                    required=False,
                    help='plot dpi (default: 600)',
                    default=600)
parser.add_argument('--cutoff1',
                    type=int,
                    required=False,
                    help='Grouping cutoff 1 (default: 3)',
                    default=3)
parser.add_argument('--cutoff2',
                    type=int,
                    required=False,
                    help='Grouping cutoff 2 (default: 10)',
                    default=10)


parser.add_argument(
    '--numgamesonmap',
    type=int,
    required=False,
    help='num games needed on a map to put in readme (default: 10)',
    default=10)
parser.add_argument('--requesttimeout',
                    type=float,
                    required=False,
                    help='api request timeout (default: 0.1)',
                    default=0.1)


args = parser.parse_args()

plot_dpi = args.dpi
date_cutoff = datetime(args.earliestyear, args.earliestmonth, 1)
num_games_on_map_cutoff = args.numgamesonmap

requestTimeout = args.requesttimeout

date_fmt = '%Y-%m-%dT%H:%M:%S+0000'

allmaps = [
    "Baltic_Main",
    "Chimera_Main" ,
    "Desert_Main" ,
    "DihorOtok_Main" ,
    "Erangel_Main" ,
    "Heaven_Main" ,
    "Range_Main" ,
    "Savage_Main" ,
    "Summerland_Main" ,
    "Tiger_Main" 
]

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
    "Baltic_Main": "Erangel.webp",
    "Chimera_Main": "Paramo.webp",
    "Desert_Main": "Miramar.webp",
    "DihorOtok_Main": "Vikendi.webp",
    "Erangel_Main": "Erangel.webp",
    "Heaven_Main": "Haven.webp",
    "Range_Main": "Range.webp",
    "Savage_Main": "Sanhok.webp",
    "Summerland_Main": "Karakin.webp",
    "Tiger_Main": "Taego.webp"
}

maxPlayersPerMap = {
    "Baltic_Main": 100,
    "Chimera_Main": 64,
    "Desert_Main": 100,
    "DihorOtok_Main": 100,
    "Erangel_Main": 100,
    "Heaven_Main": 32,
    "Range_Main": 1,
    "Savage_Main": 100,
    "Summerland_Main": 64,
    "Tiger_Main": 100
}


def pullLatestStats():
    print(" == Pulling Latest Matches == ")
    url = 'https://pubg.op.gg/api/users/59fe352b55aa60000188a0fb/matches/recent?queue_size=1&mode=fpp&type=official'
    after = '&after='
    headers = {
        'User-Agent':
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.67 Safari/537.36',
    }
    all_games = json.loads(requests.get(
        url, headers=headers).content)['matches']['items']
    num_matches = len(all_games)
    last_match_offset = all_games[-1]['offset']  # base64 encoded str

    while num_matches == 20:
        response = json.loads(
            requests.get(url + after + last_match_offset,
                         headers=headers).content)['matches']['items']
        all_games.extend(response)
        num_matches = len(response)
        last_match_offset = response[-1]['offset']
        print("Pulled " + str(num_matches) + " matches")
        time.sleep(requestTimeout)  # just in case

    with open('data/fullGameData.json', 'w') as outfile:
        json.dump(all_games, outfile)
    print("============================================================")


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

def killCategory(numKills):
    if numKills <= args.cutoff1:
        return 0
    elif numKills < args.cutoff2:
        return 1
    else:
        return 2
    

def getKillsPerWeekday(gameList):
    killsPerWeekday = {
        "Monday": [],
        "Tuesday": [],
        "Wednesday": [],
        "Thursday": [],
        "Friday": [],
        "Saturday": [],
        "Sunday": []
    }
    for game in gameList:
        curr_num_kills = game['participant']['stats']['combat']['kda']['kills']
        curr_game_kills_type = killCategory(curr_num_kills)
        killsPerWeekday[datetime.strptime(
            game['started_at'],
            date_fmt).strftime('%A')].append(curr_game_kills_type)
    return killsPerWeekday


def plotKillsPerWeekday(killsPerWeekday):
    print(" == Plotting Kills Per Weekday == ")
    labels = [
        "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday",
        "Sunday"
    ]
    type0games = list(
        map(lambda x: round(killsPerWeekday[x].count(0) / len(killsPerWeekday[x]), 2) * 100, killsPerWeekday))
    type1games = list(
        map(lambda x: round(killsPerWeekday[x].count(1) / len(killsPerWeekday[x]), 2) * 100, killsPerWeekday))
    type2games = list(
        map(lambda x: round(killsPerWeekday[x].count(2) / len(killsPerWeekday[x]), 2) * 100, killsPerWeekday))
    x = np.arange(len(labels))
    width = 0.20
    fig, ax = plt.subplots()
    rects1 = ax.bar(x - width * 1.5, type0games, width, label=f'0-{args.cutoff1}')
    rects2 = ax.bar(x - width / 2, type1games, width, label=f'{args.cutoff1 + 1}-{args.cutoff2}')
    rects3 = ax.bar(x + width / 2, type2games, width, label=f'{args.cutoff2 + 1}+')
    ax.set_ylabel('Percentage of Games')
    ax.set_title('Average # of Kills/Game by Weekday')
    ax.set_xticks(x, labels)
    ax.legend()
    ax.bar_label(rects1, padding=3)
    ax.bar_label(rects2, padding=3)
    ax.bar_label(rects3, padding=3)
    fig.tight_layout()
    plt.savefig('data/killsPerWeekday.png', dpi=plot_dpi)
    print("============================================================")


def plotAllKills(gameList):
    gameinfo = []
    for g in gameList:
        kills = g['participant']['stats']['combat']['kda']['kills']
        time = datetime.strptime(g['started_at'], date_fmt)
        time = (time.hour * 60) + time.minute
        mapn = g['map_name']
        gameinfo.append({'kills': kills, "time": time, "map": mapn})
    
    kills = []
    time = []
    maps = []
    colors = []
    for g in gameinfo:
        kills.append(g['kills'])
        time.append(g['time'])
        maps.append(g['map'])
        colors.append(allmaps.index(g['map']))
    
    kills = np.array(kills)
    time = np.array(time)
    maps = np.array(maps)
    colors = np.array(colors)
    
    sns.histplot(x=kills, data=gameinfo, kde=True, hue=maps)
    
    def f_x(xrange, **kwargs):
        return np.linspace("range", min(kills), max(), step)
    def f_y(xrange, **kwargs):
        return np.linspace("range", min(kills), max(), step)

    controls = iplt.plot(f_x, f_y, xrange=("r", -1, 3), tau=(5, 10))

    plt.show()
    
        
        
    # print('max: ' + str(max(kills)))
    # print('max: ' + str(max(time)))
    # print('min: ' + str(min(kills)))
    # print('min: ' + str(min(time)))

    # kills_hist = [0] * (max(kills) - min(kills))
    # time_hist = [0] * (max(time) - min(time))
    
    # for g in gameinfo:
    #     kills_hist[g['kills']] += 1
    #     time_hist[g['time']] += 1

    # fig, ax = plt.subplots()

    # ax.set_ylabel('kills')
    # ax.set_xlabel('time')
    # ax.set_title('kills vs time')
    # # ax.set_xticks(x, labels)
    # ax.legend()
    # plt.scatter(time, kills, c=colors, alpha=0.5)
    # fig.tight_layout()
    # plt.show()
    # plt.savefig('data/allkills.png', dpi=plot_dpi)
    print("============================================================")


def getKillsPerHour(gameList):
    killsPerHour = [[] for _ in range(24)]
    for game in gameData:
        curr_game_date = datetime.strptime(game['started_at'], date_fmt)
        curr_game_hour = curr_game_date.hour
        curr_num_kills = game['participant']['stats']['combat']['kda']['kills']
        curr_game_kills_type = killCategory(curr_num_kills)
        killsPerHour[curr_game_hour].append(curr_game_kills_type)
    return killsPerHour[18:23]  # streaming hours


def plotKillsPerHour(killsPerHour):
    print(" == Plotting Kills Per Hour == ")
    labels = ['Hour 1', 'Hour 2', 'Hour 3', 'Hour 4', 'Hour 5']
    type0games = list(
        map(lambda x: round(x.count(0) / len(x), 2) * 100, killsPerHour))
    type1games = list(
        map(lambda x: round(x.count(1) / len(x), 2) * 100, killsPerHour))
    type2games = list(
        map(lambda x: round(x.count(2) / len(x), 2) * 100, killsPerHour))
    x = np.arange(len(labels))
    width = 0.20
    fig, ax = plt.subplots()
    rects1 = ax.bar(x - width * 1.5, type0games, width, label=f'0-{args.cutoff1}')
    rects2 = ax.bar(x - width / 2, type1games, width, label=f'{args.cutoff1 + 1}-{args.cutoff2}')
    rects3 = ax.bar(x + width / 2, type2games, width, label=f'{args.cutoff2 + 1}+')
    ax.set_ylabel('Percentage of Games')
    ax.set_title('Average # of Kills/Game by Stream Hour')
    ax.set_xticks(x, labels)
    ax.legend()
    ax.bar_label(rects1, padding=3)
    ax.bar_label(rects2, padding=3)
    ax.bar_label(rects3, padding=3)
    fig.tight_layout()
    plt.savefig('data/killsPerHour.png', dpi=plot_dpi)
    print("============================================================")



def genReadme(gameList):
    killsPerMap = getKillsPerMap(gameList)
    print(" == Generating Readme == ")
    readme = open("README.md", "w")
    readme.write("# Forsen BabaG Stats\n")
    readme.write(
        "##### " + str(len(gameList)) + " Games (" +
        datetime.strptime(getOldestGame(gameList)['started_at'],
                          date_fmt).strftime('%b %d %Y') + " - " +
        datetime.strptime(getNewestGame(gameList)['started_at'],
                          date_fmt).strftime('%b %d %Y') + ")\n")
    readme.write(
        f"|Map|Image| 0-{args.cutoff1} | {args.cutoff1 + 1}-{args.cutoff2} | {args.cutoff2 + 1}+ |\n| :-: | :-: | :-: | :--: | :-: |\n")
    for gameMap in sorted(killsPerMap,
                          key=lambda k: len(killsPerMap[k]),
                          reverse=True):
        gameMapData = killsPerMap[gameMap]
        if (len(gameMapData) < num_games_on_map_cutoff):
            continue
        firstCutoff = 0
        secondCutoff = 0
        thirdCutoff = 0
        for game in gameMapData:
            if game <= 3:
                firstCutoff += 1
            elif game <= 10:
                secondCutoff += 1
            else:
                thirdCutoff += 1
        readme.write("| **" + mapNameTranslate[gameMap] + "<br>(" +
                     str(len(gameMapData)) + f" games)**<br><sub>{maxPlayersPerMap[gameMap]} Players</sub>| <img src=\"img/" +
                     mapImgTranslate[gameMap] +
                     "\" width=\"250\"/> | " +
                     str(round(firstCutoff / len(gameMapData) * 100, 2)) +
                     "% | " +
                     str(round(secondCutoff / len(gameMapData) * 100, 2)) +
                     "% | " +
                     str(round(thirdCutoff / len(gameMapData) * 100, 2)) +
                     "% |\n")
    readme.write("\n|Kills By Weekday|Kills By Hour|\n| :-: | :-: |\n| <img src=\"data/killsPerWeekday.png\" width=\"325\"/> | <img src=\"data/killsPerHour.png\" width=\"325\"/> |\n")
    readme.close()
    print("============================================================")
    plotKillsPerWeekday(getKillsPerWeekday(gameData))
    plotKillsPerHour(getKillsPerHour(gameData))


def getNewestGame(gameList):
    currNewest = gameList[0]
    for game in gameList:
        if datetime.strptime(game['started_at'], date_fmt) > datetime.strptime(
                currNewest['started_at'], date_fmt):
            currNewest = game
    return currNewest


def getOldestGame(gameList):
    currOldest = gameList[0]
    for game in gameList:
        if datetime.strptime(game['started_at'], date_fmt) < datetime.strptime(
                currOldest['started_at'], date_fmt):
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
        with open('data/fullGameData.json', 'r') as infile:
            return json.load(infile)
    except:
        print(
            "Error opening data/fullGameData.json, use --datasource=api to pull new data"
        )
        exit()


def printStats(gameList):
    killsPerMap = getKillsPerMap(gameList)
    print(" == Stats == ")
    print("Total games: ", len(gameList))
    print(
        "Oldest game: ",
        datetime.strptime(getOldestGame(gameList)['started_at'],
                          date_fmt).strftime('%b %d %Y'))
    print(
        "Newest game: ",
        datetime.strptime(getNewestGame(gameList)['started_at'],
                          date_fmt).strftime('%b %d %Y'))
    print("============================================================")


print("=====================Forsen BabaG Stats=====================")
print("Date Cutoff: " + date_cutoff.strftime('%b %d %Y'))
print("Number of games on map cutoff: " + str(num_games_on_map_cutoff))
print("Data Source: " + args.datasource)
print("============================================================")

gameData = []
if (args.datasource == 'file'):
    gameData = loadSavedGameData()
elif (args.datasource == 'api'):
    pullLatestStats()
    gameData = loadSavedGameData()
else:
    print("Invalid data source, use --datasource=file or --datasource=api")
    exit()

gameData = filterGames(gameData)

if (args.showStats):
    printStats(gameData)

if (args.genReadme):
    genReadme(gameData)
    args.genKillsPerHour = False
    args.genKillsPerWeekday = False

if (args.genKillsPerHour):
    plotKillsPerHour(getKillsPerHour(gameData))

if (args.genKillsPerWeekday):
    plotKillsPerWeekday(getKillsPerWeekday(gameData))

if (args.genAllKills):
    plotAllKills(gameData)
