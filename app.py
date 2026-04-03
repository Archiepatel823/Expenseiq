# ============================================================
# app.py — Main Flask Application
# Expense Tracker with Dashboard
# Stack: Python, Flask, PostgreSQL, SQLAlchemy, HTML/CSS/JS
# ============================================================

import os
from datetime import datetime, date
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
from sqlalchemy import func, extract

# ─── Load environment variables from .env file ───────────────
load_dotenv()

# ─── Initialize Flask app ────────────────────────────────────
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'fallback-secret-key')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Suppress warning

# ─── Initialize extensions ───────────────────────────────────
db = SQLAlchemy(app)           # ORM for database
login_manager = LoginManager(app)
login_manager.login_view = 'login'           # Redirect here if not logged in
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'info'


# ============================================================
# DATABASE MODELS (Tables)
# ============================================================

class User(UserMixin, db.Model):
    """
    User table — stores registered users.
    UserMixin gives us: is_authenticated, is_active, get_id()
    """
    __tablename__ = 'users'

    id       = db.Column(db.Integer, primary_key=True)
    name     = db.Column(db.String(100), nullable=False)
    email    = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)  # Hashed password

    # One user → many expenses (relationship)
    expenses = db.relationship('Expense', backref='user', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<User {self.email}>'


class Expense(db.Model):
    """
    Expense table — each row is one expense entry.
    """
    __tablename__ = 'expenses'

    id          = db.Column(db.Integer, primary_key=True)
    title       = db.Column(db.String(200), nullable=False)
    amount      = db.Column(db.Float, nullable=False)
    category    = db.Column(db.String(50), nullable=False)
    date        = db.Column(db.Date, nullable=False, default=date.today)
    description = db.Column(db.String(500), nullable=True)
    user_id     = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    def __repr__(self):
        return f'<Expense {self.title} ₹{self.amount}>'

    def to_dict(self):
        """Convert to dictionary for JSON API responses"""
        return {
            'id': self.id,
            'title': self.title,
            'amount': self.amount,
            'category': self.category,
            'date': self.date.strftime('%Y-%m-%d'),
            'description': self.description or ''
        }


# Flask-Login: tells it how to load a user from session
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# ============================================================
# EXPENSE CATEGORIES (used in forms + dashboard)
# ============================================================

CATEGORIES = [
    'Food & Dining',
    'Transport',
    'Shopping',
    'Entertainment',
    'Health & Medical',
    'Education',
    'Bills & Utilities',
    'Travel',
    'Other'
]


# ============================================================
# ROUTES — Authentication
# ============================================================

@app.route('/')
def index():
    """Home page — redirect based on login status"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    """
    GET  → Show registration form
    POST → Validate and create new user
    """
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        name     = request.form.get('name', '').strip()
        email    = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm  = request.form.get('confirm_password', '')

        # --- Validation ---
        if not name or not email or not password:
            flash('All fields are required.', 'error')
            return render_template('register.html')

        if password != confirm:
            flash('Passwords do not match.', 'error')
            return render_template('register.html')

        if len(password) < 6:
            flash('Password must be at least 6 characters.', 'error')
            return render_template('register.html')

        # Check if email already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email already registered. Please log in.', 'error')
            return render_template('register.html')

        # Hash password (NEVER store plain text passwords)
        hashed_password = generate_password_hash(password)

        # Create new user and save to database
        new_user = User(name=name, email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        flash('Account created! Please log in.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    GET  → Show login form
    POST → Validate credentials and log in
    """
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        email    = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        user = User.query.filter_by(email=email).first()

        # check_password_hash compares plain vs hashed
        if user and check_password_hash(user.password, password):
            login_user(user)
            flash(f'Welcome back, {user.name}!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password.', 'error')

    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    """Log out the current user"""
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))


# ============================================================
# ROUTES — Dashboard
# ============================================================

