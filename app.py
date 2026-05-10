from flask import Flask, render_template, request, redirect, url_for, flash
import pymysql
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = "secretkey"


# =========================
# CONEXIÓN MYSQL
# =========================
def get_connection():

    return pymysql.connect(
        host=os.getenv("MYSQL_HOST"),
        user=os.getenv("MYSQL_USER"),
        password=os.getenv("MYSQL_PASSWORD"),
        database=os.getenv("MYSQL_DATABASE"),
        port=int(os.getenv("MYSQL_PORT", 3306)),
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

        reservations = cur.fetchall()

        cur.close()
        conexion.close()

        return render_template(
            'index.html',
            reservations=reservations
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
        reservation_date = request.form['reservation_date']
        reservation_time = request.form['reservation_time']
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

        flash(f'Error: {e}')

    return redirect(url_for('index'))


# =========================
# ELIMINAR
# =========================
@app.route('/delete_reservation/<int:id>')
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

        flash('Reserva eliminada')

    except Exception as e:

        flash(f'Error: {e}')

    return redirect(url_for('index'))


# =========================
# EDITAR
# =========================
@app.route('/edit_reservation/<int:id>')
def edit_reservation(id):

    try:

        conexion = get_connection()
        cur = conexion.cursor()

        cur.execute(
            'SELECT * FROM reservations WHERE id = %s',
            (id,)
        )

        reservation = cur.fetchone()

        cur.close()
        conexion.close()

        return render_template(
            'edit.html',
            reservation=reservation
        )

    except Exception as e:

        return f"Error: {e}"


# =========================
# ACTUALIZAR
# =========================
@app.route('/update_reservation/<int:id>', methods=['POST'])
def update_reservation(id):

    try:

        customer_name = request.form['customer_name']
        reservation_date = request.form['reservation_date']
        reservation_time = request.form['reservation_time']
        court_type = request.form['court_type']

        conexion = get_connection()
        cur = conexion.cursor()

        cur.execute("""
            UPDATE reservations
            SET
                customer_name=%s,
                reservation_date=%s,
                reservation_time=%s,
                court_type=%s
            WHERE id=%s
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

        flash('Reserva actualizada')

    except Exception as e:

        flash(f'Error: {e}')

    return redirect(url_for('index'))


# =========================
# MAIN
# =========================
if __name__ == '__main__':
    app.run(debug=True)
