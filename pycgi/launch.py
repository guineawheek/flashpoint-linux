#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from pyflashpoint.cgi import run, error
from pprint import pformat
import cgi
import os
import subprocess


def handler(launchbox, j2env):
    params = cgi.FieldStorage()

    if "id" not in params:
        error(j2env, 400, "Bad Request", "expected id= parameter")

    game = launchbox.search("ID", params['id'].value)

    if not game:
        error(j2env, 404, "Not Found", "not found ig")

    popen_env = os.environ.copy()
    popen_env["http_proxy"] = "http://localhost:8888"
    popen_env["DISPLAY"] = ":0"
    popen_env["XAUTHORITY"] = ".Xauthority"
    popen_env["HOME"] = ""

    print("Content-type: text/html; charset=utf-8")
    print()
    #print(popen_env)
    print(j2env.get_template("launch.html").render(game=pformat(game.a)))#game.a)))
    subprocess.Popen(["wine", game.ApplicationPath, game.CommandLine], cwd=launchbox.path, env=popen_env)#, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


run(handler)
