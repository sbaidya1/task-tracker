from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from datetime import datetime
import os

# initialize flask app and configuration
app = Flask(__name__)
app.secret_key = 'dev-secret-key' #safe default 
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tasktracker.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# initialize extensions
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login' # redirect if user not logged in

# user model for auth
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

# task model (linked to user)
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    done = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

# for flask-login to load user from db
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# homepage
@app.route('/')
@login_required
def index():
    return render_template('index.html')

# register new users
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = bcrypt.generate_password_hash(request.form['password']).decode('utf-8')
        user = User(username=username, password=password)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html')

# login existing users
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('index'))
    return render_template('login.html')

# logout current user
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# get all tasks for current user
@app.route('/api/tasks', methods=['GET'])
@login_required
def get_tasks():
    tasks = Task.query.filter_by(user_id=current_user.id).all()
    return jsonify([{'id': t.id, 'title': t.title, 'done': t.done} for t in tasks])

# add a new task
@app.route('/api/tasks', methods=['POST'])
@login_required
def add_task():
    data = request.get_json()
    task = Task(title=data['title'], user_id=current_user.id)
    db.session.add(task)
    db.session.commit()
    return jsonify({'message': 'Task added successfully'})

# update an existing task (toggle done/undone)
@app.route('/api/tasks/<int:task_id>', methods=['PUT'])
@login_required
def update_task(task_id):
    data = request.get_json()
    task = Task.query.filter_by(id=task_id, user_id=current_user.id).first_or_404()
    task.done = data.get('done', task.done)
    db.session.commit()
    return jsonify({'message': 'Task updated'})

# delete a task
@app.route('/api/tasks/<int:task_id>', methods=['DELETE'])
@login_required
def delete_task(task_id):
    task = Task.query.filter_by(id=task_id, user_id=current_user.id).first_or_404()
    db.session.delete(task)
    db.session.commit()
    return jsonify({'message': 'Task deleted'})

# create folder + set up db
if __name__ == '__main__':
    os.makedirs('instance', exist_ok=True)
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static', exist_ok=True)
    with app.app_context():
        db.create_all()
    app.run(debug=True)