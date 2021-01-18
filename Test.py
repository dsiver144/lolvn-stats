teams = dict()
teams['100'] = ["TIBEST", "Player1", "zzzz"]
teams['200'] = ["Zephy", "Player2", "Player3"]

playTogetherDict = dict()
playTogetherDict["TIBEST"] = ["Player1", "zzzz"]
playTogetherDict["zzzz"] = ["TIBEST", "Player1"]
playTogetherDict["Player1"] = ["TIBEST", "zzzz"]

playTogetherDict["Zephy"] = ["Player2"]
playTogetherDict["Player2"] = ["Zephy"]
playTogetherDict["Player3"] = []
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
        fstr = p + ", " + ", ".join(friends)
        print(f"Squad: {fstr}")
    print("-----")
