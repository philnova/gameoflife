#imports
from flask.views import MethodView
from flask import render_template
from flask import Flask, render_template, request, redirect, jsonify, url_for, flash
from flask import make_response
from flask import request, redirect, url_for

import requests
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json

import random
import string
import arrow
import datetime

from forms.saveform import SaveForm
from forms.edituserform import EditUserForm
from forms.renameboardform import RenameBoardForm
from forms.setprivacyform import SetPrivacyForm
import gameoflife
from models.users import Base, User, Board, Rating

###########
# helpers #
###########

def confirm_login(login_session):
    if login_session.get('name') is not None:
        return True
    else:
        return False

def createUser(login_session):
    newUser = User(name=login_session['name'], google_id=login_session['google_id'])
    gameoflife.session.commit()
    gameoflife.session.add(newUser)
    gameoflife.session.commit()
    user = gameoflife.session.query(User).filter_by(google_id=login_session['google_id']).one()
    return user.id

def getUserInfo(user_id):
    user = gameoflife.session.query(User).filter_by(id=user_id).one()
    return user

def getUserID(google_id):
    try:
        user = gameoflife.session.query(User).filter_by(google_id=google_id).one()
        return user.id
    except:
        return None

##########
# routes #
##########

class LogoutBackend(MethodView):

    def get(self):
        try:
            revoke = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % gameoflife.login_session['access_token']
            gameoflife.login_session.clear()
            flash('You have been logged out')
            return render_template('login/logout.html', revoke = revoke, development=gameoflife.app.development)
        except:
            print "No access token"
            gameoflife.login_session.clear()
            flash('A server error occurred. Please log in again.')
            return redirect(url_for('draw',load=None, development=gameoflife.app.development))

class Logout(MethodView):

    def get(self):
        access_token = gameoflife.login_session.get('access_token')
        if access_token is None:
            print 'Access Token is None'
            response = make_response(json.dumps('Current user not connected.'), 401)
            response.headers['Content-Type'] = 'application/json'
            return response
        url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % gameoflife.login_session['access_token']
        h = httplib2.Http()
        result = h.request(url, 'GET')[0]

        if result['status'] == '200':
            username = getUserInfo(gameoflife.login_session['user_id']).name
            del gameoflife.login_session['access_token'] 
            del gameoflife.login_session['google_id']
            del gameoflife.login_session['user_id']
            gameoflife.login_session.clear()
            #response = make_response(json.dumps('You have logged out'), 200)
            #response.headers['Content-Type'] = 'application/json'
            #return response
            flash('User {0} has been logged out'.format(username))
            return redirect(url_for('draw'))
        else:
      
          response = make_response(json.dumps('Failed to revoke token for given user.', 400))
          response.headers['Content-Type'] = 'application/json'
          return response

class Login(MethodView):

    def get(self):
        gameoflife.login_session.clear()
        state = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in xrange(32))
        gameoflife.login_session['state'] = state
        return render_template('login/login.html', STATE=state, development=gameoflife.app.development)

