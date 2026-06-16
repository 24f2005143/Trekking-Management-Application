from flask import Blueprint, render_template, request, redirect, flash
from flask_login import login_required, current_user
from models import db, Trek, Booking, StaffProfile, User
from sqlalchemy import func

staff_bp = Blueprint('staff_bp', __name__)


@staff_bp.route('/staff')
@login_required
def staff_dashboard():
    if current_user.role != 'staff':
        return "Access Denied"
    if current_user.is_blacklisted:
        return "Your account has been blocked. Contact admin."

    profile = StaffProfile.query.filter_by(user_id=current_user.id).first()

    treks = db.session.query(Trek, func.count(Booking.id).label("total_trekkers")
    ).outerjoin(Booking, Booking.trek_id == Trek.id)\
     .filter(Trek.staff_id == profile.id)\
     .group_by(Trek.id).all()

    return render_template('staff_dashboard.html', treks=treks)


@staff_bp.route('/staff/trek/<int:trek_id>')
@login_required
def trek_details(trek_id):
    if current_user.role != 'staff':
        return "Access Denied"

    profile = StaffProfile.query.filter_by(user_id=current_user.id).first()
    trek = Trek.query.get_or_404(trek_id)

    if trek.staff_id != profile.id:
        return "Not allowed - this trek is not assigned to you"

    bookings = db.session.query(Booking, User)\
        .join(User, Booking.user_id == User.id)\
        .filter(Booking.trek_id == trek.id).all()

    return render_template('staff_trek_details.html', trek=trek, bookings=bookings)


@staff_bp.route('/staff/remove_participant/<int:booking_id>', methods=['POST'])  
@login_required
def remove_participant(booking_id):
    if current_user.role != 'staff':
        return "Access Denied"

    profile = StaffProfile.query.filter_by(user_id=current_user.id).first()
    booking = Booking.query.get_or_404(booking_id)
    trek = Trek.query.get_or_404(booking.trek_id)

    if trek.staff_id != profile.id:
        return "Not allowed"

    trek.available_slots += 1
    db.session.delete(booking)
    db.session.commit()
    flash("Participant removed.", "info")
    return redirect(f'/staff/trek/{trek.id}')


@staff_bp.route('/staff/update_status/<int:trek_id>', methods=['POST'])
@login_required
def update_status(trek_id):
    if current_user.role != 'staff':
        return "Access Denied"

    profile = StaffProfile.query.filter_by(user_id=current_user.id).first()
    trek = Trek.query.get_or_404(trek_id)

    if trek.staff_id != profile.id:
        return "Not allowed"

    allowed_status = ["Open", "Closed", "Started", "Ongoing", "Completed"]
    status = request.form.get('status')

    if status in allowed_status:
        trek.status = status
        db.session.commit()
        flash(f"Trek status updated to {status}.", "success")
    else:
        flash("Invalid status.", "danger")

    return redirect(f'/staff/trek/{trek_id}')


@staff_bp.route('/staff/update_slots/<int:trek_id>', methods=['POST'])
@login_required
def update_slots(trek_id):
    if current_user.role != 'staff':
        return "Access Denied"

    profile = StaffProfile.query.filter_by(user_id=current_user.id).first()
    trek = Trek.query.get_or_404(trek_id)

    if trek.staff_id != profile.id:
        return "Not allowed"

    slots = request.form.get('slots', 0)
    trek.available_slots = int(slots)
    db.session.commit()
    flash(f"Slots updated to {slots}.", "success")
    return redirect(f'/staff/trek/{trek_id}')
