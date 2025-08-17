
parking_app
It is a multi-user app that manages different parking lots, parking spots and parked vehicles. Assume that this parking app is for 4-wheeler parking.

📌 Features
🔐 User Authentication (Register & Login with Flask)
👥 Multi-User Support (Admin & Regular Users)
📍 Parking Lot Management (Create, Edit, Delete Lots & Spots)
🎫 Real-Time Spot Reservation & Status Tracking
📊 Parking History with Cost & Time Records

🛠️ Technologies Utilized
🔧 Backend Stack
Flask – Handles routing and backend logic
Flask-Login – Manages user sessions securely
SQLAlchemy – ORM for database modeling and queries
Python 3.12 – Core programming language
🎨 Frontend Tools
HTML, CSS, Bootstrap 5.0 – Design and responsiveness
Jinja2 – Enables dynamic content rendering using templates
🗄️ Database Technologies
SQLite – Lightweight, file-based relational database
SQLAlchemy – Used for database schema creation and interaction
🧠 Application Roles & Functionalities
👨‍💼 Administrator (Superuser)
Has the ability to add, modify, or delete parking lots
Can adjust the number of available parking spaces
Monitors live status of all parking spots (available or booked)
Does not require sign-up; initialized automatically during setup
👤 Registered User
Can sign up and log into the platform
Views and selects available parking locations
Is automatically assigned a free spot upon booking
Has the option to release the reserved spot after use
