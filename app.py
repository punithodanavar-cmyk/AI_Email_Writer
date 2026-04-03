from flask import Flask, render_template, request, session, redirect, url_for, jsonify
from config import Config
from database import Database
from groq_handler import GroqEmailGenerator
from auth import login_required, get_current_user
import os
import json

app = Flask(__name__)
app.config.from_object(Config)

# Initialize objects
# db = Database()
# email_generator = GroqEmailGenerator()

# =========================
# HOME ROUTE
# =========================
@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

# =========================
# REGISTER ROUTE
# =========================
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        # Validation
        if not username or not email or not password:
            return render_template('register.html', error='All fields are required')

        if password != confirm_password:
            return render_template('register.html', error='Passwords do not match')

        if len(password) < 6:
            return render_template('register.html', error='Password must be at least 6 characters')

        # Register user
        if db.register_user(username, email, password):
            return redirect(url_for('login'))
        else:
            return render_template('register.html', error='Username or email already exists')

    return render_template('register.html')

# =========================
# LOGIN ROUTE
# =========================
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user_id = db.login_user(username, password)
        if user_id:
            session['user_id'] = user_id
            session['username'] = username
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error='Invalid username or password')

    return render_template('login.html')

# =========================
# LOGOUT ROUTE
# =========================
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

# =========================
# DASHBOARD ROUTE
# =========================
@app.route('/dashboard')
@login_required
def dashboard():
    user_id = get_current_user()
    user = db.get_user_by_id(user_id)
    return render_template('dashboard.html', user=user)

# =========================
# GENERATE EMAIL API
# =========================
@app.route('/api/generate-email', methods=['POST'])
@login_required
def generate_email():
    user_id = get_current_user()

    try:
        data = request.json

        recipient = data.get('recipient')
        email_type = data.get('email_type')
        tone = data.get('tone')
        context = data.get('context')

        # Validate input
        if not all([recipient, email_type, tone, context]):
            return jsonify({'error': 'Missing required fields'}), 400

        # Generate email using Groq API
        result = email_generator.generate_email(
            recipient=recipient,
            email_type=email_type,
            tone=tone,
            context=context
        )

        if not result['success']:
            return jsonify({'error': result.get('error', 'Failed to generate email')}), 500

        # Save to database
        email_id = db.save_email(
            user_id=user_id,
            subject=result['subject'],
            body=result['body'],
            recipient=recipient,
            email_type=email_type,
            tone=tone
        )

        # Log API usage
        db.log_api_usage(
            user_id=user_id,
            tokens_used=result.get('tokens_used', 0),
            response_time=result.get('response_time', 0)
        )

        return jsonify({
            'success': True,
            'email_id': email_id,
            'subject': result['subject'],
            'body': result['body']
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# =========================
# EMAIL HISTORY
# =========================
@app.route('/history')
@login_required
def email_history():
    user_id = get_current_user()
    user = db.get_user_by_id(user_id)
    emails = db.get_email_history(user_id)
    return render_template('email_history.html', user=user, emails=emails)

# =========================
# DELETE EMAIL
# =========================
@app.route('/api/delete-email/<int:email_id>', methods=['POST'])
@login_required
def delete_email(email_id):
    user_id = get_current_user()

    if db.delete_email(email_id, user_id):
        return jsonify({'success': True})
    else:
        return jsonify({'error': 'Failed to delete email'}), 400

# =========================
# ERROR HANDLERS
# =========================
@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('500.html'), 500

# =========================
# RUN APP (IMPORTANT FIX)
# =========================
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))  # Render uses this
    app.run(debug=Config.DEBUG, host='0.0.0.0', port=port)
    