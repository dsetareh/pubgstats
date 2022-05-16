import json


f1 = open('./mapnames.json', 'r')
mapTranslate = json.load(f1)

f2 = open('./killsPerMap.json', 'r')
data = json.load(f2)

f3 = open('./mapimg.json', 'r')
mapImgTranslate = json.load(f3)

for gameMap in data:
    gameMapData = data[gameMap]
    if (len(gameMapData) < 10):
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
    print("# " + mapTranslate[gameMap] + " (" +str(len(gameMapData))+ " games)")
    print("![](img/" + mapImgTranslate[gameMap]  + ")")
    print("```")
    print("0-5: " + str(int(100*round(zeroToFive / len(gameMapData), 2))) + "%")
    print("6-10: " + str(int(100*round(SixToTen / len(gameMapData), 2))) + "%")
    print("11+: " + str(int(100*round(ElevenPlus / len(gameMapData), 2))) + "%")
    print("```")
        

