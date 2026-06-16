from flask import Blueprint, render_template, request, redirect, flash
from werkzeug.security import generate_password_hash
from flask_login import login_required, current_user
from models import db, User, Trek, Booking, StaffProfile

admin_bp = Blueprint('admin_bp', __name__)

def admin_only():
    return current_user.role != 'admin'


@admin_bp.route('/admin')
@login_required
def admin_dashboard():
    if admin_only():
        return "Access Denied"

    data = {"users": User.query.filter_by(role='user').count(),
        "staff": User.query.filter_by(role='staff').count(),
        "treks": Trek.query.count(),
        "bookings": Booking.query.count()}
    return render_template('admin_dashboard.html', data=data)


@admin_bp.route('/admin/users')
@login_required
def users():
    if admin_only():
        return "Access Denied"

    search = request.args.get('search', '')
    role_filter = request.args.get('role', '')

    query = User.query

    if search:
        query = query.filter((User.name.like(f"%{search}%")) |(User.email.like(f"%{search}%")))

    if role_filter:
        query = query.filter_by(role=role_filter)

    all_users = query.all()
    return render_template('manage_users.html', users=all_users, search=search, role_filter=role_filter)


@admin_bp.route('/block_user/<int:id>', methods=['POST'])
@login_required
def block_user(id):
    if admin_only():
        return "Access Denied"
    user = User.query.get_or_404(id)
    user.is_blacklisted = True
    db.session.commit()
    flash(f"{user.name} has been blocked.", "warning")
    return redirect('/admin/users')


@admin_bp.route('/unblock_user/<int:id>', methods=['POST'])
@login_required
def unblock_user(id):
    if admin_only():
        return "Access Denied"
    user = User.query.get_or_404(id)
    user.is_blacklisted = False
    db.session.commit()
    flash(f"{user.name} has been unblocked.", "success")
    return redirect('/admin/users')


@admin_bp.route('/block_staff/<int:id>', methods=['POST'])
@login_required
def block_staff(id):
    if admin_only():
        return "Access Denied"
    staff = User.query.get_or_404(id)
    if staff.role != 'staff':
        return "Not a staff member"
    staff.is_blacklisted = True
    db.session.commit()
    flash(f"Staff {staff.name} has been blocked.", "warning")
    return redirect('/admin/users')


@admin_bp.route('/unblock_staff/<int:id>', methods=['POST'])
@login_required
def unblock_staff(id):
    if admin_only():
        return "Access Denied"
    staff = User.query.get_or_404(id)
    if staff.role != 'staff':
        return "Not a staff member"
    staff.is_blacklisted = False
    db.session.commit()
    flash(f"Staff {staff.name} has been unblocked.", "success")
    return redirect('/admin/users')


@admin_bp.route('/admin/treks')
@login_required
def manage_treks():
    if admin_only():
        return "Access Denied"

    search = request.args.get('search', '')
    difficulty = request.args.get('difficulty', '')
    status = request.args.get('status', '')

    query = Trek.query

    if search:
        query = query.filter((Trek.trek_name.like(f"%{search}%")) |(Trek.location.like(f"%{search}%")))
    if difficulty:
        query = query.filter_by(difficulty=difficulty)
    if status:
        query = query.filter_by(status=status)

    treks = query.all()
    staff_users = User.query.filter_by(role='staff').all()

    return render_template('manage_treks.html', treks=treks, users=staff_users)


@admin_bp.route('/add_trek', methods=['POST'])
@login_required
def add_trek():
    if admin_only():
        return "Access Denied"

    trek = Trek(trek_name=request.form.get('trek_name'),
        location=request.form.get('location'),
        description=request.form.get('description'),
        duration=request.form.get('duration'),
        difficulty=request.form.get('difficulty'),
        available_slots=int(request.form.get('available_slots', 10)))
    db.session.add(trek)
    db.session.commit()
    flash("Trek added successfully!", "success")
    return redirect('/admin/treks')


