#!/usr/bin/python
# -*- coding: utf-8; mode: python -*-
import requests
from flask import Flask, request, redirect, url_for, flash, render_template
from flask_oauthlib.client import OAuth
from requests_oauthlib import OAuth1

app = Flask(__name__)
app.config['DEBUG'] = True
oauth = OAuth()
mySession=None
currentUser=None

app.secret_key = 'development'

twitter = oauth.remote_app('twitter',
    base_url='https://api.twitter.com/1.1/',
    request_token_url='https://api.twitter.com/oauth/request_token',
    access_token_url='https://api.twitter.com/oauth/access_token',
    authorize_url='https://api.twitter.com/oauth/authenticate',
    consumer_key='Yn8j64BqsI3VdWzyzLDFOfdoe',
    consumer_secret='GYyd6D0PwuBmIMhMi3ycUkHpTBVbdlO6j7MSeDir2NW3iRXUTh'
)

consumer_key = 'Yn8j64BqsI3VdWzyzLDFOfdoe'
consumer_key_secret = 'GYyd6D0PwuBmIMhMi3ycUkHpTBVbdlO6j7MSeDir2NW3iRXUTh'


# Obtener token para esta sesion
@twitter.tokengetter
def get_twitter_token(token=None):
    global mySession
    
    if mySession is not None:
        return mySession['oauth_token'], mySession['oauth_token_secret']

    
# Limpiar sesion anterior e incluir la nueva sesion
@app.before_request
def before_request():
    global mySession
    global currentUser
    
    currentUser = None
    if mySession is not None:
        currentUser = mySession
        

# Pagina principal
@app.route('/')
def index():
    global currentUser
    
    tweets = None
    if currentUser is not None:
        resp = twitter.request('statuses/home_timeline.json')
        if resp.status == 200:
            tweets = resp.data
        else:
            flash('Imposible acceder a Twitter.')
    return render_template('index.html', user=currentUser, tweets=tweets)


# Get auth token (request)
@app.route('/login')
def login():
    callback_url=url_for('oauthorized', next=request.args.get('next'))
    return twitter.authorize(callback=callback_url or request.referrer or None)


# Eliminar sesion
@app.route('/logout')
def logout():
    global mySession
    
    mySession = None
    flash('Ya no estas logeado', 'message')
    return redirect(url_for('index'))


# Callback
@app.route('/oauthorized')
def oauthorized():
    global mySession
    
    resp = twitter.authorized_response()
    if resp is None:
        flash('You denied the request to sign in.', 'error')
    else:
        mySession = resp
        flash('Estas logeado', 'message')

    return redirect(url_for('index', next=request.args.get('next')))


# Operaciones
@app.route('/deleteTweet', methods=['POST'])
def deleteTweet():
    global currentUser

    if currentUser is None:
        return redirect(url_for('login'))

    deleteID = request.form['deleteID']

    oauth = OAuth1(consumer_key,
     client_secret=consumer_key_secret,
      resource_owner_key=mySession['oauth_token'],
       resource_owner_secret=mySession['oauth_token_secret'])

    resp = requests.post('https://api.twitter.com/1.1/statuses/destroy.json', data={'id': deleteID}, auth=oauth)

    if resp.status_code is 200:
        flash('Has borrado el tweet!', 'message')
    return redirect(url_for('index'))



@app.route('/retweet', methods=['POST'])
def retweet():
    global currentUser
    global mySession

    if currentUser is None:
        return redirect(url_for('login'))

    oauth = OAuth1(consumer_key,
     client_secret=consumer_key_secret,
      resource_owner_key=mySession['oauth_token'],
       resource_owner_secret=mySession['oauth_token_secret'])

    retweetID = request.form['retweetID']

    resp = requests.post('https://api.twitter.com/1.1/statuses/retweet.json', data={'id': retweetID}, auth=oauth)

    if resp.status_code == 200:
        flash('Se ha retuiteado el tuit!!', 'message')
    return redirect(url_for('index'))


@app.route('/follow', methods=['POST'])
def follow():
    global currentUser
    global mySession

    if currentUser is None:
        return redirect(url_for('login'))

    #userName = userName.encode('utf-8')

    oauth = OAuth1(consumer_key,
     client_secret=consumer_key_secret,
      resource_owner_key=mySession['oauth_token'],
       resource_owner_secret=mySession['oauth_token_secret'])

    userID = request.form['userID']
    userName = request.form['userName']

    if not userID and not userName:
        flash('Ambos estan vacios', 'error')
    elif userID and not userName:
        respID = requests.post('https://api.twitter.com/1.1/friendships/create.json', data={'user_id': userID}, auth=oauth)

        if respID.status_code is 200:
            flash('Acabas de seguir al ususario con id {}'.format(userID), 'message')
        elif respID.status_code is 404:
            flash('Error al seguir al usuario con ID {}'.format(userID), 'error')

    elif not userID and userName:
        respName = requests.post('https://api.twitter.com/1.1/friendships/create.json', data={'screen_name': userName}, auth=oauth)

        print(respName.status_code)

        if respName.status_code is 200:
            flash('Acabas de seguir al ususario {}'.format(userName), 'message')
        elif respName.status_code is 404:
            flash('Error al seguir al usuario {}'.format(userName), 'error')

    else:
        respID = requests.post('https://api.twitter.com/1.1/friendships/create.json', data={'user_id': userID}, auth=oauth)

        if respID.status_code is 200:
            flash('Acabas de seguir al ususario con id {}'.format(userID), 'message')
        elif respID.status_code is 404:
            flash('Error al seguir al usuario con ID {}'.format(userID), 'error')
            
    return redirect(url_for('index'))

    
@app.route('/tweet', methods=['POST'])
def tweet():
    global currentUser
    global mySession
    global method
    
    if currentUser is None:
        return redirect(url_for('login'))

    oauth = OAuth1(consumer_key,
     client_secret=consumer_key_secret,
      resource_owner_key=mySession['oauth_token'],
       resource_owner_secret=mySession['oauth_token_secret'])

    statusTweet = request.form['tweetText']
    resp = requests.post('https://api.twitter.com/1.1/statuses/update.json', data={'status': statusTweet}, auth=oauth)
   
    if resp.status_code == 200:
        flash('Tweet enviado!', 'message')
    else:
        flash('No se ha podido enviar el tweet', 'error')

    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5005)