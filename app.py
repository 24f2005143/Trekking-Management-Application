from flask import Flask, render_template, request, redirect, url_for, flash
from models import db, User, StaffProfile, Trek, Booking
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import inspect, text

from routes.admin_routes import admin_bp
from routes.user_routes import user_bp
from routes.staff_routes import staff_bp

app = Flask(__name__)

app.config['SECRET_KEY'] = 'secret123'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///trek.db'

db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

app.register_blueprint(admin_bp)
app.register_blueprint(user_bp)
app.register_blueprint(staff_bp)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


with app.app_context():
    db.create_all()

    trek_columns = {col["name"] for col in inspect(db.engine).get_columns("trek")}
    if "duration" not in trek_columns:
        db.session.execute(text("ALTER TABLE trek ADD COLUMN duration INTEGER"))
        db.session.commit()
    if "description" not in trek_columns:
        db.session.execute(text("ALTER TABLE trek ADD COLUMN description TEXT"))
        db.session.commit()
    user_columns = {col["name"] for col in inspect(db.engine).get_columns("user")}
    if "is_approved" not in user_columns:
        db.session.execute(text("ALTER TABLE user ADD COLUMN is_approved BOOLEAN DEFAULT 1"))
        db.session.commit()

    
    admin = User.query.filter_by(email="admin@gmail.com").first()
    if not admin:
        admin_user = User(name="Admin",
            email="admin@gmail.com",
            password=generate_password_hash("admin123"),
            role="admin")
        db.session.add(admin_user)
        db.session.commit()
        print("Admin created: admin@gmail.com / admin123")


@app.route('/')
def home():
    return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        if User.query.filter_by(email=request.form['email']).first():
            flash("Email already exists. Please login.", "danger")
            return redirect('/register')

        role = request.form.get('role', 'user')
        if role not in ('user', 'staff'):
            role = 'user'

        user = User(name=request.form['name'],
            email=request.form['email'],
            password=generate_password_hash(request.form['password']),
            role=role, is_approved=(role == 'user'))
        
        db.session.add(user)
        db.session.commit()

        if role == 'staff':
            profile = StaffProfile(user_id=user.id)
            db.session.add(profile)
            db.session.commit()
            flash("Registration successful! Please login.", "success")
        else:
            flash("Registration successful! Please login.", "success")
        return redirect('/login')

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(email=request.form['email']).first()

        if not user or not check_password_hash(user.password, request.form['password']):
            flash("Invalid email or password.", "danger")
            return redirect('/login')

        if user.is_blacklisted:
            flash("Your account has been blocked. Contact admin.", "danger")
            return redirect('/login')
        
        if user.role == 'staff' and not user.is_approved:
            flash("Your staff account is awaiting Admin approval.", "warning")
            return redirect('/login')

        login_user(user)

        if user.role == 'admin':
            return redirect('/admin')
        elif user.role == 'staff':
            return redirect('/staff')
        else:
            return redirect('/user')

    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/login')


if __name__ == '__main__':
    app.run(debug=True)