@admin_bp.route('/delete_trek/<int:id>', methods=['POST'])
@login_required
def delete_trek(id):
    if admin_only():
        return "Access Denied"
    trek = Trek.query.get_or_404(id)
    db.session.delete(trek)
    db.session.commit()
    flash("Trek deleted.", "info")
    return redirect('/admin/treks')


@admin_bp.route('/edit_trek/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_trek(id):
    if admin_only():
        return "Access Denied"
    trek = Trek.query.get_or_404(id)

    if request.method == 'POST':
        trek.trek_name = request.form.get('trek_name')
        trek.location = request.form.get('location')
        trek.description = request.form.get('description')
        trek.duration = request.form.get('duration')
        trek.difficulty = request.form.get('difficulty')
        trek.available_slots = request.form.get('available_slots')
        db.session.commit()
        flash("Trek updated!", "success")
        return redirect('/admin/treks')

    return render_template('edit_trek.html', trek=trek)


@admin_bp.route('/admin/bookings')
@login_required
def bookings():
    if admin_only():
        return "Access Denied"

    status = request.args.get('status', '')
    payment = request.args.get('payment', '')

    query = db.session.query(Booking, User, Trek)\
        .join(User, Booking.user_id == User.id)\
        .join(Trek, Booking.trek_id == Trek.id)

    if status:
        query = query.filter(Booking.booking_status == status)
    if payment:
        query = query.filter(Booking.payment_status == payment)

    bookings = query.all()
    return render_template('manage_bookings.html', bookings=bookings)


@admin_bp.route('/admin/booking_history')
@login_required
def booking_history():
    if admin_only():
        return "Access Denied"

    booking_history = db.session.query(Booking, User, Trek)\
        .join(User, Booking.user_id == User.id)\
        .join(Trek, Booking.trek_id == Trek.id).all()

    return render_template('booking_history.html', booking_history=booking_history)


@admin_bp.route('/cancel_booking/<int:id>', methods=['POST'])
@login_required
def cancel_booking(id):
    if admin_only():
        return "Access Denied"
    booking = Booking.query.get_or_404(id)
    trek = Trek.query.get(booking.trek_id)
    if trek:
        trek.available_slots += 1
    db.session.delete(booking)
    db.session.commit()
    flash("Booking cancelled.", "info")
    return redirect('/admin/bookings')


@admin_bp.route('/add_staff', methods=['GET', 'POST'])
@login_required
def add_staff():
    if admin_only():
        return "Access Denied"

    if request.method == 'POST':
        if User.query.filter_by(email=request.form.get('email')).first():
            flash("Email already exists.", "danger")
            return redirect('/add_staff')

        staff = User(name=request.form.get('name'),email=request.form.get('email'),
            password=generate_password_hash(request.form.get('password')),
            role='staff')
        db.session.add(staff)
        db.session.commit()

        profile = StaffProfile(user_id=staff.id)
        db.session.add(profile)
        db.session.commit()

        flash(f"Staff {staff.name} added successfully!", "success")
        return redirect('/admin/users')

    return render_template('add_staff.html')


@admin_bp.route('/remove_staff/<int:id>', methods=['POST'])
@login_required
def remove_staff(id):
    if admin_only():
        return "Access Denied"
    staff = User.query.get_or_404(id)
    if staff.role != 'staff':
        return "Not a staff member"
    if staff.staff_profile:
        db.session.delete(staff.staff_profile)
    db.session.delete(staff)
    db.session.commit()
    flash("Staff removed.", "info")
    return redirect('/admin/users')


@admin_bp.route('/assign_staff/<int:trek_id>', methods=['POST'])
@login_required
def assign_staff(trek_id):
    if admin_only():
        return "Access Denied"
    trek = Trek.query.get_or_404(trek_id)
    staff_user_id = request.form.get('staff_id')
    staff_profile = StaffProfile.query.filter_by(user_id=staff_user_id).first()
    if staff_profile:
        trek.staff_id = staff_profile.id
        db.session.commit()
        flash("Staff assigned to trek!", "success")
    else:
        flash("Staff profile not found.", "danger")
    return redirect('/admin/treks')
