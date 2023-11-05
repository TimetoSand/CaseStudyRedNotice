from flask import Flask, request, render_template
import pika
import sqlite3
import threading
from flask import jsonify
import json
import compare_data
from dotenv import set_key
import os


app = Flask(__name__)

@app.route('/', methods=['POST'])
def home(): # publish all database
    conn = sqlite3.connect('my_database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM messages')
    data = cursor.fetchall()
    return render_template('index.html', data=data)

@app.route('/deleted_alert', methods=['POST'])
def delete_alert(): 
    raw_data = request.json
    data = raw_data['deleted_data']
    data['Update_Type'] = 'deleted_data'
    
    # Open a connection to the database
    db_connection = sqlite3.connect('my_database.db')
    cursor = db_connection.cursor()

    # Delete the data from the database
    cursor.execute('DELETE FROM messages WHERE name=? AND age=? AND nationality=?', (data['name'], data['age'], data['nationality']))
    db_connection.commit()
    db_connection.close()

    return {'status': 'Deleted data received and removed from database'}


@app.route('/added_alert', methods=['POST'])
def added_alert(): # publish added data
    raw_data = request.json
    data = raw_data['added_data']
    data['Update_Type'] = 'added_data'
    
    # Open a connection to the database
    db_connection = sqlite3.connect('my_database.db')
    cursor = db_connection.cursor()

    # Insert the added data into the database
    cursor.execute('INSERT INTO messages (name, age, nationality) VALUES (?, ?, ?)', (data['name'], data['age'], data['nationality']))
    db_connection.commit()
    db_connection.close()

    return {'status': 'Added data received and saved to database'}

if __name__ == "__main__":
    db_status = os.getenv('IS_DB_CREATED')
    
    listener = compare_data.listenQueueAndComparing()
    
    listener.listenQueue()
    
    if db_status == "false": #run without compare if the project is running for the first time
        listener.createDB()
        set_key('.env', 'IS_DB_CREATED', "true")
        
    listener.create_delta_table()
    
    app.run(host='0.0.0.0', port=5000)


    

    