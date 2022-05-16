import requests, json, time


url = 'https://pubg.op.gg/api/users/59fe352b55aa60000188a0fb/matches/recent?queue_size=1&mode=fpp&type=official'

after = '&after='

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.67 Safari/537.36',
}


all_games = json.loads(requests.get(url, headers=headers).content)['matches']['items']



num_matches = len(all_games)
last_match_offset = all_games[-1]['offset']

while num_matches == 20:
    response = json.loads(requests.get(url + after + last_match_offset, headers=headers).content)['matches']['items']
    all_games.extend(response)
    num_matches = len(response)
    last_match_offset = response[-1]['offset']
    time.sleep(1)

with open('fullGameData.json', 'w') as outfile:
    json.dump(all_games, outfile)