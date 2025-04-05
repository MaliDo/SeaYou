import sqlite3
from tkinter.messagebox import NO

def query(query_text, *param):
    conn = sqlite3.connect('seayou.db')
    cur = conn.cursor()
    cur.execute(query_text, param)

    column_names = []
    for column in cur.description:
        column_names.append(column[0])

    rows = cur.fetchall()
    dicts = []

    for row in rows:
        d = dict(zip(column_names, row))
        dicts.append(d)

    conn.close()
    return dicts

def get_offers():
    return query('''SELECT 
                Offers.OfferDateTime,
                Offers.PortDeparture,
                Offers.DateDeparture,
                Offers.Days,
                Offers.Pax,
                Offers.Price,
                Offers.Picture,
                Users.Username,
                Users.FirstName,
                Users.LastName,
                L.LikeCount
                from Offers
                INNER JOIN Users
                on offers.UserId = Users.UserId
                LEFT JOIN 
                (SELECT OfferId, count(userid) as LikeCount FROM likes GROUP by OfferId) L
                on offers.OfferId = L.OfferId''')

def get_users():
    return query('''SELECT * FROM Users''')

def get_client_by_username(Username):
    conn = sqlite3.connect('seayou.db')
    cur = conn.cursor()
    cur.execute("SELECT * FROM Users WHERE USERNAME = ?", [Username])
    column_names = []
    for column in cur.description:
        column_names.append(column[0])
    dicts = []
    for row in cur:
        d = dict(zip(column_names, row))
        dicts.append(d)
    if len(dicts) > 0:
        return dicts[0]
    else:
        return None

def create_user(first_name, last_name, username, dob, email, password_hash, bio, profile_picture):
    query('''
        INSERT INTO USERS
        ([Username], [FirstName], [LastName], [Email], [PasswordHash], [DoB], [Bio], [ProfilePicture])
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', username, first_name, last_name, email, password_hash, dob, bio, profile_picture, fetch=False)


def create_offer(username, port_departure, port_arrival, date_departure, days, pax, price, picture):
    conn = sqlite3.connect('seayou.db')
    cur = conn.cursor()

    # Get UserId from username
    cur.execute("SELECT UserId FROM Users WHERE Username = ?", (username,))
    user_row = cur.fetchone()
    if not user_row:
        conn.close()
        raise Exception("User not found.")

    user_id = user_row[0]

    # Insert offer
    cur.execute('''
        INSERT INTO Offers (
            OfferDateTime,
            UserId,
            PortDeparture,
            PortArrival,
            DateDeparture,
            Days,
            Pax,
            Price,
            Picture
        ) VALUES (
            datetime('now'), ?, ?, ?, ?, ?, ?, ?, ?
        )
    ''', (user_id, port_departure, port_arrival, date_departure, days, pax, price, picture))

    conn.commit()
    conn.close()
    
def get_user_id(username):
    conn = sqlite3.connect('seayou.db')
    cur = conn.cursor()
    cur.execute("SELECT UserId FROM Users WHERE Username = ?", (username,))
    row = cur.fetchone()
    conn.close()
    return row[0] if row else None

def user_liked_offer(user_id, offer_id):
    conn = sqlite3.connect('seayou.db')
    cur = conn.cursor()
    cur.execute("SELECT 1 FROM Likes WHERE UserId = ? AND OfferId = ?", (user_id, offer_id))
    result = cur.fetchone()
    conn.close()
    return result is not None

def like_offer(user_id, offer_id):
    conn = sqlite3.connect('seayou.db')
    cur = conn.cursor()
    cur.execute("INSERT INTO Likes (OfferId, UserId) VALUES (?, ?)", (offer_id, user_id))
    conn.commit()
    conn.close()

def unlike_offer(user_id, offer_id):
    conn = sqlite3.connect('seayou.db')
    cur = conn.cursor()
    cur.execute("DELETE FROM Likes WHERE OfferId = ? AND UserId = ?", (offer_id, user_id))
    conn.commit()
    conn.close()

def get_offers_for_user(user_id):
    conn = sqlite3.connect('seayou.db')
    cur = conn.cursor()
    cur.execute('''
        SELECT 
            Offers.OfferId,
            Offers.OfferDateTime,
            Offers.PortDeparture,
            Offers.DateDeparture,
            Offers.Days,
            Offers.Pax,
            Offers.Price,
            Offers.Picture,
            Users.Username,
            Users.FirstName,
            Users.LastName,
            L.LikeCount,
            CASE WHEN UL.UserId IS NOT NULL THEN 1 ELSE 0 END AS LikedByUser
        FROM Offers
        INNER JOIN Users ON Offers.UserId = Users.UserId
        LEFT JOIN (
            SELECT OfferId, COUNT(UserId) AS LikeCount
            FROM Likes
            GROUP BY OfferId
        ) L ON Offers.OfferId = L.OfferId
        LEFT JOIN (
            SELECT OfferId, UserId FROM Likes WHERE UserId = ?
        ) UL ON Offers.OfferId = UL.OfferId
    ''', (user_id,))
    column_names = [desc[0] for desc in cur.description]
    rows = cur.fetchall()
    conn.close()
    return [dict(zip(column_names, row)) for row in rows]

def count_likes(offer_id):
    conn = sqlite3.connect('seayou.db')
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM Likes WHERE OfferId = ?", (offer_id,))
    result = cur.fetchone()
    conn.close()
    return result[0] if result else 0