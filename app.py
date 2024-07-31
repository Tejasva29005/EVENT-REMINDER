from flask import Flask, render_template, request, redirect, url_for, flash
import mysql.connector
from datetime import datetime, timedelta
from config import DATABASE_CONFIG
from flask_mail import Mail, Message
from dotenv import load_dotenv
import os

app = Flask(__name__)
app.secret_key = 'ddad214d0942b07320546c2109c392e5f7ad6898ebce4ede'

def get_db_connection():
    return mysql.connector.connect(**DATABASE_CONFIG)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/save', methods=['POST'])
def save_employee():
    name = request.form['name']
    employee_id = request.form['employee_id']
    birth_date = request.form['birth_date']
    anniversary_date = request.form.get('anniversary_date', None)
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO employees (name, employee_id, birth_date, anniversary_date) VALUES (%s, %s, %s, %s)',
        (name, employee_id, birth_date, anniversary_date)
    )
    conn.commit()
    cursor.close()
    conn.close()
    
    flash('Employee details saved successfully!')
    return redirect(url_for('index'))

@app.route('/birthdays')
def birthdays():
    upcoming_birthdays = []
    today = datetime.today().date()
    week_later = today + timedelta(days=7)
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        'SELECT name, employee_id, birth_date FROM employees WHERE DAYOFYEAR(birth_date) BETWEEN DAYOFYEAR(%s) AND DAYOFYEAR(%s) ORDER BY birth_date',
        (today, week_later)
    )
    upcoming_birthdays = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return render_template('birthdays.html', birthdays=upcoming_birthdays)
# Configuring Flask-Mail
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER')
app.config['MAIL_PORT'] = os.getenv('MAIL_PORT')
app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS') == '1'
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_USERNAME')

mail = Mail(app)

@app.route('/send_email', methods=['GET', 'POST'])
def send_email():
    if request.method == 'POST':
        sender_email = request.form['sender_email']
        recipients = request.form['recipients'].split(',')
        subject = request.form['subject']
        body = request.form['body']
        
        msg = Message(subject, sender=sender_email, recipients=recipients)
        msg.body = body
        mail.send(msg)
        
        return redirect(url_for('index'))
    return render_template('send_email.html')

if __name__ == '__main__':
    app.run(debug=True)
