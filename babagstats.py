import json, itertools

  
f = open('./pubg.op.gg.har', 'rb')
data = json.load(f)

killsPerMap = {'Tiger_Main': [], 'Erangel_Main': [], 'Desert_Main': [], 'Baltic_Main': [], 'Summerland_Main': [], 'Savage_Main': [], 'DihorOtok_Main': [], 'Heaven_Main': []}
    
def clean_data(data):
    return {'time': data['started_at'], 'map': data['map_name'], 'kills': data['participant']['stats']['combat']['kda']['kills']}
    

dataEntries = filter(lambda x: x['response']['content']['mimeType'] == 'application/json', data['log']['entries'])

dataEntries = list(map(lambda x: x['response']['content']['text'], list(dataEntries)))

dataEntries = list(filter(lambda x: x[2:7] == "param", dataEntries))

dataEntries = list(map(lambda x: json.loads(x), dataEntries))

dataEntries = list(map(lambda x: x['matches']['items'], dataEntries))

dataEntries = list(itertools.chain.from_iterable(dataEntries))



dataEntries = list(map(lambda x: clean_data(x), dataEntries))

uniqueMaps = set(map(lambda x: x['map'], dataEntries))

for game in dataEntries:
    killsPerMap[game['map']].append(game['kills'])
    
with open('killsPerMap.json', 'w') as outfile:
    json.dump(killsPerMap, outfile)
