# app.py
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
import os
from datetime import datetime

app = Flask(__name__)

# Configuración de MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'travel_agency'
app.config['SECRET_KEY'] = 'your_secret_key_here'

mysql = MySQL(app)

# Rutas principales
@app.route('/')
def index():
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM destinations')
    destinations = cur.fetchall()
    cur.close()
    return render_template('index.html', destinations=destinations)

@app.route('/destinations')
def destinations():
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM destinations')
    destinations = cur.fetchall()
    cur.close()
    return render_template('destinations.html', destinations=destinations)

@app.route('/destination/<int:id>')
def destination_detail(id):
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM destinations WHERE id = %s', (id,))
    destination = cur.fetchone()
    cur.close()
    return render_template('destination_detail.html', destination=destination)

@app.route('/booking/<int:destination_id>', methods=['GET', 'POST'])
def booking(destination_id):
    if 'user_id' not in session:
        flash('Por favor, inicie sesión para realizar una reserva', 'warning')
        return redirect(url_for('login'))

    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM destinations WHERE id = %s', (destination_id,))
    destination = cur.fetchone()

    if request.method == 'POST':
        try:
            # Obtener datos del formulario
            start_date = datetime.strptime(request.form['start_date'], '%Y-%m-%d')
            end_date = datetime.strptime(request.form['end_date'], '%Y-%m-%d')
            passengers = int(request.form['passengers'])
            
            # Calcular el número de noches
            nights = (end_date - start_date).days
            
            if nights <= 0:
                flash('La fecha de fin debe ser posterior a la fecha de inicio', 'error')
                return render_template('booking.html', destination=destination, today=datetime.now().strftime('%Y-%m-%d'))
            
            # Calcular precio total
            total_price = float(destination[3]) * passengers * nights

            # Insertar la reserva
            cur.execute('''
                INSERT INTO bookings 
                (user_id, destination_id, start_date, end_date, passengers, total_price)
                VALUES (%s, %s, %s, %s, %s, %s)
            ''', (
                session['user_id'],
                destination_id,
                start_date.strftime('%Y-%m-%d'),
                end_date.strftime('%Y-%m-%d'),
                passengers,
                total_price
            ))
            mysql.connection.commit()
            flash('¡Reserva realizada con éxito!', 'success')
            return redirect(url_for('my_bookings'))
            
        except Exception as e:
            mysql.connection.rollback()
            flash('Error al procesar la reserva. Por favor, intente nuevamente.', 'error')
            print(f"Error en la reserva: {str(e)}")
            
        finally:
            cur.close()
            
    return render_template('booking.html', 
                         destination=destination, 
                         today=datetime.now().strftime('%Y-%m-%d'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        cur = mysql.connection.cursor()
        cur.execute('SELECT * FROM users WHERE email = %s', (email,))
        user = cur.fetchone()
        cur.close()

        if user and check_password_hash(user[3], password):
            session['user_id'] = user[0]
            session['user_name'] = user[1]
            flash(f'Bienvenido/a {user[1]}!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Email o contraseña incorrectos', 'error')

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Has cerrado sesión correctamente', 'success')
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = generate_password_hash(request.form['password'])

        cur = mysql.connection.cursor()
        try:
            cur.execute('INSERT INTO users (name, email, password) VALUES (%s, %s, %s)',
                       (name, email, password))
            mysql.connection.commit()
            flash('Registro exitoso. Por favor, inicia sesión.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            flash('Error en el registro. El email podría estar ya en uso.', 'error')
        finally:
            cur.close()

    return render_template('register.html')

@app.route('/search')
def search():
    query = request.args.get('q', '')
    cur = mysql.connection.cursor()
    search_query = f"%{query}%"
    cur.execute('''
        SELECT * FROM destinations 
        WHERE name LIKE %s OR description LIKE %s
    ''', (search_query, search_query))
    results = cur.fetchall()
    cur.close()
    return render_template('search_results.html', results=results, query=query)

if __name__ == '__main__':
    app.run(debug=True)