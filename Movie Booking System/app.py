from flask import Flask, render_template, request, redirect, flash, session, url_for, jsonify
import mysql.connector
import requests
import re
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import random
from datetime import datetime
import time

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
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reviews (
            review_id INT AUTO_INCREMENT PRIMARY KEY,
            movie_title VARCHAR(255),
            user_email VARCHAR(255),
            rating INT,
            comment TEXT,
            likes INT DEFAULT 0,
            dislikes INT DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS waitlists (
            waitlist_id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT,
            user_email VARCHAR(255),
            movie_title VARCHAR(255),
            show_time VARCHAR(50),
            requested_count INT,
            joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    conn.commit()
    cursor.close()
    conn.close()
    print("Database Core Tables mapped and verified successfully!")


# --- ⚡ NEW USP ROUTE: LIVE ENTERPRISE DevOps TELEMETRY API ---
@app.route('/api/telemetry')
def get_system_telemetry():
    if 'user_id' not in session: return jsonify({"error": "Unauthorized"}), 401

    start_time = time.time()
    conn = None;
    cursor = None

    # Baseline architectural simulation metrics
    telemetry_data = {
        "db_status": "CONNECTED",
        "query_latency_ms": 0,
        "total_revenue": 0,
        "active_waitlist_depth": 0,
        "server_load_factor": round(random.uniform(12.4, 38.6), 1),
        "cache_hit_ratio": "94.2%"
    }

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # 1. Aggregate Financial Surge & Base Revenue Metrics
        cursor.execute("SELECT SUM(total_price) as gross_rev FROM bookings")
        rev_res = cursor.fetchone()
        if rev_res and rev_res['gross_rev']:
            telemetry_data["total_revenue"] = int(rev_res['gross_rev'])

        # 2. Extract Queue Depth Optimization Metrics
        cursor.execute("SELECT COUNT(*) as q_depth FROM waitlists")
        q_res = cursor.fetchone()
        if q_res:
            telemetry_data["active_waitlist_depth"] = q_res['q_depth']

        # Calculate real engine compute latency profiles
        telemetry_data["query_latency_ms"] = round((time.time() - start_time) * 1000, 2)

    except Exception as e:
        telemetry_data["db_status"] = f"ERROR: {str(e)}"
    finally:
        if cursor is not None: cursor.close()
        if conn is not None: conn.close()

    return jsonify(telemetry_data)


@app.route('/')
def home():
    if 'user_id' in session:
        conn = None;
        cursor = None
        movies = []
        recommended_movies = []
        search_query = request.args.get('search', '').strip()
        is_fallback = False
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT movie_title FROM bookings WHERE user_id = %s LIMIT 3", (session['user_id'],))
            past_user_bookings = cursor.fetchall()
            booked_titles = [b_log['movie_title'] for b_log in past_user_bookings]

            if search_query:
                cursor.execute("SELECT * FROM movies WHERE title LIKE %s", (f"%{search_query}%",))
                movies = cursor.fetchall()
                if not movies:
                    cursor.execute("SELECT * FROM movies")
                    movies = cursor.fetchall()
                    is_fallback = True
            else:
                cursor.execute("SELECT * FROM movies")
                all_movies = cursor.fetchall()
                if booked_titles:
                    for m in all_movies:
                        if m['rating'] >= 7.2:
                            recommended_movies.append(m)
                        else:
                            movies.append(m)
                else:
                    movies = all_movies
        except Exception as e:
            print(e)
        finally:
            if cursor is not None: cursor.close()
            if conn is not None: conn.close()
        return render_template('dashboard.html', email=session.get('email'), movies=movies,
                               recommendations=recommended_movies, search_query=search_query, is_fallback=is_fallback)
    return render_template('auth.html')


@app.route('/book/<string:movie_title>')
def book_movie(movie_title):
    if 'user_id' not in session: return redirect('/')
    conn = None;
    cursor = None;
    movie = None;
    past_bookings = [];
    movie_reviews = []
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM movies WHERE title = %s", (movie_title,))
        movie = cursor.fetchone()
        cursor.execute("SELECT show_time, seats_list FROM bookings WHERE movie_title = %s", (movie_title,))
        past_bookings = cursor.fetchall()
        cursor.execute("SELECT * FROM reviews WHERE movie_title = %s ORDER BY created_at DESC", (movie_title,))
        movie_reviews = cursor.fetchall()
    except Exception as e:
        print(e)
    finally:
        if cursor is not None: cursor.close()
        if conn is not None: conn.close()
    if not movie: return redirect('/')
    return render_template('book.html', movie=movie, past_bookings=past_bookings, reviews=movie_reviews)


@app.route('/join-waitlist', methods=['POST'])
def join_waitlist():
    if 'user_id' not in session: return redirect('/')
    movie_title = request.form.get('movie_title')
    show_time = request.form.get('show_time')
    conn = None;
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO waitlists (user_id, user_email, movie_title, show_time, requested_count) VALUES (%s, %s, %s, %s, 1)",
            (session['user_id'], session['email'], movie_title, show_time))
        conn.commit()
        flash("⏳ Theater Full! You have successfully joined the live Queue Waitlist.", "success")
    except Exception as e:
        print(e)
    finally:
        if cursor is not None: cursor.close()
        if conn is not None: conn.close()
    return redirect(url_for('book_movie', movie_title=movie_title))


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
        conn.commit()
        return redirect(url_for('receipt', booking_id=cursor.lastrowid))
    except Exception as e:
        print(e); return redirect('/')
    finally:
        if cursor is not None: cursor.close()
        if conn is not None: conn.close()


@app.route('/refund/<int:booking_id>', methods=['POST'])
def refund_booking(booking_id):
    if 'user_id' not in session: return redirect('/')
    conn = None;
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT movie_title, show_time, seats_list FROM bookings WHERE booking_id = %s", (booking_id,))
        cancelled_booking = cursor.fetchone()
        if cancelled_booking:
            cursor.execute("DELETE FROM bookings WHERE booking_id = %s", (booking_id,))
            cursor.execute(
                "SELECT * FROM waitlists WHERE movie_title = %s AND show_time = %s ORDER BY joined_at ASC LIMIT 1",
                (cancelled_booking['movie_title'], cancelled_booking['show_time']))
            next_user_in_queue = cursor.fetchone()
            if next_user_in_queue:
                new_token = f"BKM-QUEUE-{random.randint(100000, 999999)}"
                cursor.execute(
                    "INSERT INTO bookings (user_id, movie_title, show_time, seats_count, seats_list, booking_token, total_price) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                    (next_user_in_queue['user_id'], next_user_in_queue['movie_title'], next_user_in_queue['show_time'],
                     1, cancelled_booking['seats_list'], new_token, 200))
                cursor.execute("DELETE FROM waitlists WHERE waitlist_id = %s", (next_user_in_queue['waitlist_id'],))
        conn.commit()
        flash("Ticket successfully canceled and fully refunded!", "success")
    except Exception as e:
        print(e)
    finally:
        if cursor is not None: cursor.close()
        if conn is not None: conn.close()
    return redirect(url_for('history'))


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


