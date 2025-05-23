# app.py
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_mysqldb import MySQL
from datetime import date, time, timedelta # Asegúrate de importar timedelta

app = Flask(__name__)

# Configuración MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''  # Cambia si tienes contraseña
app.config['MYSQL_DB'] = 'flaskreservas' # O el nombre de tu base de datos (e.g., 'flasktasks')

mysql = MySQL(app)

# Clave secreta para los mensajes flash
app.secret_key = 'mysecretkey'

@app.route('/')
def index():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM reservations ORDER BY reservation_date, reservation_time")
    data = cur.fetchall()

    # Procesar los datos para asegurar que reservation_time sea un objeto datetime.time
    processed_data = []
    for row in data:
        row_list = list(row) # Convertir a lista para modificar
        # El tercer índice (3) es reservation_time en tu esquema
        if isinstance(row_list[3], timedelta):
            total_seconds = int(row_list[3].total_seconds())
            hours, remainder = divmod(total_seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            row_list[3] = time(hours, minutes, seconds)
        processed_data.append(tuple(row_list)) # Volver a convertir a tupla

    return render_template('index.html', reservations=processed_data)

@app.route('/add_reservation', methods=['POST'])
def add_reservation():
    if request.method == 'POST':
        customer_name = request.form['customer_name']
        reservation_date_str = request.form['reservation_date']
        reservation_time_str = request.form['reservation_time']
        court_type = request.form['court_type']

        try:
            reservation_date = date.fromisoformat(reservation_date_str)
            reservation_time = time.fromisoformat(reservation_time_str)

            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO reservations (customer_name, reservation_date, reservation_time, court_type) VALUES (%s, %s, %s, %s)",
                        (customer_name, reservation_date, reservation_time, court_type))
            mysql.connection.commit()
            flash('Reserva agregada satisfactoriamente')
        except ValueError:
            flash('Error: Formato de fecha u hora incorrecto. Asegúrate de usar el formato correcto.', 'error')
        except Exception as e:
            flash(f'Error al agregar la reserva: {e}', 'error')
        return redirect(url_for('index'))

@app.route('/delete_reservation/<string:id>')
def delete_reservation(id):
    cur = mysql.connection.cursor()
    cur.execute('DELETE FROM reservations WHERE id = %s', (id,))
    mysql.connection.commit()
    flash('Reserva eliminada satisfactoriamente')
    return redirect(url_for('index'))

@app.route('/edit_reservation/<id>', methods=['GET', 'POST'])
def edit_reservation(id):
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM reservations WHERE id = %s', (id,))
    data = cur.fetchone()

    # Procesar el dato de la reserva para asegurar que reservation_time sea un objeto datetime.time
    if data and isinstance(data[3], timedelta):
        row_list = list(data)
        total_seconds = int(row_list[3].total_seconds())
        hours, remainder = divmod(total_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        row_list[3] = time(hours, minutes, seconds)
        data = tuple(row_list) # Convertir de nuevo a tupla

    return render_template('edit.html', reservation=data)

@app.route('/update_reservation/<id>', methods=['POST'])
def update_reservation(id):
    if request.method == 'POST':
        customer_name = request.form['customer_name']
        reservation_date_str = request.form['reservation_date']
        reservation_time_str = request.form['reservation_time']
        court_type = request.form['court_type']

        try:
            reservation_date = date.fromisoformat(reservation_date_str)
            reservation_time = time.fromisoformat(reservation_time_str)

            cur = mysql.connection.cursor()
            cur.execute("""
                UPDATE reservations
                SET customer_name = %s,
                    reservation_date = %s,
                    reservation_time = %s,
                    court_type = %s
                WHERE id = %s
            """, (customer_name, reservation_date, reservation_time, court_type, id))
            mysql.connection.commit()
            flash('Reserva actualizada correctamente')
        except ValueError:
            flash('Error: Formato de fecha u hora incorrecto. Asegúrate de usar el formato correcto.', 'error')
        except Exception as e:
            flash(f'Error al actualizar la reserva: {e}', 'error')
        return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(port=3000, debug=True)