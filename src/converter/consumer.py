import pika, sys, os, time
from pymongo import MongoClient
import gridfs
from convert import to_mp3 #package that we are going to create to convert video to mp3


def main():
    client = MongoClient("host.minikube.internal", 27017) 
    #MongoDB server runs on local machine, and the consumer service connects to it using the hostname host.minikube.internal.
    db_videos = client.videos #to interact with videos db using db_videos variable 
    db_mp3s = client.mp3s ##to interact with mp3s db using db_mp3s variable 
    #so these dbs will exist within out mongodb

    # gridfs
    fs_videos = gridfs.GridFS(db_videos)
    fs_mp3s = gridfs.GridFS(db_mp3s)

    # rabbitmq connection
    connection = pika.BlockingConnection(pika.ConnectionParameters(host="rabbitmq"))
    # RabbitMQ server runs within the Kubernetes cluster, and the consumer service connects to it using the hostname rabbitmq.
    channel = connection.channel()

    def callback(ch, method, properties, body): 
    #callback function is executed whenever a message is pulled from the RabbitMQ queue. It processes the message by converting the video to MP3 (calling the to_mp3.start function)and handles acknowledgment (basic_ack and basic_nack)based on whether the conversion was successful.
        err = to_mp3.start(body, fs_videos, fs_mp3s, ch) #when we get the message is we want to convert the video to MP3
        if err:
            ch.basic_nack(delivery_tag=method.delivery_tag)
        else:
            ch.basic_ack(delivery_tag=method.delivery_tag)

    #configuration to consume messages from the VIDEO_QUEUE. The queue name is retrieved from an environment variable.
    channel.basic_consume(
        queue=os.environ.get("VIDEO_QUEUE"), on_message_callback=callback #The consumer service starts listening for messages and processes them using the callback function. 
    )

    print("Waiting for messages. To exit press CTRL+C") #starts the consumer, which continuously listen for messages on the queue and process using callback function

    channel.start_consuming()

if __name__ == "__main__": 
    try: #consumer service runs until interrupted by the user. When interrupted, it gracefully shuts down the service.
        main()
    except KeyboardInterrupt:
        print("Interrupted")
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)

#this file contains core logic for consumer service, which processes messages from a RabbitMQ queue, converts video files to mp3 and interacts with mongodb
#p/s run mongodb on local to save resources within kubernetes cluster