import uvicorn
from fastapi import FastAPI
from model import SentimentModel
import mysql.connector

app = FastAPI()
model = SentimentModel()

# Connect to the MySQL database
def connect_to_database():
    try:
        connection = mysql.connector.connect(
            host='db',  # Docker service name for the database container
            port='3306',  # Port exposed by the database container
            user='mlusername',
            password='mlpassword',
            database='mldb'
        )
        return connection
    except mysql.connector.Error as err:
        print("Error:", err)
        return None

# Insert data into a table
def create_table(connection):
    try:
        cursor = connection.cursor()
        create_table_query = """
        CREATE TABLE IF NOT EXISTS mldb.ml_results (
            id INT AUTO_INCREMENT PRIMARY KEY,
            Input VARCHAR(255),
            Sentiment VARCHAR(255)
        )
        """
        cursor.execute(create_table_query)
        connection.commit()
        print("Table Created successfully.")
    except mysql.connector.Error as err:
        print("Error:", err)

# Insert data into a table
def insert_data(connection, data):
    try:
        cursor = connection.cursor()
        sql = "INSERT INTO mldb.ml_results (Input, Sentiment) VALUES (%s, %s)"
        cursor.execute(sql, data)
        connection.commit()
        print("Data inserted successfully.")
    except mysql.connector.Error as err:
        print("Error:", err)

@app.post('/predict')
def predict(input_sentence):
    polarity, subjectivity, result = model.get_sentiment_analysis(input_sentence)
    # Connect to the database
    db_connection = connect_to_database()

    if db_connection:
        # Sample data to insert
        data_to_insert = (input_sentence, result)

        # create Table
        create_table(db_connection)

        # Insert data into the database
        insert_data(db_connection, data_to_insert)

        # Close the database connection
        db_connection.close()
    else:
        print("Failed to connect to the database.")

    return { 'Sentiment': result
    }


if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8000)