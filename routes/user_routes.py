from flask import Blueprint, render_template, request, redirect
from flask_login import login_required, current_user
from models import db, Trek, Booking

user_bp = Blueprint('user_bp', __name__)


@user_bp.route('/user')
@login_required
def user_dashboard():
    if current_user.role != 'user':
        return "Access Denied"

    treks = Trek.query.all()
    bookings = Booking.query.filter_by(user_id=current_user.id).all()

    return render_template('user_dashboard.html', treks=treks, bookings=bookings)


@user_bp.route('/book_trek/<int:trek_id>', methods=['POST'])
@login_required
def book_trek(trek_id):
    if current_user.role != 'user':
        return "Access Denied"

    trek = Trek.query.get_or_404(trek_id)

    if trek.available_slots <= 0:
        return "No slots available"

    existing = Booking.query.filter_by(user_id=current_user.id, trek_id=trek.id).first()
    if existing:
        return "Already booked"

    booking = Booking(
        user_id=current_user.id,
        trek_id=trek.id
    )

    trek.available_slots -= 1

    db.session.add(booking)
    db.session.commit()

    return redirect('/user')


@user_bp.route('/cancel_booking/<int:booking_id>')
@login_required
def cancel_booking(booking_id):
    booking = Booking.query.get_or_404(booking_id)

    if booking.user_id != current_user.id:
        return "Not allowed"

    trek = booking.trek
    trek.available_slots += 1

    db.session.delete(booking)
    db.session.commit()

    return redirect('/user')