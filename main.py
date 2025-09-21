import os
from flask import Flask, send_from_directory, request, jsonify
from flask_security import Security, SQLAlchemyUserDatastore
from flask_security.utils import verify_password, hash_password
from flask_login import login_user, login_required, logout_user
from flask_cors import CORS
from celery.schedules import crontab

from application.config import TestConfig, ProductionConfig
from application.database import db, migrate
from application.models import User, Role
from jobs.tasks import make_celery

from auth.admin import admin_bp
from auth.user import user_bp


def create_app(config_class=TestConfig):
    app = Flask(__name__, template_folder='templates', static_folder='static')
    CORS(app, supports_credentials=True, origins=["http://localhost:8080"])

    app.config.from_object(config_class)

    user_datastore = SQLAlchemyUserDatastore(db, User, Role)
    Security(app, user_datastore)

    db.init_app(app)
    migrate.init_app(app, db)

    with app.app_context():
        db.create_all()

        admin_role = Role.query.filter_by(name='admin').first()
        if not admin_role:
            admin_role = Role(name='admin', description='Administrator')
            db.session.add(admin_role)
            db.session.commit()

        user_role = Role.query.filter_by(name='user').first()
        if not user_role:
            user_role = Role(name='user', description='User')
            db.session.add(user_role)
            db.session.commit()

        if not User.query.filter_by(email='admin@quizzards.com').first():
            admin_user = User(
                email='admin@quizzards.com',
                password=hash_password('admin#123'),
                roles=[admin_role],
                fs_uniquifier='admin-uuid-123',
                active=True
            )
            db.session.add(admin_user)
            db.session.commit()

    @app.route("/", defaults={"path": ""})
    @app.route("/<path:path>")
    def serve_vue_app(path):
        if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
            return send_from_directory(app.static_folder, path)
        return send_from_directory(app.template_folder, "index.html")

    @app.route("/login", methods=["POST"])
    def login():
        data = request.get_json(force=True)
        user = db.session.query(User).filter_by(email=data["email"]).first()
        if user and verify_password(data["password"], user.password):
            is_admin = any(role.name == "admin" for role in user.roles)
            login_user(user)
            return jsonify({
                "message": "Login successful",
                "is_admin": is_admin,
                "user_id": user.id
            }), 200
        return jsonify({"error": "Invalid credentials"}), 401

    @app.route("/register", methods=["POST"])
    def register():
        data = request.get_json(force=True)
        email = data.get("email")
        password = data.get("password")
        if not email or not password:
            return jsonify({"error": "Missing email or password"}), 400
        if User.query.filter_by(email=email).first():
            return jsonify({"error": "Email already registered"}), 400

        user_role = Role.query.filter_by(name='user').first()
        user = User(email=email, password=hash_password(password), roles=[user_role], active=True)
        db.session.add(user)
        db.session.commit()
        return jsonify({"message": "User created successfully"}), 201

    @app.route("/logout", methods=["POST"])
    @login_required
    def logout():
        logout_user()
        return jsonify({"message": "Logout Successful"}), 200

    app.celery = make_celery(app)

    app.celery.conf.beat_schedule = {
        "daily-quiz-reminders": {
            "task": "send_daily_quiz_reminders",
            "schedule": crontab(hour=0, minute=0),
        },
        "monthly-performance-reports": {
            "task": "send_monthly_performance_reports",
            "schedule": crontab(day_of_month=1, hour=0, minute=0),
        },
    }

    app.register_blueprint(admin_bp)
    app.register_blueprint(user_bp)

    return app


app = create_app()
celery = app.celery

if __name__ == "__main__":
    app.run()
