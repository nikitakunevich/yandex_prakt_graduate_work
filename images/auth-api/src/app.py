from flask import Flask
from flask_jwt_extended import JWTManager

from config import config


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    JWTManager(app)
    from db import db
    db.init_app(app)
    import models
    with app.app_context():
        db.create_all()
        # default roles initialization
        if not models.Role.query.filter_by(role_name='admin').first():
            admin_role = models.Role(role_name='admin')
            db.session.add(admin_role)
        if not models.Role.query.filter_by(role_name='adult').first():
            adult_role = models.Role(role_name='adult')
            db.session.add(adult_role)
        if not models.Role.query.filter_by(role_name='child').first():
            child_role = models.Role(role_name='child')
            db.session.add(child_role)
        db.session.commit()
    from api.v1 import router as main_blueprint
    app.register_blueprint(main_blueprint, url_prefix='/api/v1')
    return app