@app.route('/dashboard')
@login_required
def dashboard():
    """
    Main dashboard — shows summary cards + recent expenses.
    @login_required means only logged-in users can access this.
    """
    # Get current month and year
    today = date.today()
    current_month = today.month
    current_year  = today.year

    # --- Total spent this month ---
    monthly_total = db.session.query(func.sum(Expense.amount)).filter(
        Expense.user_id == current_user.id,
        extract('month', Expense.date) == current_month,
        extract('year', Expense.date)  == current_year
    ).scalar() or 0

    # --- Total spent all time ---
    all_time_total = db.session.query(func.sum(Expense.amount)).filter(
        Expense.user_id == current_user.id
    ).scalar() or 0

    # --- Total number of expenses ---
    total_count = Expense.query.filter_by(user_id=current_user.id).count()

    # --- Category breakdown (for pie chart) ---
    category_data = db.session.query(
        Expense.category,
        func.sum(Expense.amount).label('total')
    ).filter(
        Expense.user_id == current_user.id,
        extract('month', Expense.date) == current_month,
        extract('year', Expense.date)  == current_year
    ).group_by(Expense.category).all()

    # --- Last 6 months trend (for bar chart) ---
    monthly_trend = db.session.query(
        extract('month', Expense.date).label('month'),
        func.sum(Expense.amount).label('total')
    ).filter(
        Expense.user_id == current_user.id,
        extract('year', Expense.date) == current_year
    ).group_by('month').order_by('month').all()

    # --- 5 most recent expenses ---
    recent_expenses = Expense.query.filter_by(user_id=current_user.id)\
        .order_by(Expense.date.desc()).limit(5).all()

    return render_template('dashboard.html',
        monthly_total   = round(monthly_total, 2),
        all_time_total  = round(all_time_total, 2),
        total_count     = total_count,
        category_data   = category_data,
        monthly_trend   = monthly_trend,
        recent_expenses = recent_expenses,
        current_month   = today.strftime('%B %Y')
    )


# ============================================================
# ROUTES — Expenses (CRUD)
# ============================================================

@app.route('/expenses')
@login_required
def expenses():
    """List all expenses with optional filter by category/month"""
    category_filter = request.args.get('category', '')
    month_filter    = request.args.get('month', '')

    # Start with all expenses for this user
    query = Expense.query.filter_by(user_id=current_user.id)

    if category_filter:
        query = query.filter_by(category=category_filter)

    if month_filter:
        try:
            # month_filter expected as "YYYY-MM"
            year, month = month_filter.split('-')
            query = query.filter(
                extract('year',  Expense.date) == int(year),
                extract('month', Expense.date) == int(month)
            )
        except ValueError:
            pass  # Ignore bad filter input

    all_expenses = query.order_by(Expense.date.desc()).all()

    return render_template('expenses.html',
        expenses        = all_expenses,
        categories      = CATEGORIES,
        category_filter = category_filter,
        month_filter    = month_filter
    )


@app.route('/expenses/add', methods=['GET', 'POST'])
@login_required
def add_expense():
    """
    GET  → Show add expense form
    POST → Save new expense to database
    """
    if request.method == 'POST':
        title       = request.form.get('title', '').strip()
        amount      = request.form.get('amount', '')
        category    = request.form.get('category', '')
        date_str    = request.form.get('date', '')
        description = request.form.get('description', '').strip()

        # --- Validation ---
        errors = []
        if not title:   errors.append('Title is required.')
        if not amount:  errors.append('Amount is required.')
        if not category or category not in CATEGORIES:
            errors.append('Please select a valid category.')
        if not date_str:
            errors.append('Date is required.')

        try:
            amount = float(amount)
            if amount <= 0:
                errors.append('Amount must be greater than 0.')
        except ValueError:
            errors.append('Amount must be a valid number.')

        try:
            expense_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            errors.append('Invalid date format.')
            expense_date = date.today()

        if errors:
            for err in errors:
                flash(err, 'error')
            return render_template('add_expense.html', categories=CATEGORIES,
                                   form_data=request.form)

        # Save to database
        new_expense = Expense(
            title=title,
            amount=amount,
            category=category,
            date=expense_date,
            description=description,
            user_id=current_user.id
        )
        db.session.add(new_expense)
        db.session.commit()

        flash(f'Expense "{title}" added successfully!', 'success')
        return redirect(url_for('expenses'))

    return render_template('add_expense.html', categories=CATEGORIES, form_data={})


