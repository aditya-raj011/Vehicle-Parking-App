from flask import Flask, render_template,session, flash, redirect,request
from flask import current_app as app
from .models import*
from datetime import date
from application.models import User,ParkingLot, ParkingSpot, Reservation 
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use("Agg")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        pwd = request.form.get("pwd")
        this_user = User.query.filter_by(username=username).first()

        if this_user:
            if this_user.password == pwd:
                if this_user.type == "admin":
                    return redirect("/admin")
                else:
                    return redirect(f"/home/{this_user.id}")
            else:
                return "Password is incorrect"
        else:
            return "User does not exist"

    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        pwd = request.form.get("pwd")
        fullname = request.form.get("fullname")
        address = request.form.get("address")
        pincode = request.form.get("pincode")

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            return "User already exists!"

        new_user = User(username=username,password=pwd,fullname=fullname,address=address, pincode=pincode, type="user")
        db.session.add(new_user)
        db.session.commit()
        return redirect("/login")

    return render_template("register.html")



@app.route("/admin")
def admin_dashboard():
    this_user = User.query.filter_by(type="admin").first()
    filter_by = request.args.get("filter_by")
    search_text = request.args.get("search_text", "")

    if filter_by == "location":
        lots = ParkingLot.query.filter(ParkingLot.prime_location_name.ilike(f"%{search_text}%")).all()
    elif filter_by == "pincode":
        lots = ParkingLot.query.filter(ParkingLot.pincode.ilike(f"%{search_text}%")).all()
    else:
        lots = ParkingLot.query.all()
    return render_template("admin_dash.html", this_user=this_user, lots=lots)


@app.route("/home/<int:user_id>")
def user_dash(user_id):
    this_user = User.query.get(user_id)
    search_text = request.args.get("search_text", "").strip()

    if search_text:
        lots = ParkingLot.query.filter(
            (ParkingLot.prime_location_name.ilike(f"%{search_text}%")) |
            (ParkingLot.pincode.ilike(f"%{search_text}%"))
        ).all()
    else:
        lots = ParkingLot.query.all()
    for lot in lots:
        lot.available_spots = len([s for s in lot.spots if s.status == 'A'])

    history = Reservation.query.filter_by(user_id=user_id).order_by(Reservation.parking_timestamp.desc()).all()
    return render_template("user_dash.html", this_user= this_user, lots=lots, history=history,search_text=search_text)



@app.route("/add_parking_lot", methods=["GET", "POST"])
def add_parking_lot():
    if request.method == "POST":
        prime_location_name = request.form.get("name")
        address = request.form.get("address")
        pincode = request.form.get("pincode")
        price = request.form.get("price")
        max_spots = int(request.form.get("max_spots"))

        existing_lot = ParkingLot.query.filter_by(prime_location_name=prime_location_name).first()
        if existing_lot:
            return "Parking Lot with this name already exists!"
        new_lot = ParkingLot(prime_location_name=prime_location_name, address=address, pincode=pincode,price=price, max_spots=max_spots)
        db.session.add(new_lot)
        db.session.commit()

        for _ in range(max_spots):
            spot = ParkingSpot(lot_id=new_lot.id, status='A')
            db.session.add(spot)
        db.session.commit()
        return redirect("/admin")

    return render_template("new_parking.html")


@app.route("/book/<int:lot_id>/<int:user_id>", methods=["GET", "POST"])
def book_parking(lot_id, user_id):
    user = User.query.get(user_id)
    lot = ParkingLot.query.get(lot_id)

    spot = ParkingSpot.query.filter_by(lot_id=lot.id, status='A').first()
    if not spot:
        return "No available spots in this lot."

    if request.method == "POST":
        vehicle_no = request.form.get("vehicle_no")
        spot.status = "O"
        reservation = Reservation(user_id=user.id, spot_id=spot.id, vehicle_number=vehicle_no)
        db.session.add(reservation)
        db.session.commit()
        return redirect(f"/home/{user.id}")
    return render_template("book_parking.html", user=user, lot=lot, spot=spot)

@app.route("/logout")
def logout():
    return redirect("/login")


@app.route("/users")
def users():
    users = User.query.filter_by(type="user").all()
    admin = User.query.filter_by(type="admin").first() 
    return render_template("users.html", users=users, this_user=admin)

@app.route("/occupied_details/<int:spot_id>")
def occupied_details(spot_id):
    spot = ParkingSpot.query.get(spot_id)
    reservation = Reservation.query.filter_by(spot_id=spot.id, leaving_timestamp=None).first()
    return render_template("occu_parking.html", spot=spot, reservation=reservation)



@app.route("/edit_lot/<int:lot_id>", methods=["GET", "POST"])
def edit_lot(lot_id):
    lot = ParkingLot.query.get(lot_id)

    if request.method == "POST":
        lot.prime_location_name = request.form.get("name")
        lot.address = request.form.get("address")
        lot.pincode = request.form.get("pincode")
        lot.price = float(request.form.get("price"))
        new_max = int(request.form.get("max_spots"))

        current_spots = ParkingSpot.query.filter_by(lot_id=lot.id).all()
        current_count = len(current_spots)

        if new_max > current_count:
            for _ in range(new_max - current_count):
                new_spot = ParkingSpot(lot_id=lot.id, status='A')  
                db.session.add(new_spot)


        elif new_max < current_count:
            available_spots = [s for s in current_spots if s.status == 'A']
            spots_to_remove = current_count - new_max

            if len(available_spots) >= spots_to_remove:
                for spot in available_spots[:spots_to_remove]:
                    for r in spot.reservations:
                        db.session.delete(r)
                    db.session.delete(spot)
            else:
                return "Cannot reduce spots. Too many are occupied."

        lot.max_spots = new_max
        db.session.commit()
        return redirect("/admin")

    return render_template("edit_parking.html", lot=lot)



