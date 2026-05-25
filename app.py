from flask import Flask
from models import db, User
from werkzeug.security import generate_password_hash

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///trek.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)


with app.app_context():
    db.create_all()

    admin = User.query.filter_by(role="admin").first()

    if not admin:
        admin_user = User(
            name="Admin",
            email="admin@gmail.com",
            password=generate_password_hash("admin123"),
            role="admin"
        )

        db.session.add(admin_user)
        db.session.commit()
        print("Admin Created Successfully!")

    else:
        print("Admin Already Exists!")


@app.route('/')
def home():
    return "Trekking Management Application"


if __name__ == '__main__':
    app.run(debug=True)