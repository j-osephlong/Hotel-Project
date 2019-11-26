import sqlite3
import jwt
import os
import json
import codecs
import flask
from datetime import datetime  
import DBINTERFACE as DB
from PASSHASH import hashpass, checkpass

accountmanager = flask.Blueprint('accountmanager', __name__, template_folder='templates')

@accountmanager.route('/regrequest', methods = ['POST'])
def register ():
    # need to sanatize input
    DB.initdb()

    resp = json.loads(flask.request.data)
    username = resp['username']
    salt, hashedpass = hashpass(resp['password'])
    print("\tfrom client: \n\tregister request:\n\tu: " + username + ", p: "+resp['password'])

    #is username already registered
    if (userexists(username)):
        return {'message':'Username already taken', 'code':'failed'}
    #is username already requested
    if (len(DB.query("accountrequests", args="WHERE username = \'{u}\'".format(u = username)))== 1):
        return {'message':'Username already taken', 'code':'failed'}
    
    #submit account for approval
    try:
        DB.insert("accountrequests", ("\'"+username+"\'", "\'"+hashedpass+"\'", "\'"+salt+"\'", "(SELECT datetime())"))
        return {'message':'registered '+username+', pending admin approval. Try logging on later.', 'code':'success'}
    except sqlite3.IntegrityError as E:
        return {'message':'error, '+E.__str__(), 'code':'failed'}

@accountmanager.route('/loginrequest', methods = ['POST'])
def login ():
    DB.initdb()

    resp = json.loads(flask.request.data)
    print("\tfrom client: \nlogin request:\n\tu: " + str(resp['username'] + ", p: "+resp['password']))

    #check if user exists
    if (not userexists(resp['username'])):
        #check if user awaiting approval
        if (len(DB.query("accountrequests", args="WHERE username = \'{u}\'".format(u = resp['username'])))== 1):
            return {'code': 'failed', 'reason':'Account pending admin aporoval. Please try again later.', 'token': ''}
        #user does not exist, deny    
        return {'code': 'failed', 'reason':'Incorrect username or password. Please try again.', 'token': ''}

    #verify password
    if checkpass(resp['username'], resp['password']):
        #check account for ban
        if (DB.query("users", "banned", "WHERE username = \'{u}\'".format(u = resp['username']))[0][0] == 'true'):
            print("Banned user " + resp['username'] + " tried to log on.")
            return {'code': 'failed', 'reason':'Banned from server.', 'token': ''}

        #log user in, give user token
        return {'code': 'success', 'reason':'You are now logged in', 'token': createtoken(resp['username']).__str__()}
    else:
        #incorrect password
        return {'code': 'failed', 'reason':'Incorrect username or password. Please try again.', 'token': ''}

@accountmanager.route('/logout', methods = ['POST'])
def logout():
    token = json.loads(flask.request.data)['token']
    payload = jwt.decode(codecs.decode(token, "hex"), 'secret', algorithms=('HS256'))

    #remove user login tokens
    DB.delete('logintokens', 'logintokens.username = \'{u}\' AND logintokens.spice = \'{s}\''.format(u = payload['username'], s = payload['spice']))
    return {'code':'success'}

def createtoken(username):
    spice = os.urandom(10).hex()
    token = jwt.encode({'username':username, 'spice':spice}, 'secret', algorithm='HS256')

    #limit of 5 tokens
    preExisting = DB.query('logintokens', args='WHERE username = \'{u}\''.format(u = username))
    if len(preExisting) >= 5:
        oldest = datetime.strptime(preExisting[0][2], '%Y-%m-%d %H:%M:%S.%f')
        for row in preExisting:
            if datetime.strptime(row[2], '%Y-%m-%d %H:%M:%S.%f') < oldest:
                oldest = datetime.strptime(row[2], '%Y-%m-%d %H:%M:%S.%f')

        DB.delete('logintokens', 'username = \'{u}\' AND time = \'{t}\''.format(u = username, t = str(oldest)))

    #store the payload in db
    DB.insert("logintokens", ("\'"+username+"\'", "\'"+spice+"\'", "\'"+str(datetime.now())+"\'"))
    return token.hex()

def userexists(username):
    if (len(DB.query('users', args="WHERE username = \'{u}\'".format(u = username))) == 1):
        return True
    return False

@accountmanager.route('/getusername', methods=['POST'])
def serveusername():
    payload = jwt.decode(codecs.decode(json.loads(flask.request.data)['token'], "hex"), 'secret', algorithms=('HS256'))
    return {'username': payload['username']}

@accountmanager.route('/changepassword', methods=['POST'])
def changePassword():
    data = json.loads(flask.request.data)
    account = checktoken(data['token'])
    #does account exist
    if account[0] == False:
        return {'code': 'failed', 'message': 'Not logged in.'}

    if not checkpass(account[2], data['oldpass']):
        return {'code': 'failed', 'message': 'Incorrect password.'}
    
    newhash = hashpass(data['newpass'])

    DB.update('users', 'SET hashpass = \'{h}\', salt = \'{s}\' WHERE username = \'{u}\''.format(u  = account[2], s = newhash[0], h = newhash[1]))
    DB.delete('logintokens', 'username = \'{u}\''.format(u = account[2]))
    return {'code': 'success', 'message': 'Password changed.'}


def checktoken(token):
    #returns if user exists, privilege, and username

    try:
        payload = jwt.decode(codecs.decode(token, "hex"), 'secret', algorithms=('HS256'))
    except Exception as E:
        #couldn't decode, fake token
        return (False, None, None)

    #check if payload is valid
    if not userexists(payload['username']):
        return (False, None, None)

    #match payload to existing token    
    rows = DB.query('logintokens', args=" WHERE logintokens.username = \'{u}\' AND logintokens.spice = \'{s}\'".format(u = payload['username'], s = payload['spice'])) 
    if len(rows) == 1:
        return (True, DB.query('users', columns='privilege', args="WHERE username = \'{u}\'".format(u = payload['username']))[0][0], payload['username'])

    return (False, None, None)

@accountmanager.route('/authcheck', methods=['POST'])
def authcheck():
    data = json.loads(flask.request.data)
    account = checktoken(data['token'])
    return {'accountExists': account[0],
            'privilege' : account[1],
            'username' : account[2]}