"""
MedAsset Sentinel - Authentication Routes
Handles login, logout and session management
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from services import AuthService

# Create blueprint
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    Display login form and handle authentication
    GET: Show login page
    POST: Process login credentials
    """
    # If already logged in, redirect to dashboard
    if session.get('user_id'):
        return redirect(url_for('dashboard.index'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        # Authenticate user
        admin = AuthService.authenticate(username, password)

        if admin:
            # Set session
            session['user_id'] = admin.id
            session['username'] = admin.username
            session.permanent = True  # Use configured session lifetime

            flash('Login successful', 'success')
            return redirect(url_for('dashboard.index'))
        else:
            flash('Invalid username or password', 'error')

    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    """
    Log out current user and clear session
    """
    session.clear()
    flash('You have been logged out', 'info')
    return redirect(url_for('auth.login'))

