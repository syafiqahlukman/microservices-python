import pika, json #pika is python library for interacting with RabbitMQ, json is python library for JSON

#The upload function takes a file object, stores it in mongodb db using gridfs db, sends message through RabbitMQ channel, and an access object to know information about who is uploading the file as arguments
def upload(f, fs, channel, access): 
    try:
        fid = fs.put(f) #tries to upload the file in the mongodb using gridfs, if the put successful, it returns the fid,(unique id of the file)
    except Exception as err:
        print(err)
        return "internal server error", 500

    message = { #message that we want to put in the queue. the message equal to dictionary with the fid of the file, the username (came from access from auth service) of the user who uploaded the file, and the mp3_fid set to None which is empty for now
        "video_fid": str(fid),
        "mp3_fid": None,
        "username": access["username"],
    }

    try: #the function tries to put the message to the RabbitMQ queue
        channel.basic_publish( #if it works, the function publishes the message to the RabbitMQ server with the message dictionary as the body
            exchange="", #use default exchange
            routing_key="video",
            body=json.dumps(message),
            properties=pika.BasicProperties(
                delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE
            ),
        )
    except Exception as err: #if something goes wrong, the function prints the error and deletes the file from the GridFS storage system (db)
        print(err)
        fs.delete(fid)
        return "internal server error", 500