@app.route('/expenses/edit/<int:expense_id>', methods=['GET', 'POST'])
@login_required
def edit_expense(expense_id):
    """
    GET  → Show edit form pre-filled with existing data
    POST → Update expense in database
    """
    # Fetch expense — 404 if not found, 403 if not owned by current user
    expense = Expense.query.get_or_404(expense_id)
    if expense.user_id != current_user.id:
        flash('Unauthorized access.', 'error')
        return redirect(url_for('expenses'))

    if request.method == 'POST':
        expense.title       = request.form.get('title', '').strip()
        expense.category    = request.form.get('category', '')
        expense.description = request.form.get('description', '').strip()

        try:
            expense.amount = float(request.form.get('amount', 0))
        except ValueError:
            flash('Invalid amount.', 'error')
            return render_template('edit_expense.html', expense=expense, categories=CATEGORIES)

        try:
            expense.date = datetime.strptime(request.form.get('date', ''), '%Y-%m-%d').date()
        except ValueError:
            flash('Invalid date.', 'error')
            return render_template('edit_expense.html', expense=expense, categories=CATEGORIES)

        db.session.commit()
        flash('Expense updated!', 'success')
        return redirect(url_for('expenses'))

    return render_template('edit_expense.html', expense=expense, categories=CATEGORIES)


@app.route('/expenses/delete/<int:expense_id>', methods=['POST'])
@login_required
def delete_expense(expense_id):
    """Delete an expense (POST only for security)"""
    expense = Expense.query.get_or_404(expense_id)
    if expense.user_id != current_user.id:
        flash('Unauthorized.', 'error')
        return redirect(url_for('expenses'))

    db.session.delete(expense)
    db.session.commit()
    flash('Expense deleted.', 'success')
    return redirect(url_for('expenses'))


# ============================================================
# API ROUTES (JSON) — used by JavaScript charts
# ============================================================

@app.route('/api/category-data')
@login_required
def api_category_data():
    """Returns this month's spending by category as JSON for Chart.js"""
    today = date.today()
    data = db.session.query(
        Expense.category,
        func.sum(Expense.amount).label('total')
    ).filter(
        Expense.user_id == current_user.id,
        extract('month', Expense.date) == today.month,
        extract('year',  Expense.date) == today.year
    ).group_by(Expense.category).all()

    return jsonify({
        'labels': [row.category for row in data],
        'values': [round(row.total, 2) for row in data]
    })


@app.route('/api/monthly-trend')
@login_required
def api_monthly_trend():
    """Returns monthly spending totals for the current year as JSON"""
    MONTH_NAMES = ['Jan','Feb','Mar','Apr','May','Jun',
                   'Jul','Aug','Sep','Oct','Nov','Dec']
    today = date.today()

    data = db.session.query(
        extract('month', Expense.date).label('month'),
        func.sum(Expense.amount).label('total')
    ).filter(
        Expense.user_id == current_user.id,
        extract('year', Expense.date) == today.year
    ).group_by('month').order_by('month').all()

    return jsonify({
        'labels': [MONTH_NAMES[int(row.month) - 1] for row in data],
        'values': [round(row.total, 2) for row in data]
    })


# ============================================================
# RUN THE APP
# ============================================================

if __name__ == '__main__':
    with app.app_context():
        db.create_all()   # Create tables if they don't exist
        print("✅ Database tables created successfully.")
    app.run(debug=True)   # debug=True → auto-reload on code changes
