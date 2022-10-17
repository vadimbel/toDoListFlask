
from flask import g
import sqlite3


def connect_db():
    sql = sqlite3.connect('C:\\Users\\vadim\\PycharmProjects\\ToDoList\\users.db')
    return sql


def get_db():
    g.sqlite_db = connect_db()
    return g.sqlite_db


def connect_db_notes():
    sql = sqlite3.connect('C:\\Users\\vadim\\PycharmProjects\\ToDoList\\notes.db')
    return sql


def get_db_notes():
    g.sqlite_db = connect_db_notes()
    return g.sqlite_db
