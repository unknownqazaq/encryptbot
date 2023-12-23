# database_manager.py
import mysql.connector

class DatabaseManager:
    def __init__(self, host, user, password, database):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.connection = None
        self.cursor = None

    def connect(self):
        self.connection = mysql.connector.connect(
            host=self.host,
            user=self.user,
            password=self.password,
            database=self.database
        )
        self.cursor = self.connection.cursor()

    def disconnect(self):
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()

    def create_table(self):
        table_creation_query = """
            CREATE TABLE IF NOT EXISTS encrypted_data (
                id INT AUTO_INCREMENT PRIMARY KEY,
                encrypted_text TEXT,
                decrypted_text TEXT,
                encryption_key INT
            );
        """
        self.cursor.execute(table_creation_query)

    def insert_data(self, encrypted_text, decrypted_text, encryption_key):
        try:
            self.connect()  # Connect before executing the query
            insert_query = "INSERT INTO encrypted_data (encrypted_text, decrypted_text, encryption_key) VALUES (%s, %s, %s)"
            self.cursor.execute(insert_query, (encrypted_text, decrypted_text, encryption_key))
            self.connection.commit()
        except mysql.connector.Error as e:
            print(f"Error: {e}")
        finally:
            self.disconnect()  # Disconnect after the execution

    def fetch_data(self, encryption_key):
        try:
            self.connect()  # Connect before executing the query

            select_query = "SELECT encrypted_text FROM encrypted_data WHERE encryption_key = %s"
            self.cursor.execute(select_query, (encryption_key,))
            result = self.cursor.fetchone()

            return result
        except mysql.connector.Error as e:
            print(f"Error: {e}")
            return None
        finally:
            self.disconnect()  # Disconnect after the execution
