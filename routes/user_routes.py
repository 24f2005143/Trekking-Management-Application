from flask import Blueprint, render_template, request, redirect, flash, url_for
from flask_login import login_required, current_user
from models import db, Trek, Booking, User

user_bp = Blueprint('user_bp', __name__)


@user_bp.route('/user')
@login_required
def user_dashboard():
    if current_user.role != 'user':
        return "Access Denied"

    location = request.args.get("location", "")
    difficulty = request.args.get("difficulty", "")

    treks = Trek.query.filter_by(status="Open")

    if location:
        treks = treks.filter(Trek.location.like(f"%{location}%"))
    if difficulty:
        treks = treks.filter_by(difficulty=difficulty)

    treks = treks.all()

    bookings = Booking.query.filter_by(user_id=current_user.id, booking_status="Booked").all()
    booked_trek_ids = [b.trek_id for b in bookings]

    return render_template("user_dashboard.html",treks=treks,
        bookings=bookings,
        booked_trek_ids=booked_trek_ids,
        location=location,
        difficulty=difficulty)


@user_bp.route('/book_trek/<int:trek_id>', methods=['POST'])
@login_required
def book_trek(trek_id):
    if current_user.role != 'user':
        return "Access Denied"

    if current_user.is_blacklisted:
        flash("Your account is blocked. You cannot book treks.", "danger")
        return redirect('/user')

    trek = Trek.query.get_or_404(trek_id)

    
    existing = Booking.query.filter_by(user_id=current_user.id, trek_id=trek.id, booking_status="Booked").first()
    if existing:
        flash("You have already booked this trek.", "warning")
        return redirect('/user')

    if trek.status != "Open":
        flash("This trek is not open for booking.", "danger")
        return redirect('/user')

    if trek.available_slots <= 0:
        flash("No slots available for this trek.", "danger")
        return redirect('/user')

    booking = Booking(user_id=current_user.id, trek_id=trek.id)
    trek.available_slots -= 1
    db.session.add(booking)
    db.session.commit()
    flash(f"Successfully booked {trek.trek_name}!", "success")
    return redirect('/user')


@user_bp.route('/cancel_booking/<int:booking_id>', methods=['POST'])
@login_required
def cancel_booking(booking_id):
    booking = Booking.query.get_or_404(booking_id)

    if booking.user_id != current_user.id:
        return "Not allowed"

    if booking.booking_status != "Booked":
        flash("This booking cannot be cancelled.", "warning")
        return redirect('/user')

    booking.booking_status = "Cancelled"
    booking.trek.available_slots += 1
    db.session.commit()
    flash("Booking cancelled.", "info")
    return redirect('/user')


@user_bp.route('/history')
@login_required
def history():
    if current_user.role != 'user':
        return "Access Denied"

    bookings = Booking.query.filter_by(user_id=current_user.id).all()
    return render_template('history.html', bookings=bookings)


@user_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        existing = User.query.filter_by(email=request.form['email']).first()
        if existing and existing.id != current_user.id:
            flash("Email already taken by another account.", "danger")
            return redirect('/profile')

        current_user.name = request.form['name']
        current_user.email = request.form['email']
        db.session.commit()
        flash("Profile updated successfully!", "success")
        return redirect('/profile')

    return render_template('profile.html')
