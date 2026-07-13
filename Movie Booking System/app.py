from flask import Flask, render_template, request, redirect, flash, session, url_for
import mysql.connector
import requests
import re
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import random
from datetime import datetime

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

    # Clean rebuild of bookings architecture
    cursor.execute(
        "CREATE TABLE IF NOT EXISTS bookings (booking_id INT AUTO_INCREMENT PRIMARY KEY, user_id INT, movie_title VARCHAR(255), show_time VARCHAR(50), seats_count INT, seats_list TEXT, booking_token VARCHAR(100), total_price INT, booking_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP);")

    # FORCE RESET REVIEWS TABLE TO FIX UPDATE ERROR
    cursor.execute("DROP TABLE IF EXISTS reviews;")
    cursor.execute("""
        CREATE TABLE reviews (
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

    conn.commit()
    cursor.close()
    conn.close()
    print("Database Core Tables mapped and verified successfully!")


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


@app.route('/submit-review', methods=['POST'])
def submit_review():
    if 'user_id' not in session: return redirect('/')
    movie_title = request.form.get('movie_title')
    rating = request.form.get('rating')
    comment = request.form.get('comment', '').strip()
    user_email = session.get('email')

    if not rating or not comment:
        flash("❌ Both comment text and star ratings are mandatory!", "error")
        return redirect(url_for('book_movie', movie_title=movie_title))

    conn = None;
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO reviews (movie_title, user_email, rating, comment) VALUES (%s, %s, %s, %s)",
            (movie_title, user_email, rating, comment)
        )
        conn.commit()
        flash("✅ Review successfully added to discussion hub!", "success")
    except Exception as e:
        print(f"CRITICAL REVIEW SAVE ERROR: {e}")
        flash(f"❌ Database failed to save review: {e}", "error")
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


@app.route('/process-payment', methods=['POST'])
def process_payment():
    if 'user_id' not in session: return redirect('/')
    movie_title = request.form.get('movie_title')
    show_time = request.form.get('show_time')
    seats_count = int(request.form.get('seats_count', 0))
    seats_list = request.form.get('seats_list', '').strip()
    total_price = int(request.form.get('total_price', 0))

    card_name = request.form.get('card_name', '').strip()
    card_num = request.form.get('card_num', '').replace(" ", "")
    expiry_input = request.form.get('card_expiry', '').strip()
    cvv = request.form.get('card_cvv', '').strip()

    if not card_name or not card_num or not expiry_input or not cvv:
        flash("❌ All payment inputs are mandatory!", "error")
        return redirect(url_for('book_movie', movie_title=movie_title))
    if not re.match(r"^\d{16}$", card_num) or not re.match(r"^\d{3}$", cvv):
        flash("❌ Invalid Card or CVV length formatting.", "error")
        return redirect(url_for('book_movie', movie_title=movie_title))
    if not re.match(r"^(0[1-9]|1[0-2])\/\d{2}$", expiry_input):
        flash("❌ Expiry format must explicitly be MM/YY.", "error")
        return redirect(url_for('book_movie', movie_title=movie_title))

    try:
        exp_month, exp_year = map(int, expiry_input.split('/'))
        exp_year += 2000
        current_date = datetime.now()
        if (exp_year < current_date.year) or (exp_year == current_date.year and exp_month < current_date.month):
            flash("❌ Payment Declined: This Credit Card has expired!", "error")
            return redirect(url_for('book_movie', movie_title=movie_title))
    except Exception:
        return redirect(url_for('book_movie', movie_title=movie_title))

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
        print(e); return redirect('/')
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


@app.route('/refund/<int:booking_id>', methods=['POST'])
def refund_booking(booking_id):
    if 'user_id' not in session: return redirect('/')
    conn = None;
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM bookings WHERE booking_id = %s AND user_id = %s", (booking_id, session['user_id']))
        conn.commit()
        flash("Ticket successfully canceled and fully refunded!", "success")
    except Exception as e:
        print(e)
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
    app.run(debug=True)