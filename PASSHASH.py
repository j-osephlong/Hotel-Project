import os, hashlib, sqlite3

def hashpass(password):
    salt = hashlib.sha256(os.urandom(60)
        ).hexdigest().encode('ascii')
    saltedpass = salt+(bytes(password.encode('ascii')))
    hashedpass = hashlib.sha256(saltedpass).hexdigest()

    return (salt.decode('ascii'), hashedpass)

def checkpass(username, password):
    #needs error handling
    dbconn = sqlite3.connect("user.db")
    cursor = dbconn.cursor()
    cursor.execute("select * from users where username = {u}".format(u='\''+username+'\''))
    u = cursor.fetchall()
    try:
        salt = u[0][2]
        storedpass = u[0][1]
    except IndexError as E:
        return False
    print("in db:\ns: "+ salt + "\np: " + storedpass)
    saltedpass = salt.encode('ascii')+(password.encode('ascii'))
    hashedpass = hashlib.sha256(saltedpass).hexdigest()
    print("from input:\ns: "+ salt + "\np: " + hashedpass)

    return storedpass == hashedpass