class LoginBackend(MethodView):

    def post(self):
        if request.args.get('state') != gameoflife.login_session['state']:
            response = make_response(json.dumps('Invalid state parameter.'), 401)
            response.headers['Content-Type'] = 'application/json'
            return response
        else:
            print 'state parameter valid'
        # Obtain authorization code
        code = request.data

        try:
            # Upgrade the authorization code into a credentials object
            oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
            oauth_flow.redirect_uri = 'postmessage'
            credentials = oauth_flow.step2_exchange(code)
            print 'auth code upgraded to credentials'
        except FlowExchangeError:
            response = make_response(
                json.dumps('Failed to upgrade the authorization code.'), 401)
            response.headers['Content-Type'] = 'application/json'
            return response

        # Check that the access token is valid.
        access_token = credentials.access_token
        url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token={0}'.format(access_token))
        h = httplib2.Http()
        result = json.loads(h.request(url, 'GET')[1])
        # If there was an error in the access token info, abort.
        if result.get('error') is not None:
            print 'there was an error in the access token!'
            response = make_response(json.dumps(result.get('error')), 500)
            response.headers['Content-Type'] = 'application/json'

        #Verify that the access token is used for the intended user.
        u_id = credentials.id_token['sub']
        if result['user_id'] != u_id:
            response = make_response(
                json.dumps("Token's user ID doesn't match given user ID."), 401)
            response.headers['Content-Type'] = 'application/json'
            return response


        # Verify that the access token is valid for this app.
        if result['issued_to'] != gameoflife.client_id:
            response = make_response(
                json.dumps("Token's client ID does not match app's."), 401)
            response.headers['Content-Type'] = 'application/json'
            return response


        # Store the access token in the session for later use.
        gameoflife.login_session['access_token'] = credentials.access_token

        # Get user info
        userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
        params = {'access_token': credentials.access_token, 'alt': 'json'}
        answer = requests.get(userinfo_url, params=params)

        data = answer.json()

        gameoflife.login_session['google_id'] = data['id']
        gameoflife.login_session['name'] = data['name']

        print 'user info obtained'
        # check if user is already in the database
        if getUserID(gameoflife.login_session['google_id']) is None:
            print 'creating new user'
            createUser(gameoflife.login_session)
            print 'new user created'
        else: # not a new user
            pass # might add some additional logic here later

        print 'getting user info'
        current_user = gameoflife.session.query(User).filter_by(google_id=gameoflife.login_session['google_id']).one()
        gameoflife.login_session['user_id'] = current_user.id
        print 'Current user.id is ', current_user.id
        flash("You are now logged in as {0}".format(current_user.name))
        return '<p> </p>'

class Save(MethodView):

    def post(self):
        if gameoflife.login_session.get('user_id') is not None:
            form = SaveForm()
            rules = 'B'+validate_conditions(request.form['birth'], default='2')+'S'+validate_conditions(request.form['survival'], default='23')
            return render_template('social/save.html', form=form, seed=request.form['grid'], xdim=request.form['x'], ydim=request.form['y'], rules=rules, development=gameoflife.app.development, user_logged_in=(gameoflife.login_session.get('name')!=None))
        else:
            return render_template('main.html', user_logged_in = False, development=gameoflife.app.development, loaded_board='')

def validate_conditions(condition_string, default):
    for i in condition_string:
        try:
            if 0 <= int(i) <= 8:
                pass
            else:
                print 'Disallowed value detected; returning default'
                return default
        except:
            return default

    condition_string = [i for i in sorted(list(set(list(condition_string))))]
    return ''.join(condition_string)


class SaveBackend(MethodView):
    def post(self):
        if gameoflife.login_session.get('user_id') is not None:
            form = SaveForm(request.form)

            if form.validate():
                xdim = request.form['xdim']
                ydim = request.form['ydim']
                seed = request.form['seed']
                rules = request.form['rules']

                newBoard = Board(user_id=gameoflife.login_session['user_id'], nickname=form.data['nickname'], xdim = xdim, ydim = ydim, seed=seed, rules = rules, shared=form.data['shared'])
                gameoflife.session.add(newBoard)
                gameoflife.session.flush() #allows us access to primary key

                newRating = Rating(user_id=gameoflife.login_session['user_id'], board_id = newBoard.id, like=True)
                gameoflife.session.add(newRating)
                gameoflife.session.commit()

                flash('Your board has been saved with the nickname: {0}!'.format(form.data['nickname']))
                return redirect(url_for('userprofile'), code=303)
            else:
                print form.data
                return render_template('social/save.html', form=form, rules = request.form['rules'], xdim = request.form['xdim'], ydim = request.form['ydim'], seed = request.form['seed'], development=gameoflife.app.development, user_logged_in=(gameoflife.login_session.get('name')!=None)), 400
        else:
            return render_template('main.html', user_logged_in = False, development=gameoflife.app.development, loaded_board='')

class UserProfile(MethodView):
    def get(self):
        if confirm_login(gameoflife.login_session):
            current_user = getUserInfo(gameoflife.login_session['user_id'])
            boards = gameoflife.session.query(Board).filter_by(user_id=current_user.id).all()
            ratings_num = [gameoflife.session.query(Rating).filter_by(board_id=board.id, like=True, user_id = current_user.id).count() for board in boards]
            ratings_denom = [gameoflife.session.query(Rating).filter_by(board_id=board.id, user_id = current_user.id).count() for board in boards]
            ratings = [int(ratings_num[i]/float(ratings_denom[i]) * 100) for i in range(len(ratings_num))]
            thumbs_down = [ratings_denom[i] - ratings_num[i] for i in range(len(ratings_num))]
            return render_template('social/profile.html', user=current_user, boards = boards, ratings=ratings, thumbs_down=thumbs_down, thumbs_up=ratings_num, development=gameoflife.app.development, user_logged_in=(gameoflife.login_session.get('name')!=None))
        else:
            return render_template('main.html', user_logged_in = False, development=gameoflife.app.development, loaded_board='')