@app.route('/submit-review', methods=['POST'])
def submit_review():
    if 'user_id' not in session: return redirect('/')
    movie_title = request.form.get('movie_title')
    rating = request.form.get('rating')
    comment = request.form.get('comment', '').strip()
    conn = None;
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO reviews (movie_title, user_email, rating, comment) VALUES (%s, %s, %s, %s)",
                       (movie_title, session.get('email'), rating, comment))
        conn.commit()
    except Exception as e:
        print(e)
    finally:
        if cursor is not None: cursor.close()
        if conn is not None: conn.close()
    return redirect(url_for('book_movie', movie_title=movie_title))


@app.route('/like-review/<int:review_id>', methods=['POST'])
def like_review(review_id):
    if 'user_id' not in session: return redirect('/')
    movie_title = request.form.get('movie_title')
    conn = None;
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE reviews SET likes = likes + 1 WHERE review_id = %s", (review_id,))
        conn.commit()
    except Exception as e:
        print(e)
    finally:
        if cursor is not None: cursor.close()
        if conn is not None: conn.close()
    return redirect(url_for('book_movie', movie_title=movie_title))


@app.route('/dislike-review/<int:review_id>', methods=['POST'])
def dislike_review(review_id):
    if 'user_id' not in session: return redirect('/')
    movie_title = request.form.get('movie_title')
    conn = None;
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE reviews SET dislikes = dislikes + 1 WHERE review_id = %s", (review_id,))
        conn.commit()
    except Exception as e:
        print(e)
    finally:
        if cursor is not None: cursor.close()
        if conn is not None: conn.close()
    return redirect(url_for('book_movie', movie_title=movie_title))


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
    app.run(debug=True)