from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    phonenumber = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(150))
    is_admin = db.Column(db.Boolean, default=False)
    transactions = db.relationship('Transaction', backref='user', lazy=True)

class Client(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150))
    phone = db.Column(db.String(150), unique=True)
    transactions = db.relationship('Transaction', backref='client', lazy=True)

    def get_total_points(self):
        total_points = sum(transaction.points_earned for transaction in self.transactions)
        total_points -= sum(transaction.points_used for transaction in self.transactions)
        return total_points


class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    original_amount = db.Column(db.Float)  # סכום העסקה המקורי
    points_used = db.Column(db.Float, default=0)  # סכום הנקודות שהשתמש
    amount = db.Column(db.Float)  # סכום העסקה לאחר השימוש בנקודות
    points_earned = db.Column(db.Float)  # סכום הנקודות שצבר בעסקה זו
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'))
    employee_name = db.Column(db.String(150))  # שם העובד שבצע העסקה


