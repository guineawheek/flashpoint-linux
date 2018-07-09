from pyflashpoint.launchbox import LaunchBox, Game
import time
import json
from jinja2 import Environment, FileSystemLoader

if __name__ == "__main__":
    start = time.time()
    launchbox = LaunchBox("/disk/guinea/Flashpoint/Arcade")
    launchbox.parse_json("Flash.json")
    #launchbox.parse_xml()

    """
    net = []
    for g in launchbox.games:
        a = g.a
        if g.addn_app:
            a['addn_app'] = g.addn_app.a
        net.append(a)

    with open("Flash.json", "w") as f:
        json.dump(net, f)
    """
    print(f"Took {time.time() - start} seconds")

    #j2env = Environment(loader=FileSystemLoader("pyflashpoint/templates"))
    #res = j2env.get_template("index.html").render(launchbox=launchbox)
    #print(res)
