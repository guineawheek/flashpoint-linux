#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from pyflashpoint.cgi import run


def handler(launchbox, j2env):
    print("Content-type: text/html; charset=utf-8")
    print()
    print(j2env.get_template("index.html").render(launchbox=launchbox))


run(handler)
