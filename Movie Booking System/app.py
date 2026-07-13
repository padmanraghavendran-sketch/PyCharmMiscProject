from flask import Flask, render_template, request, redirect, flash, session, url_for
import mysql.connector
import requests
import re
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import random

app = Flask(__name__, template_folder=os.path.join(os.path.abspath(os.path.dirname(__file__)), 'templates'))
app.secret_key = 'super_secret_cinema_key'

TMDB_TOKEN = "eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiI4NzBlMzEyOTk2NDBmNzhkYWRjZTJmODczODE1NWMwYiIsIm5iZiI6MTc4MzA3NzY5NC4yMiwic3ViIjoiNmE0NzliM2U1NWFkOGQ5Yzg2YTNmZGQ3Iiwic2NvcGVzIjpbImFwaV9yZWFkIl0sInZlcnNpb24iOjF9.K--BNVi7V-SNCbYO7GxC81ubB1AqK4a-YU_jVLtosuY"


def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Modem99r!",
        database="mega_cinema",
        auth_plugin='mysql_native_password'
    )


def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS bookings (
            booking_id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT,
            movie_title VARCHAR(255),
            show_time VARCHAR(50),
            seats_count INT,
            seats_list TEXT,
            booking_token VARCHAR(100),
            total_price INT,
            booking_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    cursor.execute("SHOW COLUMNS FROM movies LIKE 'description';")
    if not cursor.fetchone():
        cursor.execute("ALTER TABLE movies ADD COLUMN description TEXT;")
    cursor.execute("SHOW COLUMNS FROM movies LIKE 'age_rating';")
    if not cursor.fetchone():
        cursor.execute("ALTER TABLE movies ADD COLUMN age_rating VARCHAR(50);")
    conn.commit()
    cursor.close()
    conn.close()


def sync_live_movies():
    conn = None;
    cursor = None
    try:
        url = "https://api.themoviedb.org/3/movie/now_playing?language=en-US&page=1"
        headers = {"accept": "application/json", "Authorization": f"Bearer {TMDB_TOKEN}"}
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            movie_data = response.json().get('results', [])
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
            cursor.execute("TRUNCATE TABLE movies;")
            cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")

            ratings_pool = ['U/A 13+', 'A', 'U', 'PG-13']
            for movie in movie_data[:10]:
                title = movie['title']
                rating = round(movie['vote_average'], 1)
                raw_path = movie.get('poster_path')
                poster_url = f"https://image.tmdb.org/t/p/w500{raw_path}" if raw_path else ""
                description = movie.get('overview', 'No summary available.')
                age_rating = random.choice(ratings_pool)

                cursor.execute(
                    "INSERT INTO movies (title, rating, poster_path, description, age_rating) VALUES (%s, %s, %s, %s, %s)",
                    (title, rating, poster_url, description, age_rating)
                )
            conn.commit()
    except Exception as e:
        print(e)
    finally:
        if cursor is not None: cursor.close()
        if conn is not None: conn.close()


@app.route('/')
def home():
    if 'user_id' in session:
        conn = None;
        cursor = None;
        movies = []
        search_query = request.args.get('search', '').strip()
        is_fallback = False
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            if search_query:
                cursor.execute("SELECT * FROM movies WHERE title LIKE %s", (f"%{search_query}%",))
                movies = cursor.fetchall()
                if not movies:
                    cursor.execute("SELECT * FROM movies")
                    movies = cursor.fetchall()
                    is_fallback = True
            else:
                cursor.execute("SELECT * FROM movies")
                movies = cursor.fetchall()
        except Exception as e:
            print(e)
        finally:
            if cursor is not None: cursor.close()
            if conn is not None: conn.close()
        return render_template('dashboard.html', email=session.get('email'), movies=movies, search_query=search_query,
                               is_fallback=is_fallback)
    return render_template('auth.html')


@app.route('/book/<string:movie_title>')
def book_movie(movie_title):
    if 'user_id' not in session: return redirect('/')
    conn = None;
    cursor = None;
    movie = None;
    past_bookings = []
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM movies WHERE title = %s", (movie_title,))
        movie = cursor.fetchone()
        cursor.execute("SELECT show_time, seats_list FROM bookings WHERE movie_title = %s", (movie_title,))
        past_bookings = cursor.fetchall()
    except Exception as e:
        print(e)
    finally:
        if cursor is not None: cursor.close()
        if conn is not None: conn.close()
    if not movie: return redirect('/')
    return render_template('book.html', movie=movie, past_bookings=past_bookings)


@app.route('/process-payment', methods=['POST'])
def process_payment():
    if 'user_id' not in session: return redirect('/')
    movie_title = request.form.get('movie_title')
    show_time = request.form.get('show_time')
    seats_count = int(request.form.get('seats_count', 0))
    seats_list = request.form.get('seats_list', '').strip()
    total_price = int(request.form.get('total_price', 0))

    booking_token = f"BKM-{random.randint(100000, 999999)}-{random.choice(['X', 'Z', 'Y'])}"
    conn = None;
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO bookings (user_id, movie_title, show_time, seats_count, seats_list, booking_token, total_price) VALUES (%s, %s, %s, %s, %s, %s, %s)",
            (session['user_id'], movie_title, show_time, seats_count, seats_list, booking_token, total_price)
        )
        new_id = cursor.lastrowid
        conn.commit()
        return redirect(url_for('receipt', booking_id=new_id))
    except Exception as e:
        print(e)
        return redirect('/')
    finally:
        if cursor is not None: cursor.close()
        if conn is not None: conn.close()


