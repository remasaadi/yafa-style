from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user, logout_user
from .models import Transaction, User, Client
from . import db
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.sql import func

views = Blueprint('views', __name__)

def validate_phone_number(phone):
    if not phone or len(phone) != 10 or not phone.isdigit():
        return False
    return True

@views.route('/')
@login_required
def home():
    if current_user.is_admin:
        return redirect(url_for('views.admin_dashboard'))
    else:
        return redirect(url_for('views.user_dashboard'))

@views.route('/admin-dashboard')
@login_required
def admin_dashboard():
    if not current_user.is_admin:
        return redirect(url_for('views.user_dashboard'))
    return render_template("admin_dashboard.html", user=current_user)

@views.route('/user-dashboard')
@login_required
def user_dashboard():
    if current_user.is_admin:
        return redirect(url_for('views.admin_dashboard'))
    return render_template("user_dashboard.html", user=current_user)

@views.route('/add-client', methods=['GET', 'POST'])
@login_required
def add_client():
    if request.method == 'POST':
        client_name = request.form.get('clientName')
        client_phone = request.form.get('clientPhone')

        if not client_name or not validate_phone_number(client_phone):
            flash('All fields are required and phone number must be 10 digits!', category='error')
        else:
            existing_client = Client.query.filter_by(phone=client_phone).first()
            if existing_client:
                flash('Client with this phone number already exists!', category='error')
            else:
                new_client = Client(name=client_name, phone=client_phone)
                db.session.add(new_client)
                db.session.commit()
                flash('Client added successfully!', category='success')
                return redirect(url_for('views.add_client'))

    return render_template("add_client.html", user=current_user)

@views.route('/add-transaction', methods=['GET', 'POST'])
@login_required
def add_transaction():
    client = None
    total_points = 0
    new_transaction = None
    original_amount = 0
    final_amount = 0
    points_earned = 0
    total_points_after = 0

    if request.method == 'POST':
        client_phone = request.form.get('clientPhone')
        amount = request.form.get('amount')
        points_to_use = request.form.get('pointsToUse')

        if not validate_phone_number(client_phone) or not amount:
            flash('All fields are required and phone number must be 10 digits!', category='error')
            return redirect(url_for('views.add_transaction'))

        client = Client.query.filter_by(phone=client_phone).first()
        if not client:
            flash('Client does not exist!', category='error')
            return redirect(url_for('views.add_transaction'))

        if 'check_points' in request.form:
            total_points = client.get_total_points()
            flash(f'Total points for {client.name}: {total_points}', category='info')
            return render_template("add_transaction.html", user=current_user, client=client, total_points=total_points)

        if 'cancel_transaction' in request.form:
            flash('Transaction canceled!', category='info')
            return redirect(url_for('views.add_transaction'))

        try:
            original_amount = float(amount)
            points_to_use = float(points_to_use) if points_to_use else 0
        except ValueError:
            flash('Amount and points to use must be numbers!', category='error')
            return redirect(url_for('views.add_transaction'))

        if original_amount <= 0:
            flash('Transaction amount must be greater than zero.', category='error')
            return redirect(url_for('views.add_transaction'))

        if points_to_use < 0:
            flash('Points to use cannot be negative.', category='error')
            return redirect(url_for('views.add_transaction'))

        if points_to_use > original_amount:
            flash('Points to use cannot be greater than the transaction amount.', category='error')
            return redirect(url_for('views.add_transaction'))

        if points_to_use > client.get_total_points():
            flash(f'Not enough points! You can use up to {client.get_total_points():.2f} points.', category='error')
            return redirect(url_for('views.add_transaction'))

        final_amount = original_amount - points_to_use
        points_earned = original_amount * 0.10  # Calculating from original amount

        new_transaction = Transaction(
            original_amount=original_amount,
            points_used=points_to_use,
            amount=final_amount,
            points_earned=points_earned,
            user_id=current_user.id,
            client_id=client.id,
            employee_name=current_user.first_name  # שמירת שם העובד
        )
        db.session.add(new_transaction)
        db.session.commit()

        total_points_after = client.get_total_points() +  points_earned - points_to_use

        flash(f'Transaction added! Client earned {points_earned:.2f} points.', category='success')
        flash(f'Client Name: {client.name}', category='info')
        flash(f'Client Phone: {client.phone}', category='info')
        flash(f'Original Amount: {original_amount}', category='info')
        flash(f'Amount After Points: {final_amount}', category='info')
        flash(f'Points Earned This Transaction: {points_earned:.2f}', category='info')
        flash(f'Total Points After Transaction: {total_points_after:.2f}', category='info')
        flash(f'Employee Name: {current_user.first_name}', category='info')
        flash(f'Transaction Date: {new_transaction.date}', category='info')

    return render_template("add_transaction.html", user=current_user, client=client, total_points=total_points, new_transaction=new_transaction, original_amount=original_amount, final_amount=final_amount, points_earned=points_earned, total_points_after=total_points_after)


@views.route('/delete-transaction/<int:transaction_id>', methods=['POST'])
@login_required
def delete_transaction(transaction_id):
    if not current_user.is_admin:
        flash('You do not have permission to delete transactions.', category='error')
        return redirect(url_for('views.home'))

    transaction = Transaction.query.get(transaction_id)
    if transaction:
        db.session.delete(transaction)
        db.session.commit()
        flash('Transaction deleted successfully!', category='success')
    else:
        flash('Transaction not found!', category='error')
    return redirect(url_for('views.transactions_report'))

