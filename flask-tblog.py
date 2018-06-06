from flask import Flask, url_for, render_template, request, redirect, flash, session, g
from flask_login import LoginManager, login_user, logout_user, current_user, login_required, UserMixin
from hashlib import sha256 as hash
from time import strftime
import tblog_db #SQL DATABASE FUNCTIONS
'''FOR PROFILE PICS UPLOAD
import os
from werkzeug.utils import secure_filename
'''

app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)

'''
PROFILE PICTURES

UPLOAD_FOLDER = '/user_data/profile_pictures/'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.',1)[1].lower() in ALLOWED_EXTENSIONS
'''


class User(UserMixin):
    def __init__(self, username, first, last, email, joined, password, posts=None):
        self.id = username
        self.first = first
        self.last = last
        self.email = email
        self.joined = joined
        self.password = password
        self.posts = posts

'''
LANDING PAGE
=====================================================================
ToDo:
    -Check if User is already logged in, if so forward to their page
=====================================================================
'''
@app.route('/', methods=['GET', 'POST'])
@app.route('/login/', methods=['GET', 'POST'])
def login():
    return render_template('login.html')

'''
REGISTRATION FUNCTION
=====================================================================
Notes:
    -Not an actual page, gets form data and submits to SQL db,
     then redirects
=====================================================================
'''
@app.route('/register/', methods=['GET','POST'])
def register():
    if current_user.is_authenticated:
        logout_user()

    added = False
    formError = False

    first = request.form["first"].lower().capitalize()
    last = request.form["last"].lower().capitalize()
    email = request.form["email"].lower()
    username = request.form["username"].lower()
    password = hash(request.form["password"]).hexdigest()
    joined = strftime("%Y %b %d")

    for i in [username,first,last,email,password]:
        if i == "":
            formError = True
            flash("PLEASE FILL OUT ALL FIELDS", "register")
            break

    # SQL - RETURNS BOOL
    if not formError:
        added = tblog_db.add_user(username,first,last,email,joined,password)

    '''
    0 = Form error
    1 = User succesfully added
    2 = Username already exists
    '''
    if added == 1:
        user = User(username, first, last, email, joined, password)

        if login_user(user):
            print 'USER LOGGED IN'
        else:
            print 'LOGIN FAILED'

        return redirect(url_for('user', uname=username))
    elif added == 2:
        flash('USERNAME ALREADY EXISTS', "register")
        return redirect(url_for('login'))
    else:
        return redirect(url_for('login'))

'''
AUTHENTICATION FUNCTION
=====================================================================
Notes:
    -Queries email address and checks for password match,
     no matches will return to login page
ToDo:
    -Display error messages when login fails
    -Add logout function
=====================================================================
'''
@app.route('/auth/', methods=['GET','POST'])
def auth():
    username = request.form['username'].lower()
    password = hash(request.form['password']).hexdigest()

    #SQL - RETURNS TUPLE OF USER'S LOG IN DATA
    try:
        user_data = tblog_db.auth_user(username, password)
        username = user_data[0]
        first = user_data[1]
        last = user_data[2]
        email = user_data[3]
        joined = user_data[4]
        posts = user_data[6]
        print 'USER DATA RETRIEVED'

    except:
        print 'COULD NOT GET USER DATA'

    if user_data:

        user = User(username, first, last, email, joined, password)
        '''
        session['logged_in'] = True
        session['id'] = username
        session['first'] = first
        session['last'] = last
        session['email'] = email
        '''

        #FLASK-LOGIN FUNCTION, ALLOWS current_user VAR TO BE USED IN HTML
        if login_user(user):
            print 'USER LOGGED IN'
        if current_user.is_authenticated:
            print 'AUTHENTICATED'
        else:
            print 'NOT AUTHENTICATED'

        if username == "admin":
            return redirect(url_for('admin'))
        else:
            return redirect(url_for('user', uname=username))
    else:
        flash("INVALID USERNAME OR PASSWORD", "login")
        return redirect(url_for('login'))

#PART OF FLASK-LOGIN, NO CLUE WHAT IT DOES
@login_manager.user_loader
def load_user(id):
    username, first, last, email, joined, password = tblog_db.load_user(id)
    #posts = getPosts()
    user = User(username, first, last, email, joined, password)
    return user

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

'''
USER FUNCTIONS
=====================================================================
ToDo:
    -Determine if the user is on their own page, if so display
     conrol panel/admin controls
    -If on another user's page, just so posts
    -Why doesn't login_required work?
=====================================================================
'''
@app.route('/user/<uname>', methods=['GET', 'POST'])
@login_required
def user(uname):
    getPosts()
    return render_template('usrhome.html', uname=uname)


@app.route('/get_posts', methods=['GET','POST'])
@login_required
def getPosts():
    posts = tblog_db.getPosts(current_user.id)
    print 'POSTS RETRIEVED:', posts
    current_user.posts = posts
    print 'CU POSTS:', current_user.posts


@app.route('/post', methods=['GET', 'POST'])
@login_required
def post():
    author = current_user.id
    topic = request.form["topic"]
    content = request.form["content"]
    timestamp = strftime("%b %d, %Y %H:%M:%S")

    print "POSTING:", author, topic, content, timestamp

    try:
        tblog_db.post(author, topic, content, timestamp)
        'RETURN REDIRECT GET_POSTS'
        getPosts()
        return redirect(url_for('user', uname=current_user.id))
    except StandardError as e:
        print (e)

'''
# UPLOAD PROFILE PICTURE
@app.route('/ulpp', methods=['GET', 'POST'])
def upload_pro_pic():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('uploaded_file',
                                    filename=filename))
'''

'''
SEARCH FUNCTIONALITY
=====================================================================
ToDo:
    -Write it
=====================================================================
'''
@app.route('/search')
def search():
    # SEARCH FUNCTION HERE
    return None

@app.route('/about')
def about():
    return render_template('about.html')

'''
ADMINISTRATOR FUNCTIONS
==========================================
'''
@app.route('/user/admin')
@app.route('/admin')
@login_required
def admin():
    if current_user.id != "admin":
        return redirect(url_for('user', uname=current_user.id))
    rows = tblog_db.query('users')
    return render_template('admin_panel.html', rows=rows)

@app.route('/delete_user', methods=['POST'])
def delete_user():
    user = request.form["username"]
    print 'USER TO DELETE:', user
    tblog_db.remove(user)
    return redirect(url_for('admin'))

if __name__ == '__main__':
    app.config["SECRET_KEY"] = "G04TLUV"
    app.run(debug=True)