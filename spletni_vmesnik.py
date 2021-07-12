import bottle
import os     

@bottle.get('/')
def hello_world():
    return bottle.template('hello_world.html')

# Bottle apparently has some pathing problems on windows as per https://stackoverflow.com/questions/18460924/bottlepy-template-not-found
# so we determine relative path to 'views' directory at runtime
abs_app_dir_path = os.path.dirname(os.path.realpath(__file__))
abs_views_path = os.path.join(abs_app_dir_path, 'views')
bottle.TEMPLATE_PATH.insert(0, 'views' )

bottle.run(reloader=True)