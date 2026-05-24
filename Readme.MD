#  Trekking Management Application

## Project Overview

The Trekking Management Application is a web-based project developed for adventure and trekking organizations to manage trekking activities in a simple and organized way.

Many trekking groups still use spreadsheets, phone calls, and manual records to manage bookings and trekking schedules. Because of this, problems like overbooking, missing records, and poor coordination often happen.

This application helps solve these problems by providing a centralized system where:

- Admin can manage treks and staff
- Trek Staff can handle assigned treks
- Users can explore and book trekking events

The project is developed using *Flask*, *SQLite*, *HTML*, *CSS*, *Bootstrap*, and *Jinja2 Templates*.


#  Features

## Admin Module
Admin has complete control over the system.

### Admin can:
- Add new treks
- Edit trek information
- Delete treks
- Add or remove trek staff
- Assign staff to treks
- View all users, staff, and treks
- Search users, staff, or treks using ID or name
- Blacklist users or staff if required


##  Trek Staff Module

Trek Staff members manage trekking activities assigned by the admin.

### Staff can:
- Login after admin approval
- View assigned treks
- Update available slots
- Change trek status (Open / Closed)
- View registered trekkers



##  User (Trekker) Module

Users can explore and participate in trekking events.

### Users can:
- Register and login
- View approved/open treks
- Search treks by location or difficulty
- Book treks
- View booking history
- Check booking status



#  Database Tables

## Trek Table
Stores trekking event details.

### Fields:
- Trek ID
- Trek Name
- Location
- Difficulty
- Duration
- Available Slots
- Assigned Staff ID
- Status
- Start Date
- End Date


## Booking Table
Stores booking details of trekkers.

### Fields:
- Booking ID
- User ID
- Trek ID
- Booking Date
- Booking Status


## Staff Profile Table
Stores trek staff information.

### Fields:
- Staff ID
- Name
- Contact Details
- Assigned Treks
- Status


# Technologies Used

## Backend
- Flask (Python)

## Frontend
- HTML
- CSS
- Bootstrap
- Jinja2

## Database
- SQLite



