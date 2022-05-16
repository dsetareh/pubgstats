import json


f1 = open('./mapData.json', 'r')
mapTranslate = json.load(f1)

f2 = open('./killsPerMap.json', 'r')
data = json.load(f2)

for gameMap in data:
    gameMapData = data[gameMap]
    zeroToFive = 0
    SixToEleven = 0
    ElevenPlus = 0
    for game in gameMapData:
        if game <= 5:
            zeroToFive += 1
        elif game <= 10:
            SixToEleven += 1
        else:
            ElevenPlus += 1
    print(mapTranslate[gameMap])
    print("0-5: " + str(zeroToFive) + "    " + str(int(100*round(zeroToFive / len(gameMapData), 2))) + "%")
    print("6-11: " + str(SixToEleven) + "    " + str(int(100*round(SixToEleven / len(gameMapData), 2))) + "%")
    print("11+: " + str(ElevenPlus) + "    " + str(int(100*round(ElevenPlus / len(gameMapData), 2))) + "%")
        

