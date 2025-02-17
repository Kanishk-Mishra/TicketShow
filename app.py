from flask import Flask, render_template, request, redirect
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from datetime import datetime
from models_1 import *

# ============================ Configuration ============================

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///Ticketshowdata.sqlite3"
app.config['SECRET_KEY'] = "myTicketShow"

db.init_app(app)
app.app_context().push()

# Create login manager
admin_login_manager = LoginManager(app)
user_login_manager = LoginManager(app)

# Configure login manager for admin
@admin_login_manager.user_loader
def load_admin_user(admin_id):
    return Admin.query.get(int(admin_id))

@admin_login_manager.unauthorized_handler
def admin_unauthorized():
    return redirect('/admin/login')

# Configure login manager for user
@user_login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@user_login_manager.unauthorized_handler
def user_unauthorized():
    return redirect('/user/login')

# ============================ Controllers ==============================

# Define main page
@app.route('/', methods=['GET', 'POST'])
def main_page():
    return render_template('main_page.html')

# ============================ Admin Side ==============================

# Define admin login
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'GET':
        return render_template('admin_login.html')
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        admin = Admin.query.filter_by(Username=username).first()
        if admin and admin.Password == password:
            login_user(admin)
            return redirect('/admin')
        else:
            return 'Invalid username/password combination'

#Admin dashboard
@app.route('/admin', methods = ['GET', 'POST'])
@login_required
def admin_home():
    admin = current_user.Username
    return render_template('admin_home.html', admin = admin)

#All shows
@app.route('/admin/all_shows', methods = ['GET', 'POST'])
@login_required
def all_shows():
    shows = Show.query.all()
    return render_template('all_shows.html', shows = shows)

#Add show
@app.route('/admin/all_shows/add_shows', methods = ['GET', 'POST'])
@login_required
def add_shows():
    if request.method == 'GET':
        return render_template('add_shows.html')
    if request.method == 'POST':
        s_name = request.form.get('s_name')
        ratings = float(request.form.get('ratings'))        
        tags = request.form.get('tags')
        ticket_price = float(request.form.get('ticket_price'))
        s1 = Show(Name = s_name, Rating = ratings, Tags = tags, TicketPrice = ticket_price)
        db.session.add(s1)
        db.session.commit()
        return redirect('/admin/all_shows')

#Update show
@app.route('/admin/all_shows/upd_show/<int:id>', methods = ['GET', 'POST'])
@login_required
def upd_show(id):
    s = Show.query.get(id)
    if request.method == 'GET':
        return render_template('upd_show.html', s = s)
    if request.method == 'POST':    
        s.Name = request.form.get('s_name')
        s.Rating = float(request.form.get('ratings'))        
        s.Tags = request.form.get('tags')
        s.TicketPrice = float(request.form.get('ticket_price'))
        db.session.commit()
        return redirect('/admin/all_shows')

# Delete show- del_warning.html
@app.route('/admin/all_shows/del_show/<int:id>', methods = ['GET', 'POST'])
@login_required
def del_show(id):
    s = Show.query.get(id)
    form_act = "/admin/all_shows/del_show/" + str(id)
    No = "/admin/all_shows"
    what = "Show Id"
    if request.method == 'GET':
        return render_template('del_warning.html', id = id, form_act = form_act, No = No, what = what)
    if request.method == 'POST':
        db.session.delete(s)
        db.session.commit()
        return redirect('/admin/all_shows')

#Allocate venues    
@app.route('/admin/all_shows/allocate_venues/<int:id>', methods = ['GET', 'POST'])
@login_required
def allocate_venues(id):
    s1 = Show.query.get(id)
    if request.method == 'GET':
        venues = Venue.query.all()
        return render_template('allocate_venues.html', venues = venues, s1 = s1)
    if request.method == 'POST':
        v_id = request.form.get('v_id')
        allocs = Allocation.query.filter_by(V_id = int(v_id), S_id = id).all()
        if len(allocs) == 0:    
            venue = Venue.query.get(int(v_id))
            s1.location.append(venue)
            db.session.commit()            
        return redirect('/admin/all_venues/view_allocations/' + str(v_id))

