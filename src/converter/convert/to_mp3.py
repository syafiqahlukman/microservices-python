import pika, json, tempfile, os
from bson.objectid import ObjectId # for working with MongoDB in Python.
import moviepy.editor


def start(message, fs_videos, fs_mp3s, channel):
    message = json.loads(message) #The message is being converted from JSON format to langauge that can be understand by the program

    # add empty temp file to hold the video contents
    tf = tempfile.NamedTemporaryFile()
   
    out = fs_videos.get(ObjectId(message["video_fid"])) #video file is retrieved from the fs_videos collection using its ObjectId.
    
    tf.write(out.read()) #The video contents are written to the temporary file.
   
    audio = moviepy.editor.VideoFileClip(tf.name).audio #The audio is extracted from the video file using moviepy.editor.
    tf.close() #twmp file is closed

    # write audio to a new temp file
    tf_path = tempfile.gettempdir() + f"/{message['video_fid']}.mp3"
    audio.write_audiofile(tf_path)

    # The MP3 file is read and saved to the fs_mp3s collection in MongoDB.
    f = open(tf_path, "rb")
    data = f.read()
    fid = fs_mp3s.put(data)
    f.close()
    os.remove(tf_path) #the temp mp3 file is removed

    message["mp3_fid"] = str(fid) #The file ID (mp3_fid) is added to the message.

    try: #The message is published to the MP3_QUEUE in RabbitMQ.
        channel.basic_publish(
            exchange="",
            routing_key=os.environ.get("MP3_QUEUE"),
            body=json.dumps(message),
            properties=pika.BasicProperties(
                delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE
            ),
        )
    except Exception as err: #If the message fails to publish, the file is deleted from the fs_mp3s collection in mongodb
        fs_mp3s.delete(fid)
        return "failed to publish message"

#this to_mp3.py is a function that processes a video file, extracts its audio, converts to mp3 format, and then saves it to mongodb 