class DeleteBoardBackend(MethodView):
    def get(self, id):
        if confirm_login(gameoflife.login_session):
            user = getUserInfo(gameoflife.login_session['user_id'])
            board = gameoflife.session.query(Board).filter_by(id=id).one()
            ratings = gameoflife.session.query(Rating).filter_by(board_id = id).all()
            print 'board id: ', id
            if board.user_id == user.id:
                for rating in ratings:
                    print rating.board_id
                    gameoflife.session.delete(rating)
                gameoflife.session.commit()
                gameoflife.session.delete(board)
                gameoflife.session.commit()
                flash('Your board was deleted')
            else:
                flash("Whoa, buddy. You don't have persmission to delete that board!")
            return redirect(url_for('userprofile'))
        else:
            return render_template('main.html', user_logged_in = False, development=gameoflife.app.development, loaded_board='')

class DeleteBoard(MethodView):
    def get(self, id):
        if confirm_login(gameoflife.login_session):
            return render_template('social/deleteboard.html', id=id, user_logged_in=(gameoflife.login_session.get('name')!=None))
        else:
            return render_template('main.html', user_logged_in = False, development=gameoflife.app.development, loaded_board='')

class DeleteUserBackend(MethodView):
    def get(self):
        if confirm_login(gameoflife.login_session):
            user = getUserInfo(gameoflife.login_session['user_id'])
            boards = gameoflife.session.query(Board).filter_by(user_id=user.id).all()
            ratings = gameoflife.session.query(Rating).filter_by(user_id=user.id).all()
            for rating in ratings:
                gameoflife.session.delete(rating)
            gameoflife.session.commit()
            for board in boards:
                gameoflife.session.delete(board)
            gameoflife.session.commit()
            gameoflife.session.delete(user)
            gameoflife.session.commit()
            gameoflife.login_session.clear()
            flash('Your user account and all saved boards have been deleted')
            return redirect(url_for('draw',load=None))
        else:
            return render_template('main.html', user_logged_in = False, development=gameoflife.app.development, loaded_board='')

class DeleteUser(MethodView):
    def get(self):
        if confirm_login(gameoflife.login_session):
            return render_template('user/delete.html', development=gameoflife.app.development, user_logged_in=True)
        else:
            return render_template('main.html', user_logged_in = False, development=gameoflife.app.development, loaded_board='')

class UserProfile(MethodView):
    def get(self):
        current_user = getUserInfo(gameoflife.login_session['user_id'])
        boards = gameoflife.session.query(Board).filter_by(user_id=current_user.id).all()
        ratings_num = [gameoflife.session.query(Rating).filter_by(board_id=board.id, like=True, user_id = current_user.id).count() for board in boards]
        ratings_denom = [gameoflife.session.query(Rating).filter_by(board_id=board.id, user_id = current_user.id).count() for board in boards]
        print ratings_num, ratings_denom
        ratings = [int(ratings_num[i]/float(ratings_denom[i]) * 100) for i in range(len(ratings_num))]
        thumbs_down = [ratings_denom[i] - ratings_num[i] for i in range(len(ratings_num))]
        #board_ids = ''
        #for board in boards:
        #    board_ids += str(board.id)
        print gameoflife.app.development
        return render_template('social/profile.html', user=current_user, boards = boards, ratings=ratings, thumbs_down=thumbs_down, thumbs_up=ratings_num, development=gameoflife.app.development, user_logged_in=(gameoflife.login_session.get('name')!=None))

