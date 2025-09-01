from flask import Flask, render_template, request, jsonify, session
import os
import re
import json
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import secrets

app = Flask(__name__, static_folder='static', template_folder='templates')
app.secret_key = secrets.token_hex(16)  # Secure secret key for sessions


# JSON-Datei für Reservierungen
RESERVATIONS_FILE = 'reservations.json'

EMAIL_CONFIG = {
    'smtp_server': 'smtp.gmail.com',
    'smtp_port': 587,
    'username': 'dominik.trausmuth@gmail.com',
    'password': 'srcd svos cqli kysm',
    'from_email': 'dominik.trausmuth@gmail.com'
}

# Initialisiere die JSON-Datei, falls sie nicht existiert
def init_json():
    if not os.path.exists(RESERVATIONS_FILE):
        with open(RESERVATIONS_FILE, 'w') as file:
            json.dump([], file)

# Lade Reservierungen aus der JSON-Datei
def load_reservations():
    with open(RESERVATIONS_FILE, 'r') as file:
        return json.load(file)

# Speichere Reservierungen in die JSON-Datei
def save_reservations(reservations):
    with open(RESERVATIONS_FILE, 'w') as file:
        json.dump(reservations, file, indent=4)

# Sende eine E-Mail-Benachrichtigung
def send_email(to_email, subject, body):
    try:
        # E-Mail-Inhalte vorbereiten
        msg = MIMEMultipart()
        msg['From'] = EMAIL_CONFIG['from_email']
        msg['To'] = to_email
        msg['Subject'] = subject

        msg.attach(MIMEText(body, 'plain'))

        # SMTP-Server konfigurieren
        with smtplib.SMTP(EMAIL_CONFIG['smtp_server'], EMAIL_CONFIG['smtp_port']) as server:
            server.ehlo()  # Begrüßung
            server.starttls()  # TLS-Verschlüsselung starten
            server.ehlo()  # Erneute Begrüßung nach TLS
            server.login(EMAIL_CONFIG['username'], EMAIL_CONFIG['password'])  # Authentifizierung
            server.sendmail(EMAIL_CONFIG['from_email'], to_email, msg.as_string())  # Sende E-Mail
        print(f"Email sent to {to_email}")
    except smtplib.SMTPAuthenticationError as e:
        print(f"Authentication failed: {e}")
    except Exception as e:
        print(f"Error sending email: {e}")


# Initialisiere die JSON-Datei
init_json()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/menu')
def menu():
    return render_template('menu.html')


@app.route('/save-reservation', methods=['POST'])
def save_reservation():
    data = request.get_json()
    date = data.get('date')
    time = data.get('time')
    guests = data.get('guests')
    user_email = data.get('email')

    if not date or not time or not guests or not user_email:
        return jsonify({'message': 'Error: Missing reservation details.'}), 400

    if not re.match(r'^[\w\.-]+@[a-zA-Z\d\.-]+\.[a-zA-Z]{2,}$', user_email):
        return jsonify({'message': 'Error: Invalid email address.'}), 400

    if not re.match(r'^\d{4}-\d{2}-\d{2}$', date):  # Überprüfe das Datumsformat
        return jsonify({'message': 'Error: Invalid date format. Use YYYY-MM-DD.'}), 400

    reservations = load_reservations()

    # Prüfe, ob der Zeitslot schon 5 Reservierungen hat
    existing_reservations = [r for r in reservations if r['date'] == date and r['time'] == time]
    if len(existing_reservations) >= 5:
        return jsonify({'message': 'Error: This time slot is fully booked.'}), 400

    # Füge die Reservierung hinzu
    reservation = {
        'id': len(reservations) + 1,
        'date': date,
        'time': time,
        'guests': guests,
        'email': user_email
    }
    reservations.append(reservation)
    save_reservations(reservations)

    # Reservierungsdetails in eine Textdatei schreiben
    reservation_time = datetime.strptime(time, "%H:%M").strftime("%I:%M %p")
    reservation_data = f"Reservation Successful\nDate: {date}\nTime: {reservation_time}\nGuests: {guests}\nEmail: {user_email}\n"
    with open('reservations_log.txt', 'a') as file:
        file.write(reservation_data + '\n')

    # Sende Bestätigungs-E-Mails
    admin_email_body = (
        f"A new reservation has been made:\n\n"
        f"Date: {date}\n"
        f"Time: {reservation_time}\n"
        f"Guests: {guests}\n"
        f"Email: {user_email}\n\n"
        f"Please review the reservation details."
    )
    user_email_body = (
        f"Dear customer,\n\n"
        f"Thank you for choosing The Langham! We are delighted to confirm your reservation:\n\n"
        f"Date: {date}\n"
        f"Time: {reservation_time}\n"
        f"Guests: {guests}\n\n"
        f"We look forward to welcoming you and ensuring you have a wonderful experience."
        f" If you have any special requests or need to modify your reservation, please feel free to reach out.\n\n"
        f"Warm regards,\nThe Langham Team"
    )

    send_email(EMAIL_CONFIG['from_email'], "New Reservation Alert", admin_email_body)
    send_email(user_email, "Your Reservation Confirmation", user_email_body)

    return jsonify({'message': 'Reservation successful and email notifications sent!'})

import hashlib

USERS_FILE = 'users.json'

# Initialisiere die Benutzerdatei
def init_users():
    if not os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'w') as file:
            json.dump([], file)

# Lade Benutzer aus der JSON-Datei
def load_users():
    with open(USERS_FILE, 'r') as file:
        return json.load(file)

# Speichere Benutzer in die JSON-Datei
def save_users(users):
    with open(USERS_FILE, 'w') as file:
        json.dump(users, file, indent=4)

@app.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')

    # Eingabevalidierung
    if not name or not email or not password:
        return jsonify({'message': 'Error: Missing fields.'}), 400

    # Prüfe, ob die Email bereits existiert
    users = load_users()
    if any(user['email'] == email for user in users):
        return jsonify({'message': 'Error: Email already registered.'}), 400

    # Passwort verschlüsseln
    hashed_password = hashlib.sha256(password.encode()).hexdigest()

    # Benutzer speichern
    user = {'name': name, 'email': email, 'password': hashed_password}
    users.append(user)
    save_users(users)

    return jsonify({'message': 'Sign-Up successful!'}), 200

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    # Eingabevalidierung
    if not email or not password:
        return jsonify({'message': 'Error: Missing fields.'}), 400

    # Benutzer suchen
    users = load_users()
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    user = next((user for user in users if user['email'] == email and user['password'] == hashed_password), None)

    if user:
        # Session setzen
        session['user_id'] = user['email']
        session['user_name'] = user['name']
        return jsonify({'message': f'Welcome back, {user["name"]}!', 'user': {'name': user['name'], 'email': user['email']}}), 200
    else:
        return jsonify({'message': 'Error: Invalid credentials.'}), 401

@app.route('/logout', methods=['POST'])
def logout():
    # Session löschen
    session.pop('user_id', None)
    session.pop('user_name', None)
    return jsonify({'message': 'Logged out successfully'}), 200

@app.route('/check-auth')
def check_auth():
    """Check if user is authenticated"""
    if 'user_id' in session:
        return jsonify({
            'authenticated': True,
            'user': {
                'name': session.get('user_name'),
                'email': session.get('user_id')
            }
        }), 200
    return jsonify({'authenticated': False}), 401


if __name__ == '__main__':
    app.run(debug=True)
