import os
from functools import wraps
from flask import Flask, render_template, redirect, url_for, flash, request
from flask_bootstrap import Bootstrap
from flask_ckeditor import CKEditor
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.declarative import declarative_base
from forms import CreatePostForm


Base = declarative_base()

app = Flask(__name__)
# app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
ckeditor = CKEditor(app)
Bootstrap(app)

login_manager = LoginManager()

login_manager.init_app(app)

# CONNECT TO DB
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# CONFIGURE TABLES
class User(db.Model, UserMixin, Base):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(250), unique=True)
    password = db.Column(db.String(250))


class BlogPost(db.Model, Base):
    __tablename__ = "blog_posts"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), nullable=False)
    body = db.Column(db.Text(), nullable=False)
    img_url = db.Column(db.String(250), nullable=False)


def admin(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if current_user.is_authenticated:
            is_admin = current_user.id == 1
            if not is_admin:
                flash("You are not authorized to access this page")
                return redirect(url_for('login'))
            return func(*args, **kwargs)
        flash("You are not authorized to access this page")
        return redirect(url_for('login'))

    return decorated_function


def logged_in(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if current_user.is_authenticated:
            return redirect(url_for('index.html'))
        return func(*args, **kwargs)

    return decorated_function


@app.route('/', methods=['GET', 'POST'])
def home():
    posts = BlogPost.query.all()
    form = CreatePostForm()
    if request.method == 'POST':
        form = CreatePostForm(request.form)
        if form.validate():
            title = form.title.data
            body = form.body.data
            img_url = form.img_url.data
            new_post = BlogPost(title=title, body=body, img_url=img_url)
            db.session.add(new_post)
            db.session.commit()
            return redirect(url_for('home'))
    return render_template("index.html", all_posts=posts, form=form)


@app.route('/login', methods=['GET', 'POST'])
@logged_in
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        print(username)
        print(password)
        if username == os.environ.get('username') and password == os.environ.get('password'):
            user = User.query.filter_by(username=username).first()
            login_user(user)
            return redirect(url_for('home'))
        else:
            flash('Error: Invalid username or password.')
            print('Error: Invalid username or password.')
            return render_template('login.html')

    return render_template("login.html")


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route("/delete/<int:post_id>")
@admin
def delete_post(post_id):
    post_to_delete = BlogPost.query.get(post_id)
    db.session.delete(post_to_delete)
    db.session.commit()
    return redirect(url_for('home'))


if __name__ == "__main__":
    app.run(host='127.0.0.1', port=5000, debug=True)
