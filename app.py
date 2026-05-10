from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# =========================
# CONFIGURACIÓN
# =========================
app.secret_key = 'mysecretkey'

# SQLITE
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///reservas.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# =========================
# MODELO
# =========================
class Reservation(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    customer_name = db.Column(
        db.String(100),
        nullable=False
    )

    reservation_date = db.Column(
        db.String(20),
        nullable=False
    )

    reservation_time = db.Column(
        db.String(20),
        nullable=False
    )

    court_type = db.Column(
        db.String(50),
        nullable=False
    )


# =========================
# CREAR TABLAS
# =========================
with app.app_context():
    db.create_all()


# =========================
# INICIO
# =========================
@app.route('/')
def index():

    reservations = Reservation.query.order_by(
        Reservation.reservation_date,
        Reservation.reservation_time
    ).all()

    return render_template(
        'index.html',
        reservations=reservations
    )


# =========================
# AGREGAR RESERVA
# =========================
@app.route('/add_reservation', methods=['POST'])
def add_reservation():

    try:

        reservation = Reservation(

            customer_name=request.form['customer_name'],

            reservation_date=request.form['reservation_date'],

            reservation_time=request.form['reservation_time'],

            court_type=request.form['court_type']
        )

        db.session.add(reservation)

        db.session.commit()

        flash('Reserva agregada correctamente')

    except Exception as e:

        flash(f'Error: {e}')

    return redirect(url_for('index'))


# =========================
# ELIMINAR
# =========================
@app.route('/delete_reservation/<id>')
def delete_reservation(id):

    reservation = Reservation.query.get(id)

    if reservation:

        db.session.delete(reservation)

        db.session.commit()

        flash('Reserva eliminada correctamente')

    return redirect(url_for('index'))


# =========================
# EDITAR
# =========================
@app.route('/edit_reservation/<id>')
def edit_reservation(id):

    reservation = Reservation.query.get(id)

    return render_template(
        'edit.html',
        reservation=reservation
    )


# =========================
# ACTUALIZAR
# =========================
@app.route('/update_reservation/<id>', methods=['POST'])
def update_reservation(id):

    reservation = Reservation.query.get(id)

    if reservation:

        reservation.customer_name = request.form['customer_name']

        reservation.reservation_date = request.form['reservation_date']

        reservation.reservation_time = request.form['reservation_time']

        reservation.court_type = request.form['court_type']

        db.session.commit()

        flash('Reserva actualizada correctamente')

    return redirect(url_for('index'))


# =========================
# MAIN
# =========================
if __name__ == '__main__':
    app.run(debug=True)

app = app
