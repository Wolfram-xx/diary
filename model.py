import datetime
import os

import bcrypt
import psycopg2
from dotenv import load_dotenv
from flask_login import UserMixin

load_dotenv()
class User(UserMixin):
    def __init__(self, id_, login_):
        self.id = id_
        self.login = login_

class DB:
    def __init__(self):
        try:
            self.conn = psycopg2.connect(dbname=os.getenv('DB_NAME'), user=os.getenv('DB_USER'), password=os.getenv('DB_PASSWORD'), host=os.getenv('DB_HOST'), port=os.getenv('DB_PORT'))
        except Exception as e:
            print(f'Can`t establish connection to database:\n{e}')
        cur = self.conn.cursor()
        cur.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                login TEXT UNIQUE NOT NULL,
                hash_pass TEXT NOT NULL
            );
        ''')

        cur.execute('''
            CREATE TABLE IF NOT EXISTS notes (
                id SERIAL PRIMARY KEY,
                title TEXT NOT NULL,
                description TEXT,
                owner INTEGER REFERENCES users(id),
                date TIMESTAMP WITHOUT TIME ZONE,
                status TEXT DEFAULT 'inwork'
            );
        ''')
        self.conn.commit()
        cur.close()

    def add_user(self, login, hash_pass):
        cur = self.conn.cursor()
        cur.execute(f"INSERT INTO users (login, hash_pass) VALUES (%s, %s) RETURNING id", (login, hash_pass))
        user_id = cur.fetchone()[0]
        self.conn.commit()
        cur.close()
        return user_id

    def get_user_by_login(self, login):
        cur = self.conn.cursor()
        cur.execute(f"SELECT id, login, hash_pass FROM users WHERE login=%s", (login, ))
        user_data = cur.fetchone()
        cur.close()
        return user_data

    def get_user_by_id(self, id):
        cur = self.conn.cursor()
        cur.execute(f"SELECT id, login FROM users WHERE id=%s", (id,))
        login = cur.fetchone()
        cur.close()
        return login

    def add_note(self, description, owner, title):
        cur = self.conn.cursor()
        cur.execute("INSERT INTO notes (title, description, owner, date) VALUES (%s, %s, %s, %s)", (title, description, owner, datetime.datetime.now()))
        self.conn.commit()
        cur.close()

    def get_all_users(self):
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM users")
        users = cur.fetchall()
        cur.close()
        return users

    def get_notes_by_owner(self, id):
        cur = self.conn.cursor()
        cur.execute("SELECT id, title, description, owner, TO_CHAR(date, 'DD.MM') as formatted_time, status FROM notes WHERE owner=%s", (id, ))
        notes = cur.fetchall()
        cur.close()
        return notes

    def get_note_by_id(self, id):
        cur = self.conn.cursor()
        cur.execute("SELECT id, title, description, owner, TO_CHAR(date, 'DD.MM') as formatted_time, status FROM notes WHERE id=%s", (id, ))
        note = cur.fetchone()
        cur.close()
        return note

    def edit_note(self, id, title, descritption):
        cur = self.conn.cursor()
        cur.execute("UPDATE notes SET title=%s, description=%s WHERE id=%s", (title, descritption, id))
        self.conn.commit()
        cur.close()

    def delnote(self, id):
        cur = self.conn.cursor()
        cur.execute("DELETE FROM notes WHERE id=%s", (id, ))
        self.conn.commit()
        cur.close()

    def setnotestatus(self, id, new_status):
        cur = self.conn.cursor()
        cur.execute('UPDATE notes SET status=%s WHERE id=%s', (new_status, id))
        self.conn.commit()
        cur.close()


if __name__ == "__main__":
    db = DB()
    a = int(input())
    match a:
        case 1:
            name = input("Name: ")
            passw = input("Password: ")
            db.add_user(name, bcrypt.hashpw(passw.encode(), bcrypt.gensalt()).decode())
            db.conn.close()

        case 2:
            title = input("Title: ")
            description = input("Descript: ")
            users = db.get_all_users()
            print(users)
            user = int(input("ID: "))
            for i in users:
                if user in i:
                    db.add_note(description, user, title)