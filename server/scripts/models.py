from server.app import db


class User(db.Model):
    __tablename__ = 'user'

    email = db.Column(db.String, primary_key=True)
    username = db.Column(db.String)
    password = db.Column(db.String)
    authenticated = db.Column(db.Boolean, default=False)

    def get_id(self):
        """Return the email address to satisfy Flask-Login's requirements."""
        return self.email

    def is_authenticated(self):
        """Return True if the user is authenticated."""
        return self.authenticated
