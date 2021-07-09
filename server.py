#!/bin/python
import os
import jinja2
import random
import sys

import cherrypy

ALLOWED_ANIMATION_FILE_TYPES = ['gif']


def is_animated_file(file_name):
    ending = file_name.split('.')[-1]
    return ending in ALLOWED_ANIMATION_FILE_TYPES


class Server(object):

    instance = None

    def __init__(self, port, files_root=None):
        if Server.instance is not None:
            raise Exception('Server already started')
        dispatcher = cherrypy.dispatch.RoutesDispatcher()
        dispatcher.connect('index', '/', controller=self, action='index')
        self.templateLoader = jinja2.FileSystemLoader(searchpath='./')
        self.templateEnv = jinja2.Environment(loader=self.templateLoader)
        self.port = port
        self.conf = {
            '/': {
                'request.dispatch': dispatcher,
            }
        }
        if files_root is None:
            self.anim_root = os.path.abspath(os.path.dirname(__file__))
        else:
            self.anim_root = files_root
        self.anim_dir = self.anim_root + '/anim'
        self.anim_files_conf = {
            '/': {
                'tools.staticdir.root': self.anim_root,
                'tools.staticdir.on': True,
                'tools.staticdir.dir': 'anim',
            }
        }
        self.files_root = os.path.abspath(os.path.dirname(__file__))
        self.files_conf = {
            '/': {
                'tools.staticdir.root': self.files_root,
                'tools.staticdir.on': True,
                'tools.staticdir.dir': 'files',
            }
        }
        cherrypy.server.socket_port = port
        cherrypy.server.socket_host = '0.0.0.0'
        cherrypy.tree.mount(None, '/anim', config=self.anim_files_conf)
        cherrypy.tree.mount(None, '/files', config=self.files_conf)
        app = cherrypy.tree.mount(root=None, config=self.conf)
        cherrypy.quickstart(app)

    def index(self):
        template = self.templateEnv.get_template('index.html')
        return template.render(gif_file=self.random_animated_file())

    def random_animated_file(self):
        dir = os.listdir(self.anim_dir)
        dir = [file for file in dir if is_animated_file(file)]
        return random.choice(dir)


if __name__ == '__main__':
    if len(sys.argv) == 2:
        print("Root = ")
        print(sys.argv[1])
        Server(8080, sys.argv[1])
    else:
        Server(8080)
