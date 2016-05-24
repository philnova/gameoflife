import flask
import flask.ext.sqlalchemy
from views.conway import Draw, LoginBackend, Login, LogoutBackend, SaveBackend, Save, UserProfile, EditUser, EditUserBackend
from views.conway import RenameBoard, RenameBoardBackend, DeleteBoard, DeleteBoardBackend, DeleteUser, DeleteUserBackend, Load
from views.conway import SetPrivacy, SetPrivacyBackend, Browse, Like, Dislike, About
from flask import session as login_session
import json
import urlparse

import os
import psycopg2
import urlparse



class Route(object):

    def __init__(self, url, route_name, resource):
        self.url = url
        self.route_name = route_name
        self.resource = resource

handlers = [
    Route('/', 'draw', Draw),
    Route('/load/<int:id>', 'load', Load),
    Route('/loginbackend', 'loginbackend', LoginBackend),
    Route('/login', 'login', Login),
    Route('/logout', 'logout', LogoutBackend),
    Route('/saveform/', 'savebackend', SaveBackend),
    Route('/save/', 'save', Save),
    Route('/profile', 'userprofile', UserProfile),
    Route('/profile/edit', 'editprofile', EditUser),
    Route('/profile/edit/backend', 'editprofilebackend', EditUserBackend),
    Route('/board/<int:id>/delete', 'deleteboard', DeleteBoard),
    Route('/board/<int:id>/delete/backend', 'deleteboardbackend', DeleteBoardBackend),
    Route('/board/<int:id>/rename/backend', 'renameboardbackend', RenameBoardBackend),
    Route('/board/<int:id>/rename', 'renameboard', RenameBoard),
    Route('/profile/delete', 'deleteuser', DeleteUser),
    Route('/profile/delete/backend', 'deleteuserbackend', DeleteUserBackend),
    Route('/profile/<int:id>/setprivacy', 'setprivacy', SetPrivacy),
    Route('/profile/<int:id>/setprivacybackend', 'setprivacybackend', SetPrivacyBackend),
    Route('/browse', 'browse', Browse),
    Route('/like/<int:id>', 'like', Like),
    Route('/dislike/<int:id>', 'dislike', Dislike),
    Route('/about', 'about', About),
]

APPLICATION_NAME = "Conway"

class Application(object):

    def __init__(self, routes, config, debug=True):
        self.flask_app = flask.Flask(__name__)
        self.routes = routes
        self.debug = debug
        self.login_session = login_session
        self._configure_app(config)
        self._set_routes()

    def _set_routes(self):
        for route in self.routes:
            app_view = route.resource.as_view(route.route_name)
            self.flask_app.add_url_rule(route.url, view_func=app_view)

    def _configure_app(self, config):

        self.flask_app.config['SQLALCHEMY_DATABASE_URI'] =config['DATABASE_URL']

        self.flask_app.secret_key = "asupersecr3tkeyshouldgo"

        self.db = flask.ext.sqlalchemy.SQLAlchemy(self.flask_app)

        self.google_client_id = config['GOOGLE_CLIENT_ID']
        self.google_client_secret = config['GOOGLE_CLIENT_SECRET']
        self.development = bool(config.get('DEVELOPMENT'))



    def start_app(self):
        self.flask_app.run(debug=self.debug)