class DeleteBoardBackend(MethodView):
    def get(self, id):
        if confirm_login(gameoflife.login_session):
            user = getUserInfo(gameoflife.login_session['user_id'])
            board = gameoflife.session.query(Board).filter_by(id=id).one()
            ratings = gameoflife.session.query(Rating).filter_by(board_id = id).all()
            print 'board id: ', id
            if board.user_id == user.id:
                for rating in ratings:
                    print rating.board_id
                    gameoflife.session.delete(rating)
                gameoflife.session.commit()
                gameoflife.session.delete(board)
                gameoflife.session.commit()
                flash('Your board was deleted')
            else:
                flash("Whoa, buddy. You don't have persmission to delete that board!")
            return redirect(url_for('userprofile'))
        else:
            return render_template('main.html', user_logged_in = False, development=gameoflife.app.development, loaded_board='')

class DeleteBoard(MethodView):
    def get(self, id):
        if confirm_login(gameoflife.login_session):
            return render_template('social/deleteboard.html', id=id, user_logged_in=(gameoflife.login_session.get('name')!=None))
        else:
            return render_template('main.html', user_logged_in = False, development=gameoflife.app.development, loaded_board='')

class DeleteUserBackend(MethodView):
    def get(self):
        if confirm_login(gameoflife.login_session):
            user = getUserInfo(gameoflife.login_session['user_id'])
            boards = gameoflife.session.query(Board).filter_by(user_id=user.id).all()
            ratings = gameoflife.session.query(Rating).filter_by(user_id=user.id).all()
            for rating in ratings:
                gameoflife.session.delete(rating)
            gameoflife.session.commit()
            for board in boards:
                gameoflife.session.delete(board)
            gameoflife.session.commit()
            gameoflife.session.delete(user)
            gameoflife.session.commit()
            gameoflife.login_session.clear()
            flash('Your user account and all saved boards have been deleted')
            return redirect(url_for('draw',load=None))
        else:
            return render_template('main.html', user_logged_in = False, development=gameoflife.app.development, loaded_board='')

class DeleteUser(MethodView):
    def get(self):
        if confirm_login(gameoflife.login_session):
            return render_template('user/delete.html', development=gameoflife.app.development, user_logged_in=True)
        else:
            return render_template('main.html', user_logged_in = False, development=gameoflife.app.development, loaded_board='')

class RenameBoard(MethodView):
    #confirm user has privelege to rename this board!
    def get(self, id):
        if confirm_login(gameoflife.login_session):
            board = gameoflife.session.query(Board).filter_by(id=id).one()
            form = RenameBoardForm()
            form.nickname.default = board.nickname
            form.process()
            return render_template('social/renameboard.html', form=form, id=id, development=gameoflife.app.development, user_logged_in=True)
        else:
            return render_template('main.html', user_logged_in = False, development=gameoflife.app.development, loaded_board='')

class RenameBoardBackend(MethodView):
    def post(self, id):
        if confirm_login(gameoflife.login_session):
            user = getUserInfo(gameoflife.login_session['user_id'])
            board = gameoflife.session.query(Board).filter_by(id=id).one()
            if user.id == board.user_id:
                form = RenameBoardForm(request.form)
                if form.validate():
                    board.nickname = request.form['nickname']
                    gameoflife.session.add(board)
                    gameoflife.session.commit()
                    flash('Rename successful!')
                    return redirect(url_for('userprofile'), code=303)
                else:
                    return render_template('social/renameboard.html', form=form, id=id, development=gameoflife.app.development, user_logged_in=True)
            else:
                flash('Permission denied!')
                return redirect(url_for('userprofile'))
        else:
            return render_template('main.html', user_logged_in = False, development=gameoflife.app.development, loaded_board='')

class SetPrivacy(MethodView):
    def get(self, id):
        if confirm_login(gameoflife.login_session):
            board = gameoflife.session.query(Board).filter_by(id=id).one()
            form = SetPrivacyForm()
            return render_template('social/setprivacy.html', id=id, board=board, form=form, development=gameoflife.app.development, user_logged_in=True)
        else:
            return render_template('main.html', user_logged_in = False, development=gameoflife.app.development, loaded_board='')

class SetPrivacyBackend(MethodView):
    def post(self, id):
        if confirm_login(gameoflife.login_session):
            user = getUserInfo(gameoflife.login_session['user_id'])
            board = gameoflife.session.query(Board).filter_by(id=id).one()
            if user.id == board.user_id:
                form = SetPrivacyForm(request.form)
                if form.validate():
                    board.shared = (request.form['privacy'] == 'share')
                    gameoflife.session.add(board)
                    gameoflife.session.commit()
                    flash('Privacy settings for {0} updated!'.format(board.nickname))
                    return redirect(url_for('userprofile'), code=303)
                else:
                    return render_template('social/setprivacy.html', board=board, form=form, development=gameoflife.app.development, user_logged_in=True)
            else:
                flash('Permission denied!')
                return redirect(url_for('userprofile'))
        else:
            return render_template('main.html', user_logged_in = False, development=gameoflife.app.development, loaded_board='')

