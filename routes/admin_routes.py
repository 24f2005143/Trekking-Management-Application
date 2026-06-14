from flask import Blueprint, render_template, request, redirect
from werkzeug.security import generate_password_hash
from flask_login import login_required, current_user
from models import db, User, Trek, Booking, StaffProfile

admin_bp = Blueprint('admin_bp', __name__)

@admin_bp.route('/admin')
@login_required
def admin_dashboard():
    if current_user.role != 'admin':
        return "Access Denied"

    data = {"users": User.query.filter_by(role='user').count(),
        "staff": User.query.filter_by(role='staff').count(),
        "treks": Trek.query.count(),
        "bookings": Booking.query.count()}
    return render_template('admin_dashboard.html', data=data)

@admin_bp.route('/admin/users')
@login_required
def users():
    if current_user.role != 'admin':
        return "Access Denied"

    search = request.args.get('search')

    if search:
        users = User.query.filter((User.name.like(f"%{search}%")) |
            (User.email.like(f"%{search}%")) |
            (User.role.like(f"%{search}%")) |
            (User.id == search if search.isdigit() else False)).all()
    else:
        users = User.query.all()
    return render_template('manage_users.html', users=users)


@admin_bp.route('/block_user/<int:id>', methods=['POST'])
@login_required
def block_user(id):
    if current_user.role != 'admin':
        return "Access Denied"

    user = User.query.get_or_404(id)
    user.is_blacklisted = True

    db.session.commit()
    return redirect('/admin/users')

@admin_bp.route('/unblock_user/<int:id>', methods=['POST'])
@login_required
def unblock_user(id):
    if current_user.role != 'admin':
        return "Access Denied"

    user = User.query.get_or_404(id)
    user.is_blacklisted = False

    db.session.commit()
    return redirect('/admin/users')


@admin_bp.route('/block_staff/<int:id>', methods=['POST'])
@login_required
def block_staff(id):
    if current_user.role != 'admin':
        return "Access Denied"

    staff = User.query.get_or_404(id)

    if staff.role != 'staff':
        return "Not a staff member"

    staff.is_blacklisted = True
    db.session.commit()
    return redirect('/admin/users')


@admin_bp.route('/unblock_staff/<int:id>', methods=['POST'])
@login_required
def unblock_staff(id):
    if current_user.role != 'admin':
        return "Access Denied"

    staff = User.query.get_or_404(id)

    if staff.role != 'staff':
        return "Not a staff member"

    staff.is_blacklisted = False
    db.session.commit()
    return redirect('/admin/users')


@admin_bp.route('/admin/treks')
@login_required
def manage_treks():
    if current_user.role != 'admin':
        return "Access Denied"

    search = request.args.get('search')

    if search:
        treks = Trek.query.filter((Trek.trek_name.like(f"%{search}%")) |
            (Trek.location.like(f"%{search}%")) |
            (Trek.id == search if search.isdigit() else False)).all()
    else:
        treks = Trek.query.all()

    users = User.query.all()
    return render_template('manage_treks.html', treks=treks, users=users)


@admin_bp.route('/add_trek', methods=['POST'])
@login_required
def add_trek():
    if current_user.role != 'admin':
        return "Access Denied"

    trek = Trek(trek_name=request.form.get('trek_name'),
        location=request.form.get('location'),
        duration=request.form.get('duration'),
        difficulty=request.form.get('difficulty'),
        available_slots=10)

    db.session.add(trek)
    db.session.commit()

    return redirect('/admin/treks')

@admin_bp.route('/delete_trek/<int:id>', methods=['POST'])
@login_required
def delete_trek(id):
    if current_user.role != 'admin':
        return "Access Denied"

    trek = Trek.query.get_or_404(id)

    db.session.delete(trek)
    db.session.commit()
    return redirect('/admin/treks')


@admin_bp.route('/edit_trek/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_trek(id):
    if current_user.role != 'admin':
        return "Access Denied"

    trek = Trek.query.get_or_404(id)

    if request.method == 'POST':
        trek.trek_name = request.form.get('trek_name')
        trek.location = request.form.get('location')
        trek.duration = request.form.get('duration')
        trek.difficulty = request.form.get('difficulty')

        db.session.commit()
        return redirect('/admin/treks')
    return render_template('edit_trek.html', trek=trek)


@admin_bp.route('/admin/bookings')
@login_required
def bookings():

    if current_user.role != 'admin':
        return "Access Denied"

    bookings = Booking.query.all()
    return render_template('manage_bookings.html', bookings=bookings)


@admin_bp.route('/admin/booking_history')
@login_required
def booking_history():

    if current_user.role != 'admin':
        return "Access Denied"

    booking_history = db.session.query(Booking, User, Trek)\
        .join(User, Booking.user_id == User.id)\
        .join(Trek, Booking.trek_id == Trek.id).all()

    return render_template('booking_history.html', booking_history=booking_history)


@admin_bp.route('/cancel_booking/<int:id>', methods=['POST'])
@login_required
def cancel_booking(id):
    if current_user.role != 'admin':
        return "Access Denied"

    booking = Booking.query.get_or_404(id)
    db.session.delete(booking)
    db.session.commit()

    return redirect('/admin/bookings')


@admin_bp.route('/add_staff', methods=['GET', 'POST'])
@login_required
def add_staff():
    if current_user.role != 'admin':
        return "Access Denied"

    if request.method == 'POST':
        staff = User(
            name=request.form.get('name'),
            email=request.form.get('email'),
            password=generate_password_hash(request.form.get('password')),
            role='staff'
        )

        db.session.add(staff)
        db.session.commit()

        profile = StaffProfile(user_id=staff.id)
        db.session.add(profile)
        db.session.commit()

        return redirect('/admin/users')

    return render_template('add_staff.html')

@admin_bp.route('/remove_staff/<int:id>', methods=['POST'])
@login_required
def remove_staff(id):

    if current_user.role != 'admin':
        return "Access Denied"

    staff = User.query.get_or_404(id)

    if staff.role != 'staff':
        return "Not a staff member"

    if staff.staff_profile:
        db.session.delete(staff.staff_profile)

    db.session.delete(staff)
    db.session.commit()

    return redirect('/admin/users')


@admin_bp.route('/assign_staff/<int:trek_id>', methods=['POST'])
@login_required
def assign_staff(trek_id):
    if current_user.role != 'admin':
        return "Access Denied"

    trek = Trek.query.get_or_404(trek_id)
    staff_user_id = request.form.get('staff_id')
    staff_profile = StaffProfile.query.filter_by(user_id=staff_user_id).first()

    if staff_profile:
        trek.staff_id = staff_profile.id

    db.session.commit()

    return redirect('/admin/treks')