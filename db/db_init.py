import psycopg2
from werkzeug.security import generate_password_hash

from config import DevelopmentConfig

db_uri = DevelopmentConfig.DATABASE
conn = psycopg2.connect(db_uri)
c = conn.cursor()

c.execute("DROP TABLE IF EXISTS member CASCADE")
c.execute("DROP TABLE IF EXISTS author CASCADE")
c.execute("DROP TABLE IF EXISTS warehouse CASCADE")
c.execute("DROP TABLE IF EXISTS book CASCADE")
c.execute("DROP TABLE IF EXISTS warehouse_book")
c.execute("DROP TABLE IF EXISTS rental CASCADE")
c.execute("DROP TABLE IF EXISTS rental_book")

c.execute("""CREATE TABLE member(
                    email           VARCHAR(254) PRIMARY KEY,
                    name            TEXT NOT NULL,
                    password        TEXT NOT NULL,
                    age             INTEGER NOT NULL,
                    phone_number    TEXT
)""")

c.execute("""CREATE TABLE author(
                    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    name            TEXT NOT NULL,
                    biography       TEXT
)""")

c.execute("""CREATE TABLE warehouse(
                    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    name            TEXT NOT NULL,
                    address         TEXT NOT NULL
)""")

c.execute("""CREATE TABLE book(
                    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    title           TEXT NOT NULL,
                    year_published  INTEGER NOT NULL,
                    author_id       UUID,
                    FOREIGN KEY(author_id) REFERENCES author(id) ON DELETE CASCADE
)""")

c.execute("""CREATE TABLE warehouse_book(
                    warehouse_id    UUID NOT NULL,
                    book_id         UUID NOT NULL,
                    quantity        INTEGER,
                    PRIMARY KEY (warehouse_id, book_id),
                    FOREIGN KEY(book_id) REFERENCES book(id) ON DELETE CASCADE,
                    FOREIGN KEY(warehouse_id) REFERENCES warehouse(id) ON DELETE CASCADE
)""")

c.execute("""CREATE TABLE rental (
                    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    borrow_date     DATE,
                    return_date     DATE,
                    member_id       TEXT NOT NULL, 
                    FOREIGN KEY(member_id) REFERENCES member(email)
)""")

c.execute("""CREATE TABLE rental_book (
                    rental_id       UUID NOT NULL,
                    book_id         UUID NOT NULL,
                    PRIMARY KEY (rental_id, book_id), 
                    FOREIGN KEY(rental_id) REFERENCES rental(id),
                    FOREIGN KEY(book_id) REFERENCES book(id)
)""")

members = [
    ("admin@example.com", "Admin", generate_password_hash("admin"), 25, "111-111-1111")
]
c.executemany("INSERT INTO member (email, name, password, age, phone_number) VALUES (%s,%s,%s,%s,%s)", members)

authors = [
    ("Franz Kafka", "(3 July 1883 – 3 June 1924) Was an Austrian-Czech novelist and writer from Prague, "
                    "widely regarded as a major figure of 20th-century literature."),
    ("Ivo Andric", "(9 October 1892 – 13 March 1975) Was a Yugoslav novelist, poet and short story writer "
                   "who won the Nobel Prize in Literature in 1961."),
    ("J. R. R. Tolkien", "(3 January 1892 – 2 September 1973) Was an English writer and philologist. "
                         "He was the author of the high fantasy works The Hobbit and The Lord of the Rings.")
]
c.executemany("INSERT INTO author (name, biography) VALUES (%s,%s)", authors)

warehouses = [
    ("Main warehouse", "Some street 1/1 City 1, Country 1"),
    ("Small warehouse", "Some other street 2/5 City 2, Country 1")
]
c.executemany("INSERT INTO warehouse (name, address) VALUES (%s,%s)", warehouses)

conn.commit()
conn.close()

print("Database is created.")
print("Data for test admin member, authors and warehouses initialized.")
print("You can now proceed with creating books and making rentals.")
