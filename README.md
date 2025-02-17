# TicketShow

[![Watch the video](https://i.ibb.co/wFSw6zv8/Screenshot-502.jpg)](https://youtu.be/SPLCWM50Lg8?si=vZQtm5_Y7yhq8I7P)

## Introduction
The TicketShow is a web-based application developed using Flask, a Python-based web framework. The objective of this application is to provide a platform for users to book movie tickets for various shows in different theatres and for admins to manage theatres, locations, movies, and timeframes.

## Models
The system follows the Model-View-Controller (MVC) architecture and includes the following models:

- **Venue**: Represents physical locations where shows are held, storing details like name and location.
- **Show**: Represents movies or events, storing details like name, rating, and tags.
- **Timeframe**: Represents specific time windows for shows, including start and end times.
- **Allocation**: Defines relationships between venues and shows, storing venue and show IDs.
- **Allotment**: Defines relationships between allocations and timeframes, including available seat counts.
- **Bookings**: Stores user booking details, including the user's name and ticket count.

## Overall System Design
The project uses Python and Flask to build a web application for booking movie tickets. It utilizes:
- **Flask**: For handling routing and HTTP requests.
- **Jinja2 Templates**: For generating dynamic HTML pages.
- **SQLite**: For storing venue, show, timeframe, and booking details.

The system provides a user-friendly interface for browsing shows and venues, making bookings, and allowing admins to manage venues, shows, and schedules.

## Core Functionality
- Admin and User login
- Venue Management
- Show Management
- Booking Show Tickets
- Searching for Shows/Venues

## How to Run the Project
1. **Clone the Repository**:
   ```sh
   git clone https://github.com/Kanishk-Mishra/TicketShow.git
   cd TicketShow
   ```
2. **Create a Virtual Environment and Activate it**:
   ```sh
   python3 -m venv venv
   source venv/bin/activate  # On Windows use: venv\Scripts\activate
   ```
3. **Install Dependencies**:
   ```sh
   pip install -r requirements.txt
   ```
4. **Run the Application**:
   ```sh
   python3 app.py
   ```
5. **Access the Application**:
   Open `http://127.0.0.1:5000/` in your browser.

## Conclusion
The TicketShow Ticket Booking Platform is a modular and extensible web-based application developed using Flask. It follows the MVC architecture and allows seamless management of movie ticket bookings, making it easy to add new features as required.
