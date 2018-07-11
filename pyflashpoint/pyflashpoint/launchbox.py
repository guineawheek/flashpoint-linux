import xml.etree.ElementTree as ET
import json
import os
import glob
import subprocess


class Game:
    def __init__(self, attrs: dict, lb_path):
        attrs['SpecialNotes'] = None
        self.__dict__.update(attrs)
        self.a = attrs
        self.lb_path = lb_path
        self.addn_app = None
        self.proc = None

    def start(self):
        popen_env = os.environ.copy()
        popen_env["http_proxy"] = "http://localhost:8888"
        self.proc = subprocess.Popen(["wine", self.ApplicationPath, self.CommandLine], cwd=self.lb_path, env=popen_env,
                                     stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    def _get_img_path(self, directory):
        name = self.Title
        for i in "<>:\"'/\|?*":
            name = name.replace(i, '_')

        # try a bunch of different extensions
        path = glob.glob(glob.escape(os.path.join(self.lb_path, "Images/Flash/" + directory + "/", name)) + "-*")

        if not path:
            # some boxart has this really weird uuid so handle this case
            path = glob.glob(glob.escape(os.path.join(self.lb_path, "Images/Flash/" + directory + "/", name)) + ".*")

        if not path:
            print("NOT FOUND: " + self.Title)

        return path[0]

    def get_boxart_path(self):
        return self._get_img_path("Box - Front")

    def get_screenshot_path(self):
        return self._get_img_path("Screenshot - Gameplay")

    def add_addn_app(self, addn_app):
        if addn_app.ApplicationPath == "Games\\message.bat":
            # message.bat messages don't run on other operating systems, for obvious reasons
            # half the time they don't even run on windows
            self.a['SpecialNotes'] = addn_app.CommandLine
        self.addn_app = addn_app



class AdditionalApplication:
    def __init__(self, attrs: dict):
        self.__dict__.update(attrs)
        self.a = attrs


class LaunchBox:
    def __init__(self, path : str):
        self.path = path
        self.games = []

    def parse_xml(self):
        root = ET.parse(self.path + "/Data/Platforms/Flash.xml").getroot()
        for child in root.getchildren():
            if child.tag == "Game":
                self.games.append(Game({e.tag: e.text for e in child.getchildren()}, self.path))
            elif child.tag == "AdditionalApplication":
                addn_app = AdditionalApplication({e.tag: e.text for e in child.getchildren()})
                game = self.search("ID", addn_app.a['GameID'])
                game.addn_app = addn_app

    def parse_json(self, path):
        with open(path) as f:
            net = json.load(f)
            for g in net:
                ent = Game(g, self.path)
                self.games.append(ent)
                if 'addn_app' in g:
                    ent.addn_app = AdditionalApplication(g['addn_app'])

    def search_all(self, key, value):
        res = []
        for g in self.games:
            if g.a[key] == value:
                res.append(g)
        return res

    def search(self, key, value) -> Game:
        for g in self.games:
            if g.a[key] == value:
                return g
        return None


def get_launchbox(path) -> LaunchBox:
    l = LaunchBox(path)
    l.parse_xml()
    return l
