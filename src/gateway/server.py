import os, gridfs, pika, json
from flask import Flask, request, send_file
from flask_pymongo import PyMongo
from auth import validate
from auth_svc import access
from storage import util
from bson.objectid import ObjectId
import logging

logging.basicConfig(level=logging.DEBUG)

server = Flask(__name__)

# Replace <db_password> with your actual MongoDB Atlas password
mongo_video = PyMongo(server, uri="mongodb+srv://syafiqahlukman:5hs2R5UcCMP3vHrB@cluster0.txb4s.mongodb.net/videos?retryWrites=true&w=majority&appName=Cluster0")
mongo_mp3 = PyMongo(server, uri="mongodb+srv://syafiqahlukman:5hs2R5UcCMP3vHrB@cluster0.txb4s.mongodb.net/mp3s?retryWrites=true&w=majority&appName=Cluster0")

fs_videos = gridfs.GridFS(mongo_video.db)
fs_mp3s = gridfs.GridFS(mongo_mp3.db)

connection = pika.BlockingConnection(pika.ConnectionParameters("rabbitmq"))
channel = connection.channel()

@server.route("/login", methods=["POST"])
def login():
    token, err = access.login(request)
    if not err:
        return token
    else:
        return err

@server.route("/upload", methods=["POST"])
def upload():
    access, err = validate.token(request)
    if err:
        logging.error(f"Token validation error: {err}")
        return err

    access = json.loads(access)
    logging.debug(f"Access: {access}")
    if access["admin"]:
        if len(request.files) > 1 or len(request.files) < 1:
            return "exactly 1 file required", 400

        for _, f in request.files.items():
            logging.debug("Attempting to upload file")
            err = util.upload(f, fs_videos, channel, access)
            if err:
                logging.error(f"Error during file upload: {err}")
                return err

        return "success!", 200
    else:
        return "not authorized", 401

@server.route("/download", methods=["GET"])
def download():
    access, err = validate.token(request)
    if err:
        return err

    access = json.loads(access)
    if access["admin"]:
        fid_string = request.args.get("fid")
        if not fid_string:
            return "fid is required", 400

        try:
            out = fs_mp3s.get(ObjectId(fid_string))
            return send_file(out, download_name=f"{fid_string}.mp3")
        except Exception as err:
            logging.error(err)
            return "internal server error", 500

    return "not authorized", 401

if __name__ == "__main__":
    server.run(host="0.0.0.0", port=8080)