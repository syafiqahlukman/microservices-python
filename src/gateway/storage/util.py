import pika, json
import logging

logging.basicConfig(level=logging.DEBUG)

def upload(f, fs, channel, access):
    try:
        logging.debug("Attempting to upload file to GridFS")
        fid = fs.put(f)
        logging.debug(f"File uploaded to GridFS with id: {fid}")
    except Exception as err:
        logging.error(f"Error uploading file to GridFS: {err}")
        return "internal server error", 500

    message = {
        "video_fid": str(fid),
        "mp3_fid": None,
        "username": access["username"],
    }

    try:
        logging.debug("Attempting to publish message to RabbitMQ")
        channel.basic_publish(
            exchange="",
            routing_key="video",
            body=json.dumps(message),
            properties=pika.BasicProperties(
                delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE
            ),
        )
        logging.debug("Message published to RabbitMQ")
    except Exception as err:
        logging.error(f"Error publishing message to RabbitMQ: {err}")
        fs.delete(fid)
        return "internal server error", 500

    return "file uploaded successfully", 200