@views.route('/use-points', methods=['GET', 'POST'])
@login_required
def use_points():
    if request.method == 'POST':
        client_phone = request.form.get('clientPhone')
        points_to_use = request.form.get('points')

        if not validate_phone_number(client_phone) or not points_to_use:
            flash('All fields are required and phone number must be 10 digits!', category='error')
            return redirect(url_for('views.use_points'))

        client = Client.query.filter_by(phone=client_phone).first()
        if not client:
            flash('Client does not exist!', category='error')
            return redirect(url_for('views.use_points'))

        try:
            points_to_use = float(points_to_use)
        except ValueError:
            flash('Points to use must be a number!', category='error')
            return redirect(url_for('views.use_points'))

        total_points = client.get_total_points()

        if points_to_use > total_points:
            flash(f'Not enough points! You can use up to {total_points:.2f} points.', category='error')
        else:
            new_transaction = Transaction(
                amount=-points_to_use,
                points_earned=-points_to_use,
                user_id=current_user.id,
                client_id=client.id,
                employee_name=current_user.first_name  # שמירת שם העובד
            )
            db.session.add(new_transaction)
            db.session.commit()
            flash('Points used successfully!', category='success')
            return redirect(url_for('views.use_points'))

    return render_template("use_points.html", user=current_user)

@views.route('/check-points', methods=['GET', 'POST'])
@login_required
def check_points():
    client = None
    total_points = None
    if request.method == 'POST':
        client_phone = request.form.get('clientPhone')

        if not validate_phone_number(client_phone):
            flash('Client phone number is required and must be 10 digits!', category='error')
            return redirect(url_for('views.check_points'))

        client = Client.query.filter_by(phone=client_phone).first()
        if not client:
            flash('Client does not exist!', category='error')
        else:
            total_points = client.get_total_points()
            flash(f'Total points for {client.name}: {total_points}', category='info')

    return render_template("check_points.html", user=current_user, client=client, total_points=total_points)

@views.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

# ניהול עובדים
@views.route('/manage-employees', methods=['GET', 'POST'])
@login_required
def manage_employees():
    if not current_user.is_admin:
        flash('You do not have access to this page.', category='error')
        return redirect(url_for('views.home'))

    if request.method == 'POST':
        action = request.form.get('action')
        user_id = request.form.get('user_id')
        first_name = request.form.get('first_name')
        phonenumber = request.form.get('phonenumber')
        password = request.form.get('password')

        if action == 'add':
            if not first_name or not phonenumber or not password:
                flash('All fields are required!', category='error')
            else:
                existing_user = User.query.filter_by(phonenumber=phonenumber).first()
                if existing_user:
                    flash('User with this phone number already exists!', category='error')
                else:
                    new_user = User(
                        first_name=first_name,
                        phonenumber=phonenumber,
                        password=generate_password_hash(password, method='pbkdf2:sha256'),  # שינוי לאלגוריתם בטוח יותר
                        is_admin=False
                    )
                    db.session.add(new_user)
                    db.session.commit()
                    flash('Employee added successfully!', category='success')
        elif action == 'update':
            user = User.query.get(user_id)
            if user:
                user.first_name = first_name
                user.phonenumber = phonenumber
                if password:
                    user.password = generate_password_hash(password, method='pbkdf2:sha256')  # שינוי לאלגוריתם בטוח יותר
                db.session.commit()
                flash('Employee updated successfully!', category='success')
            else:
                flash('Employee not found!', category='error')
        elif action == 'delete':
            user = User.query.get(user_id)
            if user:
                db.session.delete(user)
                db.session.commit()
                flash('Employee deleted successfully!', category='success')
            else:
                flash('Employee not found!', category='error')

    users = User.query.all()
    return render_template("manage_employees.html", user=current_user, users=users)

# דוח עסקאות
@views.route('/transactions-report', methods=['GET', 'POST'])
@login_required
def transactions_report():
    if not current_user.is_admin:
        flash('You do not have access to this page.', category='error')
        return redirect(url_for('views.home'))

    transactions = []
    if request.method == 'POST':
        date = request.form.get('date')
        if date:
            transactions = Transaction.query.filter(func.date(Transaction.date) == date).all()
            if not transactions:
                flash('No transactions found for this date.', category='info')

    return render_template("transactions_report.html", user=current_user, transactions=transactions)


@views.route('/clients-report', methods=['GET', 'POST'])
@login_required
def clients_report():
    if not current_user.is_admin:
        flash('You do not have access to this page.', category='error')
        return redirect(url_for('views.home'))

    clients = Client.query.all()

    if request.method == 'POST':
        client_id = request.form.get('client_id')
        new_name = request.form.get('new_name')
        new_phone = request.form.get('new_phone')

        if not client_id or not new_name or not new_phone:
            flash('All fields are required to update client information!', category='error')
        else:
            client = Client.query.get(client_id)
            if client:
                client.name = new_name
                client.phone = new_phone
                db.session.commit()
                flash('Client information updated successfully!', category='success')
            else:
                flash('Client not found!', category='error')

    return render_template("clients_report.html", user=current_user, clients=clients)