#All venues   
@app.route('/admin/all_venues', methods = ['GET', 'POST'])
@login_required
def all_venues():
    venues = Venue.query.all()
    return render_template('all_venues.html', venues = venues)

#Add venues
@app.route('/admin/all_venues/add_venues', methods = ['GET', 'POST'])
@login_required
def add_venues():
    if request.method == 'GET':
        return render_template('add_venues.html')
    if request.method == 'POST':
        v_name = request.form.get('v_name')
        location = request.form.get('location')
        place = request.form.get('place')
        capacity = int(request.form.get('capacity'))
        v = Venue(Name = v_name, Location = location, Place = place, Capacity = capacity)
        db.session.add(v)
        db.session.commit()
        return redirect('/admin/all_venues')

#Update venue    
@app.route('/admin/all_venues/upd_venue/<int:id>', methods = ['GET', 'POST'])
@login_required
def upd_venue(id):
    v = Venue.query.get(id)
    orig_capa = v.Capacity
    if request.method == 'GET':
        return render_template('upd_venue.html', v = v)
    if request.method == 'POST':    
        capa = int(request.form.get('capacity'))
        allot = Allotment.query.filter_by(V_id = id).all()
        if len(allot) == 0:
            v.Name = request.form.get('v_name')
            v.Location = request.form.get('location')
            v.Place = request.form.get('place')
            v.Capacity = capa
            db.session.commit()
            return redirect('/admin/all_venues')
        else:
            for a in allot:
                sold = orig_capa - a.Capacity
                if capa < sold:
                    return f"Warning! the updated capacity: {capa} is less than the tickets sold: {sold}, at {v.Name}, {v.Place} for some show. Kindly go back and refill a valid value to avoid any anomaly in the data."
                else:  
                    a.Capacity = capa - sold
                    db.session.commit()
                    v.Name = request.form.get('v_name')
                    v.Location = request.form.get('location')
                    v.Place = request.form.get('place')
                    v.Capacity = capa
                    db.session.commit()
                    return redirect('/admin/all_venues')

#Delete venues    
@app.route('/admin/all_venues/del_venue/<int:id>', methods = ['GET', 'POST'])
@login_required
def del_venue(id):
    v = Venue.query.get(id)
    form_act = "/admin/all_venues/del_venue/" + str(id)
    No = "/admin/all_venues"
    what = "Venue Id"
    if request.method == 'GET':
        return render_template('del_warning.html', id = id, form_act = form_act, No = No, what = what)
    if request.method == 'POST':
        db.session.delete(v)
        db.session.commit()
        return redirect('/admin/all_venues')

#View allocations- for particular venue (id)    
@app.route('/admin/all_venues/view_allocations/<int:id>', methods = ['GET', 'POST'])
@login_required
def view_allocations(id):
    v = Venue.query.get(id)
    shows = v.movie
    allocs = []
    for i in shows:
        a = Allocation.query.filter_by(V_id = id, S_id = i.S_id).first()
        allocs.append(int(a.A_id))
    return render_template('view_allocations.html', v = v, shows = shows, allocs = allocs, lis = list(range(len(shows))))

#All timeframes
@app.route('/admin/all_timeframes', methods = ['GET', 'POST'])
@login_required
def all_timeframes():
    timeframes = Timeframe.query.all()
    return render_template('all_timeframes.html', timeframes = timeframes)

#Add timeframe
@app.route('/admin/all_timeframes/add_timeframes', methods = ['GET', 'POST'])
@login_required
def add_timeframes():
    if request.method == 'GET':
        return render_template('add_timeframes.html')
    if request.method == 'POST':
        stime = datetime.strptime(request.form.get('stime'), '%Y-%m-%dT%H:%M')
        etime = datetime.strptime(request.form.get('etime'), '%Y-%m-%dT%H:%M')
        t1 = Timeframe(Start_time = stime, End_time = etime)
        db.session.add(t1)
        db.session.commit()
        return redirect('/admin/all_timeframes')

#Update timeframe   
@app.route('/admin/all_timeframes/upd_timeframe/<int:id>', methods = ['GET', 'POST'])
@login_required
def upd_timeframe(id):
    t = Timeframe.query.get(id)
    if request.method == 'GET':
        return render_template('upd_timeframe.html', t = t)
    if request.method == 'POST':    
        t.Start_time = datetime.strptime(request.form.get('stime'), '%Y-%m-%dT%H:%M')
        t.End_time = datetime.strptime(request.form.get('etime'), '%Y-%m-%dT%H:%M')
        db.session.commit()
        return redirect('/admin/all_timeframes')

