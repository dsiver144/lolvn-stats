import requests
from urllib.parse import quote
import re
import urllib3
from os import system, name 
urllib3.disable_warnings()

# class bcolors:
#     HEADER = '\033[95m'
#     OKBLUE = '\033[94m'
#     OKCYAN = '\033[96m'
#     OKGREEN = '\033[92m'
#     WARNING = '\033[93m'
#     FAIL = '\033[91m'
#     ENDC = '\033[0m'
#     BOLD = '\033[1m'
#     UNDERLINE = '\033[4m'
class bcolors:
    HEADER = ''
    OKBLUE = ''
    OKCYAN = ''
    OKGREEN = ''
    WARNING = ''
    FAIL = ''
    ENDC = ''
    BOLD = ''
    UNDERLINE = ''

lol_path = ""
def get_lol_path():
    global lol_path
    try:
        f = open("Path.txt")
        lol_path = f.readline()
        # Do something with the file
    except IOError:
        print("Input lol path: ")
        lol_path = input()
        f = open("Path.txt", "w")
        f.write(lol_path)
    finally:
        f.close()

name = "TIBEST"
base_url = 'https://127.0.0.1:{port}/{endpoint}'
port = -1
password = -1


def connect_client():
    try:
        f = open(lol_path + "/LeagueClient/lockfile", "r")
    except:
        print("Lockfile not found. Please run League of Legends to use this app.")
        input()
        quit()
    p = re.compile(r'LeagueClient\:(\d+)\:(\d+)\:(.+?)\:https')
    m = p.match(f.readline())
    global port, password
    port = m.group(2)
    password = m.group(3)

def get_summoner_by_name(name):
    end_point = "lol-summoner/v1/summoners?name=" + quote(name)
    url = base_url.format(port=port, endpoint=end_point)
    x = requests.get(url, auth = ('riot', password), verify=False)
    return x.json()
def get_rank_info(puuid):
    end_point = "lol-ranked/v1/ranked-stats/" + puuid
    url = base_url.format(port=port, endpoint=end_point)
    x = requests.get(url, auth = ('riot', password), verify=False)
    return x.json()

def get_match_list(puuid):
    end_point = "lol-career-stats/v1/summoner-games/" + puuid
    url = base_url.format(port=port, endpoint=end_point)
    x = requests.get(url, auth = ('riot', password), verify=False)
    return x.json()
def get_match_list2(accountId):
    end_point = f"lol-match-history/v1/friend-matchlists/{accountId}"
    url = base_url.format(port=port, endpoint=end_point)
    x = requests.get(url, auth = ('riot', password), verify=False)
    return x.json()

def get_win_rate(data):
    total_matches = data['wins'] + data['losses'];
    if total_matches == 0:
        return 0.0    
    return round(data['wins'] / total_matches, 1) * 100
def get_game_detail_data(game_id):
    end_point = f"lol-match-history/v1/games/{game_id}"
    #print(end_point)
    url = base_url.format(port=port, endpoint=end_point)
    x = requests.get(url, auth = ('riot', password), verify=False)
    return x.json()
def get_current_summoner():
    end_point = "lol-summoner/v1/current-summoner/"
    url = base_url.format(port=port, endpoint=end_point)
    x = requests.get(url, auth = ('riot', password), verify=False)
    return x.json()

playTogetherDict = dict()

