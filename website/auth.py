from flask import Blueprint, render_template, request, flash, redirect, url_for
from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import login_user, login_required, logout_user, current_user
from .models import User
from . import db

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        phonenumber = request.form.get('phonenumber')
        password = request.form.get('password')

        user = User.query.filter_by(phonenumber=phonenumber).first()
        if user:
            if check_password_hash(user.password, password):
                login_user(user, remember=True)
                if user.is_admin:
                    return redirect(url_for('views.admin_dashboard'))
                else:
                    return redirect(url_for('views.user_dashboard'))
            else:
                flash('Incorrect password, try again.', category='error')
        else:
            flash('Phone number not found.', category='error')

    return render_template("login.html", user=current_user)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@auth.route('/update-password', methods=['GET', 'POST'])
@login_required
def update_password():
    if request.method == 'POST':
        old_password = request.form.get('old_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')

        if not check_password_hash(current_user.password, old_password):
            flash('Old password is incorrect.', category='error')
        elif new_password != confirm_password:
            flash('New passwords do not match.', category='error')
        else:
            current_user.password = generate_password_hash(new_password, method='pbkdf2:sha256')  # שינוי לאלגוריתם בטוח יותר
            db.session.commit()
            flash('Password updated successfully!', category='success')
            return redirect(url_for('views.home'))

    return render_template("update_password.html", user=current_user)