#Delete timeframe    
@app.route('/admin/all_timeframes/del_timeframe/<int:id>', methods = ['GET', 'POST'])
@login_required
def del_timeframe(id):
    t = Timeframe.query.get(id)
    form_act = "/admin/all_timeframes/del_timeframe/" + str(id)
    No = "/admin/all_timeframes"
    what = "Timeframe Id"
    if request.method == 'GET':
        return render_template('del_warning.html', id = id, form_act = form_act, No = No, what = what)
    if request.method == 'POST':
        db.session.delete(t)
        db.session.commit()
        return redirect('/admin/all_timeframes')

#View allotment for paticular timeframe (id)     
@app.route('/admin/all_timeframes/view_allotments/<int:id>', methods = ['GET', 'POST'])
@login_required
def view_allotments(id):
    t = Timeframe.query.get(id)
    allocs = t.assignment
    venues = Venue.query.all()
    shows = Show.query.all()
    return render_template('view_allotments.html', t = t, allocs = allocs, venues = venues, shows = shows)

#Allot timeframes to the particular allocation (id)
@app.route('/admin/allocations/allot_timeframes/<int:id>', methods = ['GET', 'POST'])
@login_required
def allot_timeframes(id):
    a = Allocation.query.get(id)
    ven = Venue.query.get(int(a.V_id))
    if request.method == 'GET':
        t = Timeframe.query.all()
        return render_template('allot_timeframes.html', a = a, t = t)
    if request.method == 'POST':
        t_id = request.form.get('t_id')
        timeframe = Timeframe.query.get(int(t_id))
        allots = Allotment.query.filter_by(A_id = id, T_id = int(t_id)).all()
        if len(allots) == 0:
            a.time.append(timeframe)
            db.session.commit()
        
            allotment = Allotment.query.filter_by(A_id = id, T_id = int(t_id)).first()
            allotment.S_id = a.S_id
            allotment.V_id = a.V_id
            allotment.Capacity = ven.Capacity
            db.session.commit()
        return redirect('/admin/all_timeframes/view_allotments/' + str(t_id))

#Allocations
@app.route('/admin/allocations', methods = ['GET', 'POST'])
@login_required
def allocations():
    asso = Allocation.query.all()
    showid = []
    venueid = []
    for i in asso:
        showid.append(i.S_id)
        venueid.append(i.V_id)
    if request.method == 'GET':
        shname = []
        vname = []
        place = []
        for j in showid:
            shname.append((Show.query.get(j)).Name)
        for k in venueid:
            vname.append((Venue.query.get(k)).Name)
            place.append((Venue.query.get(k)).Place)
        return render_template('allocations.html',lis = list(range(len(asso))), asso = asso, shname = shname, vname = vname, place = place)

#Delete allocations
@app.route('/admin/allocations/del_allocation/<int:id>', methods = ['GET', 'POST'])
@login_required
def del_allocation(id):
    a = Allocation.query.get(id)
    form_act = "/admin/allocations/del_allocation/" + str(id)
    No = "/admin/allocations"
    what = "Allocation Id"
    if request.method == 'GET':
        return render_template('del_warning.html', id = id, form_act = form_act, No = No, what = what)
    if request.method == 'POST':
        db.session.delete(a)
        db.session.commit()
        return redirect('/admin/allocations')

#Allotments
@app.route('/admin/allotments', methods = ['GET', 'POST'])
@login_required
def allotments():
    allots = Allotment.query.all()
    allocs = Allocation.query.all()
    venues = Venue.query.all()
    shows = Show.query.all()
    timeframes = Timeframe.query.all()
    return render_template('allotments.html', timeframes = timeframes, allocs = allocs, venues = venues, shows = shows, allots = allots)

