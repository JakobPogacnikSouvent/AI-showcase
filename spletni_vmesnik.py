import bottle
import os
from model import RPS_controller

rps_controller = RPS_controller()

@bottle.get('/')
def hello_world():
    return bottle.template('hello_world.html')

@bottle.post('/rps/')
def nova_igra():
    game_id = rps_controller.new_game()
    print('redirecting')
    bottle.redirect(f'/rps/{game_id}/')

@bottle.get('/rps/<game_id:int>/')
def rps(game_id):
    game = rps_controller.games[game_id]
    return bottle.template('rps.tpl', game=game, game_id=game_id)

@bottle.post('/rps/<game_id:int>/')
def rps_update(game_id):
    player_choice = bottle.request.forms.get('player_choice')
    rps_controller.play(game_id, player_choice)
    bottle.redirect(f'/rps/{game_id}/')

# Bottle apparently has some pathing problems on windows as per https://stackoverflow.com/questions/18460924/bottlepy-template-not-found
# so we determine relative path to 'views' directory at runtime

# abs_app_dir_path = os.path.dirname(os.path.realpath(__file__))
# abs_views_path = os.path.join(abs_app_dir_path, 'views')
# bottle.TEMPLATE_PATH.insert(0, 'views' )

bottle.run(reloader=True)