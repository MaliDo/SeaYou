from datetime import datetime, date

offer1 = {
    'Name' : 'Harry',
    'Username' : 'hpotter',
    'Departure' : 'Split, Croatia',
    'StartDate' : date(2022, 6, 10),
    'EndDate' : date(2022, 6, 20),
    'Passengers' : 10,
    'Likes' : 3,
    'Picture' : 'offer1.jpg',
    'OfferDate' : datetime(2022, 4, 9, 13, 48, 0, 0)
}

offer2 = {
    'Name' : 'Ron',
    'Username' : 'rweasley',
    'Departure' : 'Rhodes, Greece',
    'StartDate' : date(2022, 7, 1),
    'EndDate' : date(2022, 7, 20),
    'Passengers' : 15,
    'Likes' : 0,
    'Picture' : 'offer2.jpeg',
    'OfferDate' : datetime(2022, 4, 6, 9, 32, 0, 0)
}

offer3 = {
    'Name' : 'Hermione',
    'Username' : 'hgranger',
    'Departure' : 'Limassol, Cyprus',
    'StartDate' : date(2022, 8, 10),
    'EndDate' : date(2022, 8, 20),
    'Passengers' : 10,
    'Likes' : 4,
    'Picture' : 'offer3.jpg',
    'OfferDate' : datetime(2022, 4, 1, 20, 24, 0, 0)
}

offers = [offer1, offer2, offer3]