class RenameBoard(MethodView):
    def get(self, id):
        if confirm_login(gameoflife.login_session):
            board = gameoflife.session.query(Board).filter_by(id=id).one()
            form = RenameBoardForm()
            form.nickname.default = board.nickname
            form.process()
            return render_template('social/renameboard.html', form=form, id=id, development=gameoflife.app.development, user_logged_in=True)
        else:
            return render_template('main.html', user_logged_in = False, development=gameoflife.app.development, loaded_board='')

class RenameBoardBackend(MethodView):
    def post(self, id):
        if confirm_login(gameoflife.login_session):
            user = getUserInfo(gameoflife.login_session['user_id'])
            board = gameoflife.session.query(Board).filter_by(id=id).one()
            if user.id == board.user_id:
                form = RenameBoardForm(request.form)
                if form.validate():
                    board.nickname = request.form['nickname']
                    gameoflife.session.add(board)
                    gameoflife.session.commit()
                    flash('Rename successful!')
                    return redirect(url_for('userprofile'), code=303)
                else:
                    return render_template('social/renameboard.html', form=form, id=id, development=gameoflife.app.development, user_logged_in=True)
            else:
                flash('Permission denied!')
                return redirect(url_for('userprofile'))
        else:
            return render_template('main.html', user_logged_in = False, development=gameoflife.app.development, loaded_board='')

class SetPrivacy(MethodView):
    def get(self, id):
        if confirm_login(gameoflife.login_session):
            board = gameoflife.session.query(Board).filter_by(id=id).one()
            form = SetPrivacyForm()
            return render_template('social/setprivacy.html', id=id, board=board, form=form, development=gameoflife.app.development, user_logged_in=True)
        else:
            return render_template('main.html', user_logged_in = False, development=gameoflife.app.development, loaded_board='')

class SetPrivacyBackend(MethodView):
    def post(self, id):
        if confirm_login(gameoflife.login_session):
            user = getUserInfo(gameoflife.login_session['user_id'])
            board = gameoflife.session.query(Board).filter_by(id=id).one()
            if user.id == board.user_id:
                form = SetPrivacyForm(request.form)
                if form.validate():
                    board.shared = (request.form['privacy'] == 'share')
                    gameoflife.session.add(board)
                    gameoflife.session.commit()
                    flash('Privacy settings for {0} updated!'.format(board.nickname))
                    return redirect(url_for('userprofile'), code=303)
                else:
                    return render_template('social/setprivacy.html', board=board, form=form, development=gameoflife.app.development, user_logged_in=True)
            else:
                flash('Permission denied!')
                return redirect(url_for('userprofile'))
        else:
            return render_template('main.html', user_logged_in = False, development=gameoflife.app.development, loaded_board='')


class EditUserBackend(MethodView):
    def post(self):
        if gameoflife.login_session.get('user_id') is not None:
            form = EditUserForm(request.form)
            if form.validate():
                user = getUserInfo(gameoflife.login_session['user_id'])
                user.name = request.form['name']
                gameoflife.session.add(user)
                gameoflife.session.commit()
                flash('Your username has been changed to {0}'.format(user.name))
                return redirect(url_for('userprofile'), code=303)
            else:
                return render_template('social/edituser.html', form=form, user=current_user, development=gameoflife.app.development, user_logged_in=True)
        else:
            return render_template('main.html', user_logged_in = False, development=gameoflife.app.development, loaded_board='')

class EditUser(MethodView):
    def get(self):
        if gameoflife.login_session.get('user_id') is not None:
            current_user = getUserInfo(gameoflife.login_session['user_id'])
            form = EditUserForm()
            form.name.default = current_user.name
            form.process()
            return render_template('social/edituser.html', form=form, user=current_user, development=gameoflife.app.development, user_logged_in=True)
        else:
            return render_template('main.html', user_logged_in = False, development=gameoflife.app.development, loaded_board='')

