import sqlite3 as sql

def add_user(username,first,last,email,joined,password):
    try:
        with sql.connect('db/tblog.db') as conn:
            print 'CONNECTED TO DB'
            cur = conn.cursor()
            print 'QUERYING USERNAME:', username
            cur.execute('SELECT * FROM users WHERE username="%s";' % username)
            rows = cur.fetchall()
            print 'VERIFYING USERNAME AVAILABLE'
            if not rows:
                # USERNAME DOES NOT ALREADY EXIST
                cur.execute('INSERT INTO users (username,first,last,email,joined,password) VALUES (?,?,?,?,?,?)',
                            (username,first,last,email,joined,password))
                conn.commit()
                print 'USER ADDED'
                return 1
            else:
                print 'USERNAME ALREADY EXISTS'
                return 2

    except:
        print 'USER NOT ADDED'
        return 0

def auth_user(username, password):
    try:
        with sql.connect('db/tblog.db') as conn:
            print 'CONNECTED TO DB'
            conn.row_factory = sql.Row
            cur = conn.cursor()
            cur.execute('SELECT * FROM users WHERE username="%s";' % username)
            rows = cur.fetchall()
            if rows[0][5] == password:
                print 'LOGIN OK'
                return rows[0]
            else:
                print 'PASSWORD MISMATCH'
                return None

    except:
        print 'USER FETCH FAILED'
        return None

def load_user(username):
    try:
        with sql.connect('db/tblog.db') as conn:
            print 'CONNECTED TO DB'
            conn.row_factory = sql.Row
            cur = conn.cursor()
            print 'CUR OK'
            print 'SEARCHING %s' % username
            cur.execute('SELECT * FROM users WHERE username="%s";' % username)
            row = cur.fetchall()
            print 'ROW RETURNED  in load_user:', row
            row = row[0]
            username = row[0]
            first = row[1]
            last = row[2]
            email = row[3]
            joined = row[4]
            password = row[5]

            print 'MATCH FOUND'
            print username, first, last, email, joined, password
            return username, first, last, email, joined, password
    except:
        print 'USER FETCH FAILED'
        return None

def query( field=None, selector=None ):
    if field:
        field = (field,)
    if selector:
        selector = (selector,)

    try:
        with sql.connect('db/tblog.db') as conn:
            print 'CONNECTED TO DB'
            conn.row_factory = sql.Row
            cur = conn.cursor()
            print 'SEARCHING'

            if field and selector:
                print 'SELECT * FROM users WHERE ? = ?'
                cur.execute('SELECT * FROM users WHERE ? = ?', (field, selector) )
            else:
                print 'SELECT rowid, username, first, last, email FROM users'
                cur.execute('SELECT rowid, username, first, last, email, joined FROM users')

            rows = cur.fetchall()
            print 'ROWS FETCHED:', rows
            return rows
    except:
        print 'QUERY FAILED'
        return None

def remove(user):
    user = (user,)
    with sql.connect('db/tblog.db') as conn:
        print 'CONNECTED TO DB'
        cur = conn.cursor()
        cur.execute('DELETE FROM users WHERE username = ?', user)
        print 'DELETING', user[0]
        conn.commit()
    return None



def post(author, topic, content, timestamp):
    '''
    author = (author,)
    topic = (topic,)
    content = (content,)
    timestamp = (timestamp,)
    '''
    print 'CONVERSIONS:', author, topic, content, timestamp
    with sql.connect('db/tblog.db') as conn:
        print 'CONNECTED TO DB'
        cur = conn.cursor()
        print 'CUR OK'
        try:
            cur.execute('INSERT INTO posts (author,topic,content,timestamp) VALUES (?,?,?,?)',
                        (author,topic,content,timestamp))
            print 'POST ADDED'
            conn.commit()
        except StandardError as e:
            print (e)



def getPosts(author):
    author = (author,)
    with sql.connect('db/tblog.db') as conn:
        print 'CONNECTED TO DB'
        cur = conn.cursor()
        try:
            print 'SELECT rowid, topic, content, timestamp FROM posts WHERE author=', author
            cur.execute('SELECT rowid, topic, content, timestamp FROM posts WHERE author=? ORDER BY rowid DESC', author)
            posts = cur.fetchall()
            print 'POSTS RETRIEVED:', posts

            return posts
        except StandardError as e:
            print (e)
