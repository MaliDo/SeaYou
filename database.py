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