# -*- coding: utf-8 -*-
import cgi
import sys
import os
import cgitb
from jinja2 import Environment, PackageLoader
from pyflashpoint.launchbox import get_launchbox


def error(j2env, code, msg, desc):
    print(f"Status: {code} {msg}")
    print()
    print(j2env.get_template("error.html").render(code=code, msg=msg, desc=desc))
    sys.exit()

def run(handler):
    cgitb.enable()
    j2env = Environment(loader=PackageLoader("pyflashpoint", "templates"))

    if os.environ["REMOTE_ADDR"] != "127.0.0.1":
        error(j2env, 403, "Forbidden", "You do not have permission to access this resource.")

    launchbox = get_launchbox("Flashpoint/Arcade")

    handler(launchbox, j2env)
