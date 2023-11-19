# thing
from flask import Flask, request, Response
import sys
from sentence_transformers import SentenceTransformer
sys.path.append("model/")
from model import Model
from json import dumps
import dotenv
import jwt
from uuid import uuid4
import redis
import os
import psycopg2
import redis


dotenv.load_dotenv()
app = Flask(__name__)
transformer = SentenceTransformer("all-MiniLM-L6-v2")
maxAllowedCache = 100

@app.route("/")
def hello():
    return "hello"

@app.route("/sign_up", methods=["POST"])
async def sign_up():
    email = request.json["email"]
    password = request.json["password"]
    conn = psycopg2.connect(database="postgres",
                        host="34.31.33.98",
                        user="postgres",
                        password="IsbgVhMCgVDuV4")
    cursor = conn.cursor()
    uid = -1
    valid = False
    try:
        cursor.execute(f"INSERT INTO \"User\" (email, password) VALUES ('{email}', '{password}')")
        conn.commit()
        cursor.execute(f"SELECT id FROM \"User\" WHERE email='{email}'")
        #fetched = fetched[0][1:len(fetched[0]) - 1].split(",")
        uid = cursor.fetchone()[0]
        valid = True
    finally:
        conn.close()

    if (valid):
        encoded = jwt.encode({ "id": uid}, os.getenv("JWT_SECRET"))
        return dumps({
            'jwt': encoded
        })
    else:
        return dumps({
            "error": "user already exists"
        }), 400

@app.route("/login", methods=["POST"])
async def login():
    email = request.json["email"]
    password = request.json["password"]
    user_pw = ""
    conn = psycopg2.connect(database="postgres",
                        host="34.31.33.98",
                        user="postgres",
                        password="IsbgVhMCgVDuV4")
    cursor = conn.cursor()
    fetched = False
    uid = -1
    try:
        cursor.execute(f"SELECT (id, password) FROM \"User\" WHERE email='{request.json['email']}'")
        fetched = cursor.fetchone()
        fetched = fetched[0][1:len(fetched[0]) - 1].split(",")
        user_pw = fetched[1]
        uid = fetched[0]
        fetched = True
    finally:
        conn.close()

    if (fetched and user_pw == password):
        encoded = jwt.encode({ "id": uid }, os.getenv("JWT_SECRET"), algorithm="HS256")
        return dumps({
            'jwt': encoded
        })
    elif (not fetched):
        return dumps({
            'error': 'user not found'
        }), 405
    else:
        return dumps({
            "error": "password not correct"
        }), 400

@app.route("/get_api_keys", methods=["POST"])
async def get_api_keys():
    encoded = request.json["jwt"]
    decoded = jwt.decode(encoded, os.getenv("JWT_SECRET"), algorithms=["HS256"])
    conn = psycopg2.connect(database="postgres",
                        host="34.31.33.98",
                        user="postgres",
                        password="IsbgVhMCgVDuV4")
    cursor = conn.cursor()
    keys = []
    try:
        cursor.execute("SELECT guid FROM \"ApiKeys\" WHERE \"userId\" = '" + decoded["id"] + "'")
        keys = cursor.fetchall()
    finally:
        conn.close()
    return dumps({
        "keys": [key[0] for key in keys]
    })

@app.route("/add_api_key", methods=["POST"])
async def add_api_key():
    encoded = request.json["jwt"]
    decoded = jwt.decode(encoded, os.getenv("JWT_SECRET"), algorithms=["HS256"])
    conn = psycopg2.connect(database="postgres",
                        host="34.31.33.98",
                        user="postgres",
                        password="IsbgVhMCgVDuV4")
    cursor = conn.cursor()
    keys = []
    try:
        guid = str(uuid4())
        cursor.execute(f"INSERT INTO \"ApiKeys\" (guid, \"userId\") VALUES ('{guid}', {decoded['id']})")
        conn.commit()
        cursor.execute("SELECT guid FROM \"ApiKeys\" WHERE \"userId\" = " + decoded["id"])
        keys = cursor.fetchall()
    finally:
        conn.close()
    return dumps({
        "keys": [key[0] for key in keys]
    })

@app.route("/delete_api_key", methods=["POST"])
async def delete_api_key():
    encoded = request.json["jwt"]
    decoded = jwt.decode(encoded, os.getenv("JWT_SECRET"), algorithms=["HS256"])
    conn = psycopg2.connect(database="postgres",
                        host="34.31.33.98",
                        user="postgres",
                        password="IsbgVhMCgVDuV4")
    cursor = conn.cursor()
    keys = []
    try:
        cursor.execute("SELECT \"userId\" FROM \"ApiKeys\" WHERE guid = '" + request.json["key"] + "'")
        uid = cursor.fetchone()[0]
        decoded["id"] = int(decoded["id"])
        if (uid == decoded["id"]):
            cursor.execute("DELETE FROM \"ApiKeys\" WHERE guid = '" + request.json["key"] + "'")
            conn.commit()
            cursor.execute("SELECT guid FROM \"ApiKeys\" WHERE \"userId\" = " + str(decoded["id"]))
            keys = cursor.fetchall()
        else:
            return dumps({
                "error": "Cannot delete key for another user"
            }), 400
    finally:
        conn.close()
    return dumps({
        "keys": [key[0] for key  in keys]
    })


@app.route("/get_intent", methods=["POST"])
def get_intent():
    encoded = request.json["jwt"]
    decoded = jwt.decode(encoded, os.getenv("JWT_SECRET"), algorithms=["HS256"])
    model = Model(request.json["prompt"], model=transformer)
    out = model()
    return dumps({
        "certaintyValue": out
    })


if (__name__ == "__main__"):
    app.run(port=3000)