#Delete allotments
@app.route('/admin/allotments/del_allotment/<int:id>', methods = ['GET', 'POST'])
@login_required
def del_allotment(id):
    a1 = Allotment.query.get(id)
    form_act = "/admin/allotments/del_allotment/" + str(id)
    No = "/admin/allotments"
    what = "Allotment Id"
    if request.method == 'GET':
        return render_template('del_warning.html', id = id, form_act = form_act, No = No, what = what)
    if request.method == 'POST':
        db.session.delete(a1)
        db.session.commit()
        return redirect('/admin/allotments')

#Define admin logout
@app.route('/admin/logout')
@login_required
def admin_logout():
    logout_user()
    return redirect('/')

# ============================ User Side ==============================

# Define user login
@app.route('/user/login', methods=['GET', 'POST'])
def user_login():
    if request.method == 'GET':
        return render_template('user_login.html')
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(Username=username).first()
        if user and user.Password == password:
            login_user(user)
            return redirect('/user')
        else:
            return 'Invalid username/password combination'
        
#User dashboard- displays all the cities and search box to search theatres based on location preference and city.
#Renders user_dashboard.html on 'GET' request
#When 'POST' request of the form in by user_dashboard is hit, it acts as a 'GET' request for ve_sear_result.html
#ve_sear_result.html displays all the available shows in the venue and a search box to search for show based on venue and timeframe
@app.route('/user', methods=['GET', 'POST'])
@login_required
def user_dashboard():
    v = Venue.query.all()
    t = Timeframe.query.all()
    v_place = []
    for i in v:
        if i.Place not in v_place:
            v_place.append(i.Place)
    loc_list = []
    for i in v:
        locs = (i.Location).split(", ")
        for j in locs:
            if j not in loc_list:
                loc_list.append(j)
    if request.method == 'GET':    
        return render_template('user_dashboard.html', v_place = v_place, loc_list = loc_list)
    if request.method == 'POST':
        loc = request.form.get('loc')
        city = request.form.get('city')
        if city != '':
            venues_n = []
            venues_p = []
            for i in v:
                if loc in i.Location:
                    venues_n.append(i.Name)
                    venues_p.append(i.Place)
            cities = Venue.query.filter_by(Place = city).all() 
            if len(cities) == 0:
                return "Sorry, no city found with the given name."
            else:
                points_n = []
                points_p = []
                points_id = []
                for i in range(len(venues_n)):
                    for j in cities:
                        if venues_n[i] == j.Name and venues_p[i] == j.Place:
                            points_n.append(j.Name)
                            points_p.append(j.Place)
                            points_id.append(j.V_id)
                if len(points_n) == 0:
                    return "Sorry, no venues found with such place/location combination."
                else:
                    le = range(len(points_n))
                    return render_template('ve_sear_result.html',le = le, points_n = points_n, points_p = points_p, points_id = points_id, t = t)
        if city == '':
            venues_n = []
            venues_p = []
            venues_id = []
            for i in v:
                if loc in i.Location:
                    venues_n.append(i.Name)
                    venues_p.append(i.Place)
                    venues_id.append(i.V_id)
                    l = range(len(venues_n))
            return render_template('ve_sear_result.html',l = l, venues_n = venues_n, venues_p = venues_p, venues_id = venues_id, t = t)

#Check Allotment- Doesn't renders anything (directly) but checks the 'POST' request made by the form in ve_sear_result.html is valid or not
#That is whether a timeframe is allotted to a venue and thus to an allocation or not
#If the request is valid then it redirects to see_show function to render a template containing the shows fulfilling the condition
#This only serves as the 'POST' request for the form in ve_sear_result.html as the 'GET' request is the 'POST' request of user_dasboard
@app.route('/user/city', methods=['GET', 'POST'])
@login_required
def check_allotment():
     if request.method == 'POST':
        v_id = request.form.get('v_id')
        t_id = request.form.get('t_id')  
        allot = Allotment.query.filter_by(V_id = int(v_id), T_id = int(t_id)).all()
        if len(allot) != 0:
            allot_id = allot[0].Allot_id
            return  redirect('/user/city/see_show/' + str(allot_id))
        else:
            return "Sorry! The given timeframe is not allotted to the show, please check for another timeframe."