def show_player_info(name, champion, mode = 'details'):
    global playTogetherDict
    summoner = get_summoner_by_name(name)
    puuid = summoner['puuid']
    matches = get_match_list2(summoner['accountId'])['games']['games']
    m_index = 0
    match_nums = min(20, len(matches))
    match_str = ""
    aram_str = ""
    Kills = 0.0
    Deaths = 0.0
    Assits = 0.0
    Wins = 0.0
    playTogetherDict[name] = dict()
    AramGames = 0
    RiftGames = 0
        
    for match in matches[::-1]:
        if match is None:
            break
        if m_index == match_nums:
            break
        if m_index == 0:
            detail = get_game_detail_data(match['gameId'])
            i = 0
            for player in detail['participantIdentities']:
                sname = player['player']['summonerName']
                playTogetherDict[name][sname] = detail['participants'][i]['teamId']
                i += 1
            
        stats = match['participants'][0]['stats']
        m_index += 1
        
                
        if match['gameMode'] == "ARAM":
            AramGames += 1
            #aram_str += (f"{bcolors.FAIL}-{bcolors.ENDC} ", f"{bcolors.OKGREEN}O{bcolors.ENDC} ")[stats['win'] == True]
        else:
            Kills += stats['kills']
            Deaths += stats['deaths']
            Assits += stats['assists']
            RiftGames += 1
            match_str += (f"{bcolors.FAIL}-{bcolors.ENDC} ", f"{bcolors.OKGREEN}O{bcolors.ENDC} ")[stats['win'] == True]
            Wins += 1 if stats['win'] == True else 0

            
        
        #print(match)
    if match_nums != 0:
        Kills = round(Kills / RiftGames, 1)
        Deaths = round(Deaths / RiftGames, 1)    
        Assits = round(Assits / RiftGames, 1)
        WinRate = round(Wins / RiftGames, 1) * 100
        KDA = (Kills + Assits) / Deaths
        KDA = round(KDA, 2)
    else:
        KDA = 0.0
        WinRate = 0.0
    teamId = -1
    for summonerName, team in playTogetherDict[name].items():
        if summonerName == name:
            teamId = team
    trash = []
    for summonerName, team in playTogetherDict[name].items():
        if summonerName == name or team != teamId:
            trash.append(summonerName)
    for summonerName in trash:
        playTogetherDict[name].pop(summonerName)

    rankInfo = get_rank_info(puuid)['queueMap']
    solo = rankInfo['RANKED_SOLO_5x5']
    flex = rankInfo['RANKED_FLEX_SR']
    playerTag = "Aram Player" if AramGames > RiftGames else "Normal Player"
    rankMsg = "{} {} ({} wins) - {} LP (Last Season: {} {})"
    if mode == 'details':
        print(f"  > Name     : {bcolors.HEADER}{name} ({champion}){bcolors.ENDC} ({playerTag})")
        #print(f"  > Team    : {'Blue' if player['team'] == 'ORDER' else 'Red'}")
        print(f"    + Recent : {match_str} (Win Rate: {WinRate}%)")
        print(f"    + KDA    : {bcolors.OKGREEN}{Kills}{bcolors.ENDC}/{bcolors.FAIL}{Deaths}{bcolors.ENDC}/{bcolors.WARNING}{Assits}{bcolors.ENDC} ({KDA})")
        print( "   =============================================================")
        print( "    - Solo   : " + rankMsg.format(solo['tier'], solo['division'], solo['wins'], solo['leaguePoints'], solo['previousSeasonEndTier'], solo['previousSeasonEndDivision']))
        print( "    - Flex   : " + rankMsg.format(flex['tier'], flex['division'], flex['wins'], flex['leaguePoints'], flex['previousSeasonEndTier'], flex['previousSeasonEndDivision']))
        print("---------------------------------------------------------------------")
    elif mode == 'simple':
        lastSoloTier = solo['previousSeasonEndTier']
        lastSoloDiv = solo['previousSeasonEndDivision']
        lastFlexTier = flex['previousSeasonEndTier']
        lastFlexDiv = flex['previousSeasonEndDivision']
        print(f"+ {name} ({champion}) ({playerTag})  |  {solo['tier']} {solo['division']} {solo['leaguePoints']}LP (Last: {lastSoloTier} {lastSoloDiv}) (Solo), {flex['tier']} {flex['division']} {flex['leaguePoints']}LP (Last: {lastFlexTier} {lastFlexDiv}) (Flex)  |  KDA: {KDA}, WR: {WinRate}%")
        print("-------------------------------------------------")
    return summoner



def get_playerlist(mode = 'details'):
    try:
        result = requests.get("https://127.0.0.1:2999/liveclientdata/playerlist", auth = ('riot', password), verify=False)
    except:
        print("You're not in game.")
        return askForCommands()
    print("---------------------------------------------------------------------")
    teams = dict()
    teams['100'] = []
    teams['200'] = []
    champions = {}
    for player in result.json():
        if player['isBot']:
            continue
        #print(player)
        name = player['summonerName']
        champion = player['championName']
        summoner = show_player_info(name, champion, mode)
        teamId = 100 if player['team'] == "ORDER" else 200
        teams[str(teamId)].append(name)
        champions[name] = champion
        #print(player)
    print("> Play together Info <")
    print("---------------------------------------------------------------------")
    for teamId, team in teams.items():
        marked = dict()
        squad = []
        for p in team:
            if squad.count(p) > 0:
                continue
            for p2 in playTogetherDict[p]:
                if team.count(p2) > 0:
                    if p not in marked:
                        marked[p] = []
                    marked[p].append(p2)
                    squad.append(p2)
        for p, friends in marked.items():
            fstr = f"{p} ({champions[p]}), " + ", ".join([fr + " (" + champions[fr] + ")" for fr in friends])
            print(f"Squad: {fstr}")
        print(" ")
    playTogetherDict.clear()
    askForCommands()    

def search_player():
    print(f"{bcolors.OKGREEN}> Input summoner name: {bcolors.ENDC}")
    name = input()
    system("cls")
    print("---------------------------------------------------------------------")
    show_player_info(name, "None")
    askForCommands()

def searchGame():
    #/lol/spectator/v4/featured-games
    end_point = "/lol/spectator/v4/featured-games" #+ quote(name)
    url = base_url.format(port=port, endpoint=end_point)
    x = requests.get(url, auth = ('riot', password), verify=False)
    return x.json()

def showCurrentSummonerInfo():
    system("cls")
    print("---------------------------------------------------------------------")
    name = get_current_summoner()['displayName']
    show_player_info(name, "None")
    askForCommands()

def askForCommands():
    print(f"{bcolors.WARNING}Command: (q: Quit | r: Show Rank (rs: Simple) | s: Search ){bcolors.ENDC} | c: Current Summoner")
    command = input()
    if command == 'r':
        system("cls")
        get_playerlist()
    if command == 'rs':
        system("cls")
        get_playerlist('simple')
    elif command == 's':
        system("cls")
        search_player()
    elif command == 'm':
        system("cls")
        set_display_mode()
    elif command == 't':
        print(searchGame())
    elif command == 'c':
        system("cls")
        showCurrentSummonerInfo()
    else:
        quit

def main():
    get_lol_path()
    connect_client()
    print(f"{bcolors.OKBLUE}Connected to League Client!{bcolors.ENDC}")
    askForCommands()

if __name__ == "__main__":
    main()

