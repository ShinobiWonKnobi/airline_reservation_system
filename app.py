# app.py

from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
from passlib.hash import sha256_crypt  # You'll need to install passlib
from flask import g

app = Flask(__name__)

# MySQL Configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_DB'] = 'airline_db'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
mysql = MySQL(app)

# Secret key for session management
app.secret_key = 'your_secret_key'

# Database connection functions
def get_db():
    # Check if 'db' is not in the global context (g)
    if 'db' not in g:
        # If not, create a cursor from the MySQL connection
        g.db = mysql.connection.cursor()

    # Return the cursor
    return g.db

# Placeholder function for getting user profile data
def get_user_profile(username):
    try:
        # Get a cursor from the connection
        cur = get_db()

        # Execute the SELECT query to fetch user profile data
        cur.execute("SELECT username, email, age FROM users WHERE username = %s", (username,))

        # Fetch the user profile data
        user_profile = cur.fetchone()

        if user_profile:
            # Convert the result to a dictionary for easier use in templates
            profile_data = {
                "username": user_profile['username'],
                "email": user_profile['email'],
                "age": user_profile['age']
                # Add more fields as needed
            }

            return profile_data
        else:
            # User not found
            return None

    except Exception as e:
        # Handle exceptions (e.g., database errors)
        print(f"Error fetching user profile: {e}")
        return None
    finally:
        # Close the cursor (done automatically due to teardown_appcontext)
        pass

# Routes

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = sha256_crypt.hash(request.form['password'])
        name = request.form['name']

        # Insert user data into the 'users' table
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO users (username, password, name) VALUES (%s, %s, %s)", (username, password, name))
        mysql.connection.commit()
        cur.close()

        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        entered_password = request.form['password']

        # Retrieve user data from the 'users' table
        cur = mysql.connection.cursor()
        result = cur.execute("SELECT * FROM users WHERE username = %s", [username])

        if result > 0:
            user_data = cur.fetchone()
            stored_password = user_data['password']

            if sha256_crypt.verify(entered_password, stored_password):
                # Login successful
                session['logged_in'] = True
                session['username'] = username

                # Check if there is a 'next' parameter
                next_url = request.args.get('next')
                if next_url:
                    return redirect(next_url)
                else:
                    return redirect(url_for('dashboard'))
            else:
                # Incorrect password
                return render_template('login.html', error='Invalid password')
        else:
            # User not found
            return render_template('login.html', error='User not found')

    return render_template('login.html')



# Update your dashboard route
@app.route('/dashboard')
def dashboard():
    if 'logged_in' in session:
        return render_template('dashboard/main_dashboard.html')
    else:
        return redirect(url_for('login', next=request.url))
    
# Add routes for different sections
@app.route('/dashboard/profile')
def dashboard_profile():
    if 'logged_in' in session:
        # Fetch user profile data from the database
        profile_data = get_user_profile(session['username'])  # Implement this function
        return render_template('dashboard/profile.html', profile_data=profile_data)
    else:
        return redirect(url_for('login', next=request.url))


@app.route('/dashboard/book_flight')
def dashboard_book_flight():
    # Assume you have a list of flights. Replace this with your actual logic to get flights from the database.
    flights = [
        {"id": 1, "source": "City A", "destination": "City B", "departure_time": "12:00 PM", "price": 150},
        {"id": 2, "source": "City C", "destination": "City D", "departure_time": "2:30 PM", "price": 200},
        # Add more flights as needed
    ]

    return render_template('dashboard/book_flight.html', flights=flights)

@app.route('/dashboard/confirm_booking/<int:flight_id>')
def confirm_booking(flight_id):
    # Add logic to confirm the booking. You can update the database or perform other actions.
    # For now, we'll just display a confirmation message.
    return f"Booking confirmed for flight with ID {flight_id}. Thank you for booking!"

if __name__ == '__main__':
    app.run(debug=True)
