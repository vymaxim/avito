import psycopg2

DB_NAME = "avito"
DB_USER = "postgres"
DB_PASS = "admin"
DB_HOST = "localhost"
DB_PORT = "5432"

connect = psycopg2.connect(
    database=DB_NAME,
    user=DB_USER,
    password=DB_PASS,
    host=DB_HOST,
    port=DB_PORT
)

cur = connect.cursor()
cur.execute('''CREATE TABLE IF NOT EXISTS ROOMS
     (ROOM_ID BIGSERIAL PRIMARY KEY NOT NULL,
     DESCRIPTION TEXT NOT NULL,
     PRICE INT NOT NULL,
     DATA_CREATE DATE NOT NULL);''')

cur.execute('''CREATE TABLE IF NOT EXISTS BOOKINGS
     (BOOKING_ID BIGSERIAL PRIMARY KEY NOT NULL,
     ROOM_ID INT NOT NULL,
     DATA_START DATE NOT NULL,
     DATA_END DATE NOT NULL,
     FOREIGN KEY (ROOM_ID) REFERENCES ROOMS (ROOM_ID) ON DELETE CASCADE);''')


connect.commit()