class Load(MethodView):
    def get(self, id):
        board = gameoflife.session.query(Board).filter_by(id=id).one()
        if board.shared == True or board.user_id == gameoflife.login_session.get('user_id'):
            if gameoflife.login_session.get('name') is not None:
                return render_template('main.html', user_logged_in=True, loaded_board=board, development=gameoflife.app.development)
            else:
                return render_template('main.html', user_logged_in=False, loaded_board=board, development=gameoflife.app.development)
        else:
            flash('Sorry, that board is not public!')
            if gameoflife.login_session.get('name') is not None:
                return render_template('main.html', user_logged_in=True, loaded_board=board, development=gameoflife.app.development)
            else:
                return render_template('main.html', user_logged_in=False, loaded_board=board, development=gameoflife.app.development)

class Like(MethodView):
    def get(self, id):
        if confirm_login(gameoflife.login_session):
            board = gameoflife.session.query(Board).filter_by(id=id).one()
            user = getUserInfo(gameoflife.login_session['user_id'])
            if board.shared == True:
                if gameoflife.session.query(Rating).filter_by(board_id = id, user_id = user.id).count():
                    #rating already exists and is being updated
                    newRating = gameoflife.session.query(Rating).filter_by(board_id = id, user_id=user.id).one()
                    newRating.like = True
                else:
                    newRating = Rating(user_id = user.id, board_id = board.id, like=True)
                    gameoflife.session.add(newRating)
                    gameoflife.session.commit()
                    return redirect(url_for('load', id=board.id))

            else:
                flash('Sorry, that board is not public!')
                return render_template('main.html', user_logged_in=(gameoflife.login_session.get('name')!=None), loaded_board='', development=gameoflife.app.development)
        else:
            return render_template('main.html', user_logged_in = False, development=gameoflife.app.development, loaded_board='')

class Dislike(MethodView):
    def get(self, id):
        if confirm_login(gameoflife.login_session):
            board = gameoflife.session.query(Board).filter_by(id=id).one()
            user = getUserInfo(gameoflife.login_session['user_id'])
            if board.shared == True:
                if gameoflife.session.query(Rating).filter_by(board_id = id, user_id = user.id).count():
                    #rating already exists and is being updated
                    newRating = gameoflife.session.query(Rating).filter_by(board_id = id, user_id=user.id).one()
                    newRating.like = False
                else:
                    newRating = Rating(user_id = user.id, board_id = board.id, like=False)
                gameoflife.session.add(newRating)
                gameoflife.session.commit()
                return redirect(url_for('load', id=board.id))

            else:
                flash('Sorry, that board is not public!')
                return render_template('main.html', user_logged_in=(gameoflife.login_session.get('name')!=None), loaded_board='', development=gameoflife.app.development)
        else:
            return render_template('main.html', user_logged_in = False, development=gameoflife.app.development, loaded_board='')

class Browse(MethodView):
    def get(self):
        boards = gameoflife.session.query(Board).filter_by(shared=True).all()
        users = [gameoflife.session.query(User).filter_by(id=board.user_id).one().name for board in boards]
        ratings_num = [gameoflife.session.query(Rating).filter_by(board_id=board.id, like=True).count() for board in boards]
        ratings_denom = [gameoflife.session.query(Rating).filter_by(board_id=board.id).count() for board in boards]
        ratings = [int(ratings_num[i]/float(ratings_denom[i]) * 100) for i in range(len(ratings_num))]
        #print users
        #print boards
        #print ratings
        thumbs_down = [ratings_denom[i] - ratings_num[i] for i in range(len(ratings_num))]

        return render_template('social/browse.html', user_logged_in=(gameoflife.login_session.get('name')!=None), boards=boards, users=users, ratings=ratings, thumbs_up = ratings_num, thumbs_down=thumbs_down, development=gameoflife.app.development)

class Draw(MethodView):
    def get(self):
        if gameoflife.login_session.get('name') is not None:
            return render_template('main.html', user_logged_in=True, loaded_board='', development=gameoflife.app.development)
        else:
            return render_template('main.html', user_logged_in = False, loaded_board='', development=gameoflife.app.development)

class About(MethodView):
    def get(self):
        return render_template('about.html', development=gameoflife.app.development, user_logged_in=(gameoflife.login_session.get('name')!=None))



