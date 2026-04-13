from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from datetime import timedelta
import os

db = SQLAlchemy()
jwt = JWTManager()
bcrypt = Bcrypt()


def create_app():
    app = Flask(__name__)

    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'super-secret-key-2024')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///taskapi.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'jwt-secret-2024')
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)
    app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=30)

    db.init_app(app)
    jwt.init_app(app)
    bcrypt.init_app(app)
    CORS(app)

    from routes.auth import auth_bp
    from routes.tasks import tasks_bp
    from routes.users import users_bp
    from routes.pages import pages_bp

    app.register_blueprint(pages_bp)
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(tasks_bp, url_prefix='/api/tasks')
    app.register_blueprint(users_bp, url_prefix='/api/users')

    with app.app_context():
        db.create_all()
        seed_demo()

    return app


def seed_demo():
    from models import User, Task
    if User.query.count() == 0:
        hashed = bcrypt.generate_password_hash('demo123').decode('utf-8')
        u = User(username='demo', email='demo@taskapi.com', password=hashed, full_name='Demo User')
        db.session.add(u)
        db.session.flush()
        tasks = [
            Task(title='Setup Flask project', description='Initialize project structure', priority='high', status='done', user_id=u.id, category='Development'),
            Task(title='Design database schema', description='Plan models and relationships', priority='high', status='done', user_id=u.id, category='Development'),
            Task(title='Implement JWT auth', description='Add login/register endpoints', priority='medium', status='in_progress', user_id=u.id, category='Development'),
            Task(title='Write API docs', description='Document all endpoints', priority='low', status='todo', user_id=u.id, category='Documentation'),
            Task(title='Deploy to Render', description='Deploy the API to production', priority='medium', status='todo', user_id=u.id, category='DevOps'),
        ]
        for t in tasks:
            db.session.add(t)
        db.session.commit()
