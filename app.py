from flask import Flask, render_template, request, redirect, url_for
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

    trek_columns = {column["name"] for column in inspect(db.engine).get_columns("trek")}
    if "duration" not in trek_columns:
        db.session.execute(text("ALTER TABLE trek ADD COLUMN duration INTEGER"))
        db.session.commit()

    admin = User.query.filter_by(email="admin@gmail.com").first()

    if not admin:
        admin_user = User(
            name="Admin",
            email="admin@gmail.com",
            password=generate_password_hash("admin123"),  # ✅ FIXED
            role="admin"
        )
        db.session.add(admin_user)
        db.session.commit()

        print("✅ Admin created: admin@gmail.com / admin123")


@app.route('/')
def home():
    return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':

        if User.query.filter_by(email=request.form['email']).first():
            return "Email already exists"

        user = User(
            name=request.form['name'],
            email=request.form['email'],
            password=generate_password_hash(request.form['password']),  # ✅ FIXED
            role='user'
        )

        db.session.add(user)
        db.session.commit()

        return redirect('/login')

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':

        user = User.query.filter_by(email=request.form['email']).first()

        if not user:
            return "Invalid email"

        # ✅ FIXED PASSWORD CHECK
        if not check_password_hash(user.password, request.form['password']):
            return "Invalid password"

        if user.is_blacklisted:
            return "You are blocked"

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