# thing
from flask import Flask, request, Response
import sys
from sentence_transformers import SentenceTransformer
sys.path.append("model/")
from model import Model
from prisma import Prisma
from json import dumps
import dotenv
import jwt
from uuid import uuid4
import redis
import os


dotenv.load_dotenv()
app = Flask(__name__)
transformer = SentenceTransformer("all-MiniLM-L6-v2")
prisma = Prisma()
r = redis.Redis(
  host='redis-16537.c10.us-east-1-2.ec2.cloud.redislabs.com',
  port=16537,
  password=os.getenv("REDIS_PW"))
maxAllowedCache = 100

@app.route("/")
def hello():
    return "redis back up"

@app.route("/sign_up", methods=["POST"])
async def sign_up():
    email = request.json["email"]
    password = request.json["password"]
    await prisma.connect()
    user = None
    try:
        user = await prisma.user.create(
            data={
                'email': email,
                'password': password
            }
        )
    finally:
        await prisma.disconnect()

    if (user != None):
        encoded = jwt.encode({ "id": user.id }, os.getenv("JWT_SECRET"))
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
    await prisma.connect()
    user = None
    try:
        user = await prisma.user.find_unique_or_raise(where={
                'email': email,
            })
    finally:
        await prisma.disconnect()

    if (user != None and user.password == password):
        encoded = jwt.encode({ "id": user.id }, os.getenv("JWT_SECRET"), algorithm="HS256")
        return dumps({
            'jwt': encoded
        })
    elif (user == None):
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
    await prisma.connect()
    keys = []
    try:
        keys = await prisma.apikeys.find_many(where={
            "userId": decoded["id"]
        })
    finally:
        await prisma.disconnect()
    return dumps({
        "keys": [key.guid for key in keys]
    })

@app.route("/add_api_key", methods=["POST"])
async def add_api_key():
    encoded = request.json["jwt"]
    decoded = jwt.decode(encoded, os.getenv("JWT_SECRET"), algorithms=["HS256"])
    await prisma.connect()
    keys = []
    try:
        await prisma.apikeys.create(
            data={
                "guid": str(uuid4()),
                "userId": decoded["id"]
            }
        )
        keys = await prisma.apikeys.find_many(where={
            "userId": decoded["id"]
        })
    finally:
        await prisma.disconnect()
    return dumps({
        "keys": [key.guid for key  in keys]
    })

@app.route("/delete_api_key", methods=["POST"])
async def delete_api_key():
    encoded = request.json["jwt"]
    decoded = jwt.decode(encoded, os.getenv("JWT_SECRET"), algorithms=["HS256"])
    await prisma.connect()
    keys = []
    try:
        key = await prisma.apikeys.delete(
            where={
                "guid": request.json["key"]
            }
        )

        if (key.userId == decoded["id"]):
            await prisma.apikeys.delete(
                where={
                    "guid": request.json["key"]
                }
            )
            keys = await prisma.apikeys.find_many(where={
                "userId": decoded["id"]
            })
        else:
            return dumps({
                "error": "Cannot delete key for another user"
            })
    finally:
        await prisma.disconnect()
    return dumps({
        "keys": [key.guid for key  in keys]
    })


@app.route("/get_intent", methods=["POST"])
def get_intent():
    # encoded = request.json["jwt"]
    # decoded = jwt.decode(encoded, os.getenv("JWT_SECRET"), algorithms=["HS256"])
    model = Model(request.json["prompt"], model=transformer)
    try:
        out = r.get(model.hash())
        if out != None:
            return dumps({
                "certaintyValue": out
            })
        if r.dbsize() >= maxAllowedCache:
            r.delete(next(r.scan()))
        r.set(model.hash(), out)
    finally:
        out = model()
        return dumps({
            "certaintyValue": out[0]
        })


if (__name__ == "__main__"):
    app.run(port=3000)