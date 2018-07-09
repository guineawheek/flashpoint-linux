#!/usr/bin/env python3 -i
import xml.etree.ElementTree as ET
from pprint import pprint

tree = ET.parse("Flash.xml")
root = tree.getroot()

games = []
for entry in root.getchildren():
    game = {"Type": entry.tag}
    for element in entry.getchildren():
        game[element.tag] = element.text
    games.append(game)

t = {}
for game in games:
    for k, v in game.items():
        if k in [
                'AutoRunAfter', 'Broken', 'CommunityStarRating', 'CommunityStarRatingTotalVotes', 'Completed', 'ConfigurationCommandLine', 'ConfigurationPath', 'DosBoxConfigurationPath', 'Emulator', 'Favorite', 'LastPlayedDate', 'ManualPath', 'MusicPath', 'Platform', 'Portable', 'Priority', 'Rating', 'Region', 'ScummVMAspectCorrection', 'ScummVMFullScreen', 'ScummVMGameDataFolderPath', 'ScummVMGameType', 'SideA', 'SideB', 'StarRating', 'StarRatingFloat', 'UseDosBox', 'UseEmulator', 'UseScummVM', 'Version', 'VideoPath', 'WikipediaURL']:
            continue
        if k not in t:
            t[k] = {v}
        else:
            t[k].add(v)

res = {}
for k, v in t.items():
    if len(v) < 15:
        res[k] = v
    else:
        res[k] = len(v)
