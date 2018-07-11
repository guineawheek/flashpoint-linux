from flask import Flask, render_template, send_file, jsonify, abort
from .launchbox import get_launchbox
from pprint import pformat
from functools import wraps
import os


launchbox = get_launchbox(os.path.join(os.environ['FLASHPOINT'], os.environ['FLASHPOINT_MODE']))
app = Flask(__name__)


def game_route(func):
    @wraps(func)
    def w(game_id, *args, **kwargs):
        game = launchbox.search("ID", game_id)
        if not game:
            abort(404)
        return func(game, *args, **kwargs)
    return w


@app.route('/')
def index():
    # TODO: actually make sorting functions
    a = list(launchbox.games)
    a.sort(key=lambda g: g.Title)
    return render_template('index.html', games=a)


@app.route('/game/<game_id>')
@game_route
def game_info(game):
    return render_template('game_info.html', game=game, pformat=pformat, environ=dict(os.environ))


@app.route('/game/<game_id>/launch')
@game_route
def launch_game(game):
    game.start()
    return f"please wait while {game.Title} launches..."


@app.route('/game/<game_id>/boxart')
@game_route
def get_boxart(game):
    return send_file(game.get_boxart_path())


@app.route('/game/<game_id>/screenshot')
@game_route
def get_screenshot(game):
    return send_file(game.get_screenshot_path())


@app.route('/game/<game_id>/info')
@game_route
def get_game_info(game):
    return jsonify(game.a)

