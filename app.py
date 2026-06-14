from flask import Flask, render_template, request, redirect, url_for
from models import db, User, StaffProfile,Trek,Booking
from flask_login import LoginManager,login_user,logout_user,login_required,current_user

from routes.admin_routes import admin_bp
from routes.user_routes import user_bp

app = Flask(__name__)
app.register_blueprint(admin_bp)
app.register_blueprint(user_bp)

app.config['SECRET_KEY'] = 'secret123'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///trek.db'

db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


with app.app_context():
    db.create_all()

    admin = User.query.filter_by(role='admin').first()

    if not admin:
        admin_user = User(
            name='Admin',
            email='admin@gmail.com',
            password='admin123',
            role='admin'
        )

        db.session.add(admin_user)
        db.session.commit()

        print("Admin Created")



@app.route('/')
def home():
    return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
def register():

    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')

        existing_user = User.query.filter_by(email=email).first()

        if existing_user:
            return "Email already exists"

        new_user = User(
            name=name,
            email=email,
            password=password,
            role='user'
        )

        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('login'))
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email,password=password).first()

        if user:
            if user.is_blacklisted:
                return "You are blacklisted"

            login_user(user)

            if user.role == 'admin':
                return redirect('/admin')
            elif user.role == 'staff':
                return redirect(url_for('staff_dashboard'))
            else:
                return redirect(url_for('user_dashboard'))

        else:
            return "Invalid Email or Password"
    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():

    logout_user()
    return redirect(url_for('login'))




@app.route('/staff')
@login_required
def staff_dashboard():

    if current_user.role != 'staff':
        return "Access Denied"

    return render_template('staff_dashboard.html')


@app.route('/user')
@login_required
def user_dashboard():

    if current_user.role != 'user':
        return "Access Denied"
    return render_template('user_dashboard.html')


@app.route('/add_staff',methods=['GET', 'POST'])
@login_required
def add_staff():

    if current_user.role != 'admin':
        return "Access Denied"

    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')

        existing_user = User.query.filter_by(email=email).first()

        if existing_user:
            return "Email already exists"

        staff_user = User(name=name,email=email,password=password,role='staff')

        db.session.add(staff_user)
        db.session.commit()

        profile = StaffProfile(user_id=staff_user.id)

        db.session.add(profile)
        db.session.commit()

        return "Staff Added Successfully"
    return render_template('add_staff.html')




if __name__ == '__main__':
    app.run(debug=True)