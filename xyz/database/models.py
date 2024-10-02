from flask_security import UserMixin, RoleMixin, AsaList
from flask_security.models import fsqla_v3 as fsqla


def define_models(db):
    # Define models
    fsqla.FsModels.set_db_info(db)

    roles_users = db.Table('roles_users',
                           db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
                           db.Column('role_id', db.Integer(), db.ForeignKey('role.id')), extend_existing=True)

    class Role(db.Model, RoleMixin):
        id = db.Column(db.Integer(), primary_key=True)
        name = db.Column(db.String(80), unique=True)
        description = db.Column(db.String(255))

    class User(db.Model, UserMixin):
        id = db.Column(db.Integer, primary_key=True)
        email = db.Column(db.String(255), unique=True)
        # Make username unique but not required.
        username = db.Column(db.String(255), unique=True, nullable=True)
        password = db.Column(db.String(255))
        active = db.Column(db.Boolean())
        fs_uniquifier = db.Column(db.String(255), unique=True, nullable=False)
        confirmed_at = db.Column(db.DateTime())
        roles = db.relationship('Role', secondary=roles_users,
                                backref=db.backref('users', lazy='dynamic'))
        tf_phone_number = db.Column(db.String(128), nullable=True)
        tf_primary_method = db.Column(db.String(64), nullable=True)
        tf_totp_secret = db.Column(db.String(255), nullable=True)

    return User, Role, roles_users