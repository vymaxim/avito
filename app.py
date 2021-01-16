from flask import Flask, jsonify, request

import db
import psycopg2

conn = db.connect
cur = conn.cursor()

app = Flask(__name__)


@app.route('/room/list', methods=['GET'])

# Example request:
# curl -X GET http://127.0.0.1:5000/room/list
# curl -X GET http://127.0.0.1:5000/room/list "sort=price asc"
# curl -X GET http://127.0.0.1:5000/room/list "sort=price desc"
# curl -X GET http://127.0.0.1:5000/room/list "sort=data asc"
# curl -X GET http://127.0.0.1:5000/room/list "sort=data desc"

def room_list():
    sort = request.form.get('sort')
    try:
        if sort is None:
            cur.execute("SELECT * FROM ROOMS")
        elif sort.lower() == 'price asc':
            cur.execute("SELECT * FROM ROOMS ORDER BY PRICE ASC")
        elif sort.lower() == "price desc":
            cur.execute("SELECT * FROM ROOMS ORDER BY PRICE DESC")
        elif sort.lower() == "data asc":
            cur.execute("SELECT * FROM ROOMS ORDER BY DATA_CREATE ASC")
        elif sort.lower() == "data desc":
            cur.execute("SELECT * FROM ROOMS ORDER BY DATA_CREATE DESC")
        else:
            return jsonify(f'Invalid request. The options request: "sort=price asc" or "sort=price desc" or "sort=data asc" or "sort=data desc"')
        rows = cur.fetchall()
        rooms_list = []
        for row in rows:
            room = {
                "room_id": row[0],
                "description": row[1],
                "price": row[2],
                "data_create": row[3]
            }
            rooms_list.append(room)
        if not room_list:
            return jsonify(f'the list of rooms is empty')
        else:
            return jsonify(rooms_list)
    except psycopg2.errors.InFailedSqlTransaction:
        cur.execute('rollback')
        return jsonify(f'Invalid request, try again')


@app.route('/room/create', methods=['POST'])

# Example request:
# curl -X POST http://127.0.0.1:5000/room/create -d "description=luxury" -d "price=3000"

def room_create():
    new_room = {
        "description": request.form.get('description'),
        "price": request.form.get('price')
    }
    try:
        cur.execute("INSERT INTO ROOMS (DESCRIPTION, PRICE) VALUES(%(description)s, %(price)s) RETURNING ROOM_ID",
                    new_room)
        last_row_id = {
            "room_id": cur.fetchone()[0]
        }
        conn.commit()
        return jsonify(last_row_id)
    except psycopg2.errors.InFailedSqlTransaction:
        cur.execute('rollback')
        return jsonify(f'Invalid request, try again')
    except psycopg2.errors.NotNullViolation:
        return jsonify(f'Invalid request. Example request: curl -X POST http://127.0.0.1:5000/room/create -d "description=luxury" -d "price=3000" ')
    except psycopg2.errors.InvalidTextRepresentation:
        return jsonify(f'Invalid data type entered')


@app.route('/room/<int:room_id>', methods=['DELETE'])
# Example request:
# curl -X DELETE http://127.0.0.1:5000/room/3

def room_delete(room_id):
    room = {"room_id": room_id}
    try:
        cur.execute("SELECT ROOM_ID FROM ROOMS")
        row = cur.fetchall()
        flag = False
        for x in row:
            if room_id in x:
                flag = True
                break
        if flag == True:
            cur.execute("DELETE from ROOMS where ROOM_ID=%(room_id)s", room)
            conn.commit()
            return jsonify(f'Room deleted. Bookings on this room deleted')
        else:
            return jsonify(f'There is no such room')
    except psycopg2.errors.InFailedSqlTransaction:
        cur.execute('rollback')
        return jsonify(f'Invalid request, try again')

@app.route('/bookings/list', methods=['GET'])
# Example request:
# curl -X GET http://127.0.0.1:5000/bookings/list?room_id=4
def get_booking_list():
    room = {"room_id": request.args.get("room_id")}
    cur.execute("SELECT * FROM BOOKINGS WHERE ROOM_ID=%(room_id)s ORDER BY DATA_START ASC", room)
    rows = cur.fetchall()
    booking_list = []
    for row in rows:
        room = {
            "booking_id": row[0],
            "data_start": row[2],
            "data_end": row[3]
        }
        booking_list.append(room)
    if not booking_list:
        return jsonify(f'this room is not booked')
    else:
        return jsonify(booking_list)


@app.route('/bookings/create', methods=['POST'])
# Example request:
# curl -X POST http://127.0.0.1:5000/bookings/create -d "room_id=10" -d "data_start=2020-01-01" -d "data_end=2020-05-01"

def booking_create():
    new_booking = {
        "room_id": request.form.get('room_id'),
        "data_start": request.form.get('data_start'),
        "data_end": request.form.get('data_end')
    }
    try:
        cur.execute(
            "INSERT INTO BOOKINGS (ROOM_ID, DATA_START, DATA_END) VALUES(%(room_id)s, %(data_start)s, %(data_end)s) RETURNING BOOKING_ID",
            new_booking)
        last_row_id = {
            "booking_id": cur.fetchone()[0]
        }
        conn.commit()
        return jsonify(last_row_id)
    except psycopg2.errors.InFailedSqlTransaction:
        cur.execute('rollback')
        return jsonify(f'Invalid request, try again')
    except psycopg2.errors.NotNullViolation:
        return jsonify(
            f'Invalid request. Example request: curl -X POST http://127.0.0.1:5000/bookings/create -d "room_id=10" -d "data_start=2020-01-01" -d "data_end=2020-05-01" ')
    except psycopg2.errors.InvalidTextRepresentation:
        return jsonify(f'Invalid data type entered')
    except psycopg2.errors.ForeignKeyViolation:
        return jsonify(f'There is no such room')


@app.route('/bookings/<int:booking_id>', methods=['DELETE'])
# Example request:
# curl -X DELETE http://127.0.0.1:5000/bookings/234

def booking_delete(booking_id):
    booking = {"booking_id": booking_id}
    try:
        cur.execute("SELECT BOOKING_ID FROM BOOKINGS")
        row = cur.fetchall()
        flag = False
        for x in row:
            if booking_id in x:
                flag = True
                break
        if flag == True:
            cur.execute("DELETE from BOOKINGS where BOOKING_ID=%(booking_id)s", booking)
            conn.commit()
            return f'Booking deleted'
        else:
            return jsonify(f'There is no such booking')
    except psycopg2.errors.InFailedSqlTransaction:
        cur.execute('rollback')
        return jsonify(f'Invalid request, try again')


if __name__ == '__main__':
    app.run(debug=True)

conn.close()