@app.route('/receipt/<int:booking_id>')
def receipt(booking_id):
    if 'user_id' not in session: return redirect('/')
    conn = None;
    cursor = None;
    booking = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM bookings WHERE booking_id = %s AND user_id = %s",
                       (booking_id, session['user_id']))
        booking = cursor.fetchone()
    except Exception as e:
        print(e)
    finally:
        if cursor is not None: cursor.close()
        if conn is not None: conn.close()
    if not booking: return redirect('/')
    return render_template('receipt.html', b=booking)


@app.route('/history')
def history():
    if 'user_id' not in session: return redirect('/')
    conn = None;
    cursor = None;
    items = []
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM bookings WHERE user_id = %s ORDER BY booking_date DESC", (session['user_id'],))
        items = cursor.fetchall()
    except Exception as e:
        print(e)
    finally:
        if cursor is not None: cursor.close()
        if conn is not None: conn.close()
    return render_template('history.html', email=session.get('email'), bookings=items)


# --- NEW TICKET REFUND CORE CONTROLLER ---
@app.route('/refund/<int:booking_id>', methods=['POST'])
def refund_booking(booking_id):
    if 'user_id' not in session: return redirect('/')
    conn = None;
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        # Ensure users can only drop their own reservations
        cursor.execute("DELETE FROM bookings WHERE booking_id = %s AND user_id = %s", (booking_id, session['user_id']))
        conn.commit()
        flash("Ticket successfully canceled and fully refunded!", "success")
    except Exception as e:
        print(f"Refund error: {e}")
    finally:
        if cursor is not None: cursor.close()
        if conn is not None: conn.close()
    return redirect(url_for('history'))


@app.route('/signup', methods=['POST'])
def signup():
    email = request.form.get('email').strip()
    phone = request.form.get('phone').strip()
    password = request.form.get('password')
    if not re.match(r"^[a-zA-Z0-9._%+-]+@gmail\.com$", email) or not re.match(r"^\d{10}$", phone): return redirect('/')
    conn = None;
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (email, phone, password) VALUES (%s, %s, %s)", (email, phone, password))
        conn.commit()
    except Exception as e:
        print(e)
    finally:
        if cursor is not None: cursor.close()
        if conn is not None: conn.close()
    return redirect('/')


@app.route('/login', methods=['POST'])
def login():
    email = request.form.get('email').strip()
    password = request.form.get('password')
    conn = None;
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE email=%s AND password=%s", (email, password))
        user = cursor.fetchone()
        if user:
            session['user_id'] = user['user_id']
            session['email'] = user['email']
    except Exception as e:
        print(e)
    finally:
        if cursor is not None: cursor.close()
        if conn is not None: conn.close()
    return redirect('/')


@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')


if __name__ == '__main__':
    init_db()
    sync_live_movies()
    app.run(debug=True)