#Homepage for a particular city
#Displays all the shows available at particular city when clicked on the city name from the user_dashboard
#It also has a form to search for a show based on venue and timeframe
@app.route('/user/city/<place>', methods=['GET', 'POST'])
@login_required
def view_city(place):
    v = Venue.query.filter_by(Place = place).all()
    t = Timeframe.query.all()
    soid = []
    for i in v:
        allo = Allocation.query.filter_by(V_id = i.V_id).all()
        if len(allo) != 0:
            for a in allo:
                soid.append(a.S_id)
    so = []
    if len(soid) != 0:
        for j in soid:
            s = Show.query.get(int(j))
            if s.Name not in so: 
                so.append(s.Name)
    if request.method == 'GET':
        return render_template('view_city.html', v = v, t = t, so = so)
    if request.method == 'POST':
        v_id = request.form.get('v_id')
        t_id = request.form.get('t_id')  
        allot = Allotment.query.filter_by(V_id = int(v_id), T_id = int(t_id)).all()
        if len(allot) != 0:
            allot_id = allot[0].Allot_id
            return  redirect('/user/city/see_show/' + str(allot_id))
        else:
            return "Sorry! The given timeframe is not allotted to the show, please check for another timeframe."

#See Show: Displays available show for given timeframe at a particuar venue 
#It's the page that finally displays the search results of the form in ve_sear_result.html 
#Hit show name to check seat availability
@app.route('/user/city/see_show/<int:id>', methods=['GET', 'POST'])
@login_required
def see_show(id):
    allot = Allotment.query.get(id)
    s = Show.query.get(allot.S_id)
    return render_template('see_show.html', s = s, allot = allot)

#Booking- checks if seat is available on 'GET' request, books the ticket on 'POST' request
#Renders book.html       
@app.route('/user/city/see_show/book/<int:id>', methods=['GET', 'POST'])
@login_required
def booking(id):
    allot = Allotment.query.get(id)
    showid = allot.S_id
    venuid = allot.V_id
    timid = allot.T_id
    s = Show.query.get(int(showid))
    v = Venue.query.get(int(venuid))
    t = Timeframe.query.get(int(timid))
    if request.method == 'GET':
        if allot.Capacity >= 1:
            return render_template('book.html', s = s, v = v, t = t, allot = allot)
        else:
            return f"Housefull! Sorry, there are no seats available for {s.Name} in {v.Name}, {v.Place} at timeframe: {t.Start_time} to {t.End_time}"
    if request.method == 'POST':
        user = request.form.get('username')
        u = User.query.filter_by(Username = user).all()
        if len(u) != 0:
            allot.Capacity = allot.Capacity - 1
            db.session.commit()
            u1 = User.query.filter_by(Username = user).first()
            u1.association.append(allot)
            db.session.commit()

            b = Bookings.query.filter_by(Allot_id = id, U_id = u1.U_id).first()
            if type(b.Tickets) == int:
                b.Tickets = b.Tickets + 1
                db.session.commit()
            else:
                b.Tickets = 1
                db.session.commit()
            return redirect('/user/city/see_show/book/booking_confirmation/' + str(u1.U_id))
        else:
            return "Username mismatch! Please check the spelling of your Username."

#Confirmation page
@app.route('/user/city/see_show/book/booking_confirmation/<int:id>', methods=['GET', 'POST'])
@login_required
def booking_confirmation(id):
    b = Bookings.query.filter_by(U_id = id).all()
    u = User.query.get(id)
    allot = Allotment.query.all()
    ven = Venue.query.all()
    sho = Show.query.all()
    tim = Timeframe.query.all()
    return render_template('confirmation_page.html', b = b, u = u, allot = allot, ven = ven, sho = sho, tim = tim)

#Update number of tickets
@app.route('/user/city/see_show/book/booking_confirmation/tickets/<int:id>', methods=['GET', 'POST'])
@login_required
def tickets(id):
    b = Bookings.query.get(id)
    a = Allotment.query.get(int(b.Allot_id))
    if request.method == 'GET':
        return render_template('tickets.html', id = id)
    if request.method == 'POST':
        total_tick = int(request.form.get('total_tick'))
        if total_tick > (a.Capacity + b.Tickets):
            return "Sorry, the entered value is more than the tickets available."
        elif total_tick < 1:
            return "Oops! The number of tickets to be booked cannot be less than one. You may choose to cancel the booking from the previous tab."
        else:
            a.Capacity = a.Capacity + b.Tickets
            db.session.commit()
            
            b.Tickets = total_tick
            a.Capacity = a.Capacity - b.Tickets
            db.session.commit()
            return redirect('/user/city/see_show/book/booking_confirmation/' + str(b.U_id))

