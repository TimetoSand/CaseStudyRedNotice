import os
import pika
import requests
import sqlite3
from queue import Queue
import json
from datetime import datetime



class listenQueueAndComparing:
    def __init__(self):
        self.queue = Queue()
        try:
            self.channel = self.connect_to_rabbitmq()
        except Exception as e:
            print(f"Failed to connect to RabbitMQ: {e}")
            self.channel = None

        if self.channel is not None:
            self.listenQueue()

    def connect_to_rabbitmq(self):
        host = os.getenv('RABBITMQ_HOST')
        port = int(os.getenv('RABBITMQ_PORT'))
        username = os.getenv('RABBITMQ_USERNAME')
        password = os.getenv('RABBITMQ_PASSWORD')
        virtual_host = os.getenv('RABBITMQ_VIRTUAL_HOST')

        credentials = pika.PlainCredentials(username, password)
        parameters = pika.ConnectionParameters(host, port, virtual_host, credentials)
        
        try:
            connection = pika.BlockingConnection(parameters)
        except pika.exceptions.AMQPConnectionError as e:
            print(f"Failed to connect to RabbitMQ in function: {e}")
            return None
        
        return connection.channel()

    def listenQueue(self): # consume data
        queue_name = os.getenv('RABBITMQ_QUEUE_NAME')
        try:
            self.channel.basic_consume(queue_name, on_message_callback=self.callback, auto_ack=True)
            self.channel.start_consuming()
        except Exception as e:
            print(f"Failed to consume from queue: {e}")

    def callback(self, ch, method, properties, body): # consume data
        try:
            self.queue.put(json.loads(body))
        except Exception as e:
            print(f"Failed to process message: {e}")

    def createDB(self):
        db_connection = sqlite3.connect('my_database.db')
        cursor = db_connection.cursor()
        # Create a table in your database if it doesn't exist
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY,
        name TEXT,
        age TEXT,
        nationality TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''') 
        db_connection.commit()

        while True:
            try:
                message = self.queue.get()
                # Insert the message into the database
                cursor.execute('INSERT INTO messages (name, age, nationality) VALUES (?, ?, ?)', 
                            (message['name'], message['age'], message['nationality']))
                db_connection.commit()
            except Exception as e:
                print(f"Failed to get message from queue: {e}")


    def create_delta_table(self):
        # Create a new database connection
        db_connection = sqlite3.connect('my_database.db')
        delta_cursor = db_connection.cursor()

        # Create a new table in your delta database if it doesn't exist
        delta_cursor.execute('''
        CREATE TABLE IF NOT EXISTS delta_messages (
            id INTEGER PRIMARY KEY,
            name TEXT,
            age TEXT,
            nationality TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        ''')

        db_connection.commit()
    
    def compare(self):
        db_connection = sqlite3.connect('my_database.db')
        cursor = db_connection.cursor()

        cursor.execute("SELECT * FROM messages")
        messages = cursor.fetchall()

        cursor.execute("SELECT * FROM delta_messages")
        delta_messages = cursor.fetchall()

        # Find records that are in 'messages' but not in 'delta_messages' (deleted data)
        deleted_data = [message for message in messages if message not in delta_messages]

        # Find records that are in 'delta_messages' but not in 'messages' (added data)
        added_data = [message for message in delta_messages if message not in messages]

        # Send alerts for deleted and added data
        requests.post('http://127.0.0.1:5000/deleted_alert', json={'deleted_data': deleted_data})
        requests.post('http://127.0.0.1:5000/added_alert', json={'added_data': added_data})

        # Update the 'messages' table with the current content of the 'delta_messages' table
        cursor.execute('DELETE FROM messages')  # Remove all existing records
        cursor.executemany('INSERT INTO messages VALUES (?, ?, ?, ?, ?)', delta_messages)  # Insert new records

        # Commit changes and close the connection
        db_connection.commit()
        db_connection.close()



