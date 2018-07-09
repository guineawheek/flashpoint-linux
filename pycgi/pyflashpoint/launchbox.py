import xml.etree.ElementTree as ET
import json
class LaunchBox:
    def __init__(self, path : str):
        self.path = path
        self.games = []

    def parse_xml(self):
        root = ET.parse(self.path + "/Data/Platforms/Flash.xml").getroot()
        for child in root.getchildren():
            if child.tag == "Game":
                self.games.append(Game({e.tag: e.text for e in child.getchildren()}))
            elif child.tag == "AdditionalApplication":
                addn_app = AdditionalApplication({e.tag: e.text for e in child.getchildren()})
                game = self.search("ID", addn_app.a['GameID'])
                game.addn_app = addn_app

    def parse_json(self, path):
        with open(path) as f:
            net = json.load(f)
            for g in net:
                ent = Game(g)
                self.games.append(ent)
                if 'addn_app' in g:
                    ent.addn_app = AdditionalApplication(g['addn_app'])


    def search_all(self, key, value):
        res = []
        for g in self.games:
            if g.a[key] == value:
                res.append(g)
        return res

    def search(self, key, value):
        for g in self.games:
            if g.a[key] == value:
                return g
        return None

class Game:
    def __init__(self, attrs: dict):
        self.__dict__.update(attrs)
        self.a = attrs
        self.addn_app = None

class AdditionalApplication:
    def __init__(self, attrs: dict):
        self.__dict__.update(attrs)
        self.a = attrs

def get_launchbox(path):
    l = LaunchBox(path)
    l.parse_json("Flash.json")
    return l