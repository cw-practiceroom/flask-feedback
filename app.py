from flask import Flask, render_template, redirect, session
from models import db, connect_db, User, Feedback
from forms import RegisterForm, LoginForm, FeedbackForm, DeleteForm
from werkzeug.exceptions import Unauthorized

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///feedback_users'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['SECRET_KEY'] = 'col3'

connect_db(app)


@app.route('/')
def redirect_register():

    return redirect('/register')


@app.route('/register', methods=['GET', 'POST'])
def register():

    form = RegisterForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        email = form.email.data
        first_name = form.first_name.data
        last_name = form.last_name.data

        newUser = User.register(username, password, email, first_name, last_name)
        db.session.add(newUser)
        db.session.commit()

        session['username'] = newUser.username

        return redirect(f'/users/{newUser.username}')

    else:
        return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():

    form = LoginForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        user = User.authenticate(username, password)

        if user:
            session['username'] = user.username
            return redirect(f'/users/{user.username}')

        else:
            form.username.errors = ['Incorrect username/password']
    
    return render_template('login.html', form=form)


@app.route('/users/<username>')
def secret_page(username):

    if 'username' not in session or username != session['username']:
        raise Unauthorized()
    
    user = User.query.filter_by(username=username).first()

    return render_template('secret.html', user=user)


@app.route('/logout')
def logout():

    session.pop('username')
    return redirect('/')


@app.route('/users/<username>/delete', methods=['POST'])
def delete_user(username):

    if 'username' not in session or username != session['username']:
        raise Unauthorized()

    user = User.query.filter_by(username=username).first()
    db.session.delete(user)
    db.session.commit()
    session.pop('username')

    return redirect('/')


@app.route('/users/<username>/feedback/add', methods=['GET', 'POST'])
def add_feedback(username):
    
    if 'username' not in session or username != session['username']:
        raise Unauthorized()

    form = FeedbackForm()

    if form.validate_on_submit():
        title = form.title.data
        content = form.content.data

        feedback = Feedback(title=title, content=content, username=username)

        db.session.add(feedback)
        db.session.commit()

        return redirect(f'/users/{username}')

    else:
        return render_template('new-feedback.html', form=form)


@app.route('/feedback/<int:id>/update', methods=['GET', 'POST'])
def edit_feedback(id):

    feedback = Feedback.query.get(id)

    if "username" not in session or feedback.username != session['username']:
        raise Unauthorized()

    form = FeedbackForm(obj=feedback)

    if form.validate_on_submit():
        feedback.title = form.title.data
        feedback.content = form.content.data

        db.session.commit()

        return redirect(f'/users/{feedback.username}')

    return render_template('edit-feedback.html', form=form)


@app.route('/feedback/<int:id>/delete', methods=['POST'])
def delete_feedback(id):

    feedback = Feedback.query.get(id)
    if "username" not in session or feedback.username != session['username']:
        raise Unauthorized()

    form = DeleteForm()

    if form.validate_on_submit():
        db.session.delete(feedback)
        db.session.commit()

    return redirect(f'/users/{feedback.username}')
