from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

class Admin(db.Model, UserMixin):
    A_id = db.Column(db.Integer, primary_key=True)
    Username = db.Column(db.String(50), nullable = False)
    Password = db.Column(db.String(10), nullable=False)

    def get_id(self):
        return str(self.A_id)
    
class User(db.Model, UserMixin):
    U_id = db.Column(db.Integer, primary_key=True)
    Username = db.Column(db.String(50), nullable = False)
    Password = db.Column(db.String(10), nullable=False)
    association = db.relationship('Allotment', backref = "person", secondary = "bookings")
    
    def get_id(self):
        return str(self.U_id)

class Venue(db.Model):
    V_id = db.Column(db.Integer, primary_key=True)
    Name = db.Column(db.String(50), nullable=False)
    Location = db.Column(db.String(50), nullable=False)
    Place = db.Column(db.String(50), nullable=False)
    Capacity = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f"<Venue {self.Name}>"

class Show(db.Model):
    S_id = db.Column(db.Integer, primary_key=True)
    Name = db.Column(db.String(50), nullable = False)
    Rating = db.Column(db.Float, nullable=False)
    Tags = db.Column(db.String(50), nullable = True)
    TicketPrice = db.Column(db.Float, nullable = False)
    location = db.relationship('Venue', backref = "movie", secondary = "allocation")
    
    def __repr__(self):
        return f"<Show {self.Name}>"
    
class Timeframe(db.Model):
    T_id = db.Column(db.Integer, primary_key=True)
    Start_time = db.Column(db.DateTime, nullable=False)
    End_time = db.Column(db.DateTime, nullable=False)
    assignment = db.relationship('Allocation', backref = "time", secondary = "allotment")

    def __repr__(self):
        return f"<Timeframe: {self.Start_time} to {self.End_time} >"
    
class Allocation(db.Model):
    A_id = db.Column(db.Integer, primary_key=True)
    S_id = db.Column(db.Integer, db.ForeignKey("show.S_id"))
    V_id = db.Column(db.Integer, db.ForeignKey("venue.V_id"))

class Allotment(db.Model):
    Allot_id = db.Column(db.Integer, primary_key=True)
    A_id = db.Column(db.Integer, db.ForeignKey("allocation.A_id"))
    T_id = db.Column(db.Integer, db.ForeignKey("timeframe.T_id"))
    S_id = db.Column(db.Integer)
    V_id = db.Column(db.Integer)
    Capacity = db.Column(db.Integer)

class Bookings(db.Model):
    B_id = db.Column(db.Integer, primary_key = True)
    U_id = db.Column(db.Integer, db.ForeignKey("user.U_id"))
    Allot_id = db.Column(db.Integer, db.ForeignKey("allotment.Allot_id"))
    Tickets = db.Column(db.Integer)