#Cancel Booking       
@app.route('/user/city/see_show/book/booking_confirmation/cancel/<int:id>', methods=['GET', 'POST'])
@login_required
def cancel_booking(id):
    b = Bookings.query.get(id)
    if request.method == 'GET':
        return render_template('cancel_warning.html', b = b)
    if request.method == 'POST':
        allot = Allotment.query.get(b.Allot_id)
        allot.Capacity = allot.Capacity + b.Tickets
        db.session.commit()

        db.session.delete(b)
        db.session.commit()
        return redirect('/user/city/see_show/book/booking_confirmation/' + str(b.U_id))
    
#My Bookings- all the bookings done by the user- a tab on user dasboard
@app.route('/user/my_bookings', methods=['GET', 'POST'])
@login_required
def my_bookings():
    username = current_user.Username
    user = User.query.filter_by(Username = username).first()
    b = Bookings.query.filter_by(U_id = user.U_id).all()
    allot = Allotment.query.all()
    ven = Venue.query.all()
    sho = Show.query.all()
    tim = Timeframe.query.all()
    return render_template('my_bookings.html', b = b, u = username, allot = allot, ven = ven, sho = sho, tim = tim)

#All Shows- Displays all the movies and has form to search them by tags and ratings
#Act as 'GET' request for mo_sear_result.html in its 'POST' request of the form
@app.route('/user/movies', methods=['GET', 'POST'])
@login_required
def shows():
    s = Show.query.all()
    tag_list = []
    for i in s:
        tags = (i.Tags).split(", ")
        for j in tags:
            if j not in tag_list:
                tag_list.append(j)
    if request.method == 'GET':
        return render_template('shows.html', tag_list = tag_list, s = s)
    if request.method == 'POST':
        tag = request.form.get('tag')
        rating = request.form.get('rating')
        if rating != '':
            rating = float(rating)
            shows = []
            for i in s:
                if tag in i.Tags:
                    shows.append(i.Name)
            movies = Show.query.filter_by(Rating = rating).all() 
            if len(movies) == 0:
                return "Sorry, no movies found with the given rating."
            else:
                films = []
                for i in shows:
                    for j in movies:
                        if i == j.Name:
                            films.append(j.Name)
                if len(films) == 0:
                    return "Sorry, no movies found with such tag/rating combination."
                else:
                    return render_template('mo_sear_result.html', films = films)
        if rating == '':
            shows = []
            for i in s:
                if tag in i.Tags:
                    shows.append(i.Name)
            return render_template('mo_sear_result.html', shows = shows)

#View Shows- It is a form to get timeframe for a particular allocation
#Doesn't renders the search results- redirects to tne next decor         
@app.route('/user/movies/view_show/<name>', methods=['GET', 'POST'])
@login_required
def view_shows(name):
    s = Show.query.filter_by(Name = name).first()
    v = Venue.query.all()
    if request.method == 'GET':
        return render_template('view_show.html', v = v, name = name)
    if request.method == 'POST':
        v_id = request.form.get('v_id') 
        allot = Allotment.query.filter_by(V_id = int(v_id), S_id = s.S_id).all()
        if len(allot) != 0:
            allot_id = allot[0].Allot_id
            return  redirect('/user/movies/see_timeframe/' + str(allot_id))
        else:
            return "Sorry! The given venue is not allocated to the show, please check for another venue."

#Displays the search result of the View Shows form    
@app.route('/user/movies/see_timeframe/<int:id>', methods=['GET', 'POST'])
@login_required
def see_timeframe(id):
    allot = Allotment.query.get(id)
    t = Timeframe.query.get(allot.T_id)
    return render_template('see_timeframe.html', t = t, allot = allot)

#Define user logout
@app.route('/user/logout')
@login_required
def user_logout():
    logout_user()
    return redirect('/')
        
if __name__ == "__main__":
    app.run(debug = True)
