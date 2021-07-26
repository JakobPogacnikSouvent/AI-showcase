import bottle
import os
from model import RPS_controller, TIAR_controller, FIAR_controller, User

rps_controller = RPS_controller()
tiar_controller = TIAR_controller()
fiar_controller = FIAR_controller()

USERNAME_COOKIE = "username"
COOKIE_SECRET = 'A common mistake that people make when trying to design something completely foolproof is to underestimate the ingenuity of complete fools.'

@bottle.get('/')
def home():
    user = get_current_user() # Also validates login

    return bottle.template('home2.html', user=user)

def validate_login():
    username = bottle.request.get_cookie(USERNAME_COOKIE, secret=COOKIE_SECRET)
    if not username:
        bottle.redirect('/login/')

def get_current_user():
    username = bottle.request.get_cookie(USERNAME_COOKIE, secret=COOKIE_SECRET)
    if not username:
        bottle.redirect('/login/')
    return username

@bottle.post('/rps/')
def rps_new_game():
    user = get_current_user() # Also validates login
    game_id = rps_controller.new_game()
    bottle.redirect(f'/rps/{game_id}/')

@bottle.get('/rps/<game_id:int>/')
def rps(game_id):
    user = get_current_user() # Also validates login

    game = rps_controller.games[game_id]
    return bottle.template('rps2.html', game=game, game_id=game_id, user=user)

@bottle.post('/rps/<game_id:int>/')
def rps_update(game_id):
    player_choice = bottle.request.forms.get('player_choice')
    rps_controller.play(game_id, player_choice)
    bottle.redirect(f'/rps/{game_id}/')

@bottle.post('/tiar/')
def tiar_new_game():
    user = get_current_user() # Also validates login
    game_id = tiar_controller.new_game()
    bottle.redirect(f'/tiar/{game_id}/')

@bottle.get('/tiar/<game_id:int>/')
def tiar(game_id):
    user = get_current_user() # Also validates login

    game = tiar_controller.games[game_id]
    return bottle.template('tiar.html', game=game, game_id=game_id, user=user)

@bottle.post('/tiar/<game_id:int>/')
def tiar_update(game_id):
    x, y = list(map(int, bottle.request.forms.get('coords').split(',')))
    tiar_controller.player_play(game_id, x, y)
    bottle.redirect(f'/tiar/{game_id}/')

@bottle.post('/fiar/')
def fiar_new_game():
    user = get_current_user() # Also validates login
    game_id = fiar_controller.new_game()
    bottle.redirect(f'/fiar/{game_id}/')

@bottle.get('/fiar/<game_id:int>/')
def fiar(game_id):
    user = get_current_user() # Also validates login

    game = fiar_controller.games[game_id]
    return bottle.template('fiar.html', game=game, game_id=game_id, user=user)

@bottle.post('/fiar/<game_id:int>/')
def fiar_update(game_id):
    column = int(bottle.request.forms.get('column'))
    fiar_controller.player_play(game_id, column)
    bottle.redirect(f'/fiar/{game_id}/')

@bottle.get('/login/')
def login_get():
    return bottle.template('login.html', error=None)

@bottle.post('/login/')
def login_post():
    password_cleartext = bottle.request.params.get('password')
    username = bottle.request.params.get('username')
    
    if not username or not password_cleartext:
        return bottle.template('login.html', error='Please input username or password.')

    try:
        # Check if correct username and password
        User.login(username, password_cleartext) # Raises value erorr on incorect login

        # Login
        bottle.response.set_cookie(USERNAME_COOKIE, username, path="/", secret=COOKIE_SECRET)
        bottle.redirect("/")
    except ValueError as e:
        return bottle.template('login.html', error=e)

@bottle.post('/logout/')
def logout_post():
    bottle.response.delete_cookie(USERNAME_COOKIE, path='/')
    bottle.redirect('/')

@bottle.get('/register/')
def register_get():
    return bottle.template('register.html', error=None)

@bottle.post('/register/')
def register_post():
    username = bottle.request.forms.get('username')
    password_cleartext = bottle.request.forms.get('password')
    if not username or not password_cleartext:
        return bottle.template('register.html', error='Username or password cannot be empty.')
    
    try:
        User.register(username, password_cleartext) # Raises ValueError if user already exists
        
        # Login user
        bottle.response.set_cookie(USERNAME_COOKIE, username, path="/", secret=COOKIE_SECRET)
        bottle.redirect("/")
    except ValueError as e:
        return bottle.template('register.html', error=e)

@bottle.get('/test/')
def test():
    return bottle.template('imagetest.html')

@bottle.route('/static/<picture>')
def serve_picture(picture):
    return bottle.static_file(picture, root='static')


# Bottle apparently has some pathing problems on windows as per https://stackoverflow.com/questions/18460924/bottlepy-template-not-found
# so we determine relative path to 'views' directory at runtime

# abs_app_dir_path = os.path.dirname(os.path.realpath(__file__))
# abs_views_path = os.path.join(abs_app_dir_path, 'views')
# bottle.TEMPLATE_PATH.insert(0, 'views' )

if __name__ == '__main__':
    bottle.run(reloader=True)