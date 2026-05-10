from flask import Flask, render_template, request, redirect, url_for, flash
import pymysql
from datetime import date, time, timedelta
import os

app = Flask(__name__)

# =========================
# CONFIGURACIÓN
# =========================
app.secret_key = 'mysecretkey'


# =========================
# FUNCIÓN DE CONEXIÓN
# =========================
def get_connection():

    return pymysql.connect(
        host=os.getenv("mysql_host", "localhost"),
        user=os.getenv("mysql_user", "root"),
        password=os.getenv("mysql_password", ""),
        database=os.getenv("mysql_db", "flaskreservas"),
        port=int(os.getenv("mysql_port", 3306)),
        cursorclass=pymysql.cursors.DictCursor
    )


# =========================
# INICIO
# =========================
@app.route('/')
def index():

    try:

        conexion = get_connection()

        cur = conexion.cursor()

        cur.execute("""
            SELECT * FROM reservations
            ORDER BY reservation_date, reservation_time
        """)

        data = cur.fetchall()

        processed_data = []

        for row in data:

            if isinstance(row['reservation_time'], timedelta):

                total_seconds = int(
                    row['reservation_time'].total_seconds()
                )

                hours, remainder = divmod(total_seconds, 3600)

                minutes, seconds = divmod(remainder, 60)

                row['reservation_time'] = time(
                    hours,
                    minutes,
                    seconds
                )

            processed_data.append(row)

        cur.close()
        conexion.close()

        return render_template(
            'index.html',
            reservations=processed_data
        )

    except Exception as e:

        return f"Error en INDEX: {e}"


# =========================
# AGREGAR RESERVA
# =========================
@app.route('/add_reservation', methods=['POST'])
def add_reservation():

    try:

        customer_name = request.form['customer_name']

        reservation_date = date.fromisoformat(
            request.form['reservation_date']
        )

        reservation_time = time.fromisoformat(
            request.form['reservation_time']
        )

        court_type = request.form['court_type']

        conexion = get_connection()

        cur = conexion.cursor()

        cur.execute("""
            INSERT INTO reservations
            (
                customer_name,
                reservation_date,
                reservation_time,
                court_type
            )
            VALUES (%s, %s, %s, %s)
        """, (
            customer_name,
            reservation_date,
            reservation_time,
            court_type
        ))

        conexion.commit()

        cur.close()
        conexion.close()

        flash('Reserva agregada correctamente')

    except Exception as e:

        flash(f'Error al agregar: {e}', 'error')

    return redirect(url_for('index'))


# =========================
# ELIMINAR RESERVA
# =========================
@app.route('/delete_reservation/<id>')
def delete_reservation(id):

    try:

        conexion = get_connection()

        cur = conexion.cursor()

        cur.execute(
            'DELETE FROM reservations WHERE id = %s',
            (id,)
        )

        conexion.commit()

        cur.close()
        conexion.close()

        flash('Reserva eliminada correctamente')

    except Exception as e:

        flash(f'Error al eliminar: {e}', 'error')

    return redirect(url_for('index'))


# =========================
# EDITAR RESERVA
# =========================
@app.route('/edit_reservation/<id>')
def edit_reservation(id):

    try:

        conexion = get_connection()

        cur = conexion.cursor()

        cur.execute(
            'SELECT * FROM reservations WHERE id = %s',
            (id,)
        )

        data = cur.fetchone()

        if data and isinstance(data['reservation_time'], timedelta):

            total_seconds = int(
                data['reservation_time'].total_seconds()
            )

            hours, remainder = divmod(total_seconds, 3600)

            minutes, seconds = divmod(remainder, 60)

            data['reservation_time'] = time(
                hours,
                minutes,
                seconds
            )

        cur.close()
        conexion.close()

        return render_template(
            'edit.html',
            reservation=data
        )

    except Exception as e:

        return f"Error al editar: {e}"


# =========================
# ACTUALIZAR RESERVA
# =========================
@app.route('/update_reservation/<id>', methods=['POST'])
def update_reservation(id):

    try:

        customer_name = request.form['customer_name']

        reservation_date = date.fromisoformat(
            request.form['reservation_date']
        )

        reservation_time = time.fromisoformat(
            request.form['reservation_time']
        )

        court_type = request.form['court_type']

        conexion = get_connection()

        cur = conexion.cursor()

        cur.execute("""
            UPDATE reservations
            SET
                customer_name = %s,
                reservation_date = %s,
                reservation_time = %s,
                court_type = %s
            WHERE id = %s
        """, (
            customer_name,
            reservation_date,
            reservation_time,
            court_type,
            id
        ))

        conexion.commit()

        cur.close()
        conexion.close()

        flash('Reserva actualizada correctamente')

    except Exception as e:

        flash(f'Error al actualizar: {e}', 'error')

    return redirect(url_for('index'))


# =========================
# MAIN
# =========================
if __name__ == '__main__':
    app.run(debug=True)