@app.route("/view_spot/<int:spot_id>")
def view_spot(spot_id):
    spot = ParkingSpot.query.get(spot_id)
    return render_template("view_parking.html", spot=spot)




@app.route("/delete_spot/<int:spot_id>", methods=["POST"])
def delete_spot(spot_id):
    spot = ParkingSpot.query.get(spot_id)
    lot = spot.lot  #Use the backref

    if spot.status == 'A':
        db.session.delete(spot)
        db.session.commit()
        lot.max_spots = ParkingSpot.query.filter_by(lot_id= lot.id).count()
        db.session.commit()
        return redirect("/admin")
    return "Cannot delete an occupied spot."

@app.route("/delete_lot/<int:lot_id>", methods=["POST"])
def delete_lot(lot_id):
    lot = ParkingLot.query.get(lot_id)
    occupied_spots = [spot for spot in lot.spots if spot.status == 'O']
    if occupied_spots:
        return "Cannot delete lot. Some spots are still occupied."
    
    ParkingSpot.query.filter_by(lot_id=lot_id).delete()
    db.session.delete(lot)
    db.session.commit()
    return redirect("/admin")



@app.route("/release/<int:reservation_id>", methods=["GET", "POST"])
def release_parking(reservation_id):
    reservation = Reservation.query.get(reservation_id)
    spot = ParkingSpot.query.get(reservation.spot_id)
    lot = ParkingLot.query.get(spot.lot_id)

    if request.method == "POST":
        reservation.leaving_timestamp = datetime.utcnow()
        duration_hours = (reservation.leaving_timestamp - reservation.parking_timestamp).total_seconds() / 3600
        cost = round(duration_hours * lot.price, 2)

        reservation.cost_per_unit = cost
        spot.status = "A"

        db.session.commit()
        return redirect(f"/home/{reservation.user_id}")

    # Calculate cost
    current_time = datetime.utcnow()
    duration_hours = (current_time - reservation.parking_timestamp).total_seconds() / 3600
    cost = round(duration_hours * lot.price, 2)

    return render_template(
        "release_parking.html",
        spot=spot,
        reservation=reservation,
        current_time=current_time.strftime("%Y-%m-%d %H:%M"),
        cost=cost
    )



@app.route("/edit_profile/<int:user_id>", methods=["GET", "POST"])
def edit_profile(user_id):
    user = User.query.get(user_id)
    if request.method == "POST":
        user.fullname = request.form["fullname"]
        user.address = request.form["address"]
        user.pincode = request.form["pincode"]
        db.session.commit()

        if user.type == "admin":
            return redirect("/admin")
        else:
            return redirect(f"/home/{user.id}")
    return render_template("edit_profile.html", user=user)


@app.route("/admin_summary")
def admin_summary():
    lots = ParkingLot.query.all()

    lot_names = []
    available = []
    occupied = []
    revenue = []

    for lot in lots:
        lot_names.append(lot.prime_location_name)
        a, o, r = 0, 0, 0

        for spot in lot.spots:
            if spot.status == 'A':
                a += 1
            elif spot.status == 'O':
                o += 1

            for res in spot.reservations:
                if res.leaving_timestamp:
                    duration = (res.leaving_timestamp - res.parking_timestamp).total_seconds() / 3600
                    r += duration * res.cost_per_unit

        available.append(a)
        occupied.append(o)
        revenue.append(r)

    # Bar Chart 
    if lot_names:
        x = range(len(lot_names))
        bar_width = 0.35
        plt.bar([i - bar_width/2 for i in x], available, width=bar_width, label="Available", color="green")
        plt.bar([i + bar_width/2 for i in x], occupied, width=bar_width, label="Occupied", color="red")
        plt.xticks(x, lot_names, rotation=30)
        plt.xlabel("Parking Lots")
        plt.ylabel("No. of Spots")
        plt.title("Available vs Occupied")
        plt.legend()
        plt.tight_layout()
        plt.savefig("static/lot_status_bar.png")
        plt.clf()

    # Pie Chart
    if any(revenue):
        plt.pie(revenue, labels=lot_names, autopct="%1.1f%%", colors=plt.cm.Pastel1.colors)
        plt.title("Revenue Share")
        plt.tight_layout()
        plt.savefig("static/revenue_pie.png")
        plt.clf()

    admin = User.query.filter_by(type="admin").first()

    return render_template("admin_summary.html", this_user=admin)


@app.route("/user_summary/<int:user_id>")
def user_summary(user_id):
    user = User.query.get(user_id)
    reservations = Reservation.query.filter_by(user_id=user_id).all()

    lot_names = []
    lot_counts = []

    for reservation in reservations:
        lot_name = reservation.spot.lot.prime_location_name
        if lot_name in lot_names:
            lot_counts[lot_names.index(lot_name)] += 1
        else:
            lot_names.append(lot_name)
            lot_counts.append(1)

    # Bar Chart
    colors = ["green", "blue", "red"] * ((len(lot_names) // 3) + 1)
    plt.bar(lot_names, lot_counts, color=colors[:len(lot_names)])
    plt.title("Summary on Already Used Parking Spots")
    plt.xlabel("Parking Lots")
    plt.ylabel("Usage Count")
    plt.xticks(rotation=30)
    plt.tight_layout()
    plt.savefig("static/user_bar.png")
    plt.clf()

    return render_template("user_summary.html", this_user=user)






