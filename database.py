import mysql.connector
from mysql.connector import Error

class Database:
    def __init__(self):
        self.host = "localhost"
        self.user = "root"
        self.password = ""
        self.database = "travel_agency"
        self.connection = None

    def connect(self):
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database
            )
            if self.connection.is_connected():
                print("Conexión exitosa a la base de datos")
                return True
        except Error as e:
            print(f"Error al conectar a la base de datos: {e}")
            return False

    def disconnect(self):
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("Conexión cerrada")

    def execute_query(self, query, params=None):
        try:
            cursor = self.connection.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            self.connection.commit()
            return cursor
        except Error as e:
            print(f"Error al ejecutar la consulta: {e}")
            return None

    def fetch_all(self, query, params=None):
        cursor = self.execute_query(query, params)
        if cursor:
            result = cursor.fetchall()
            cursor.close()
            return result
        return None

    def fetch_one(self, query, params=None):
        cursor = self.execute_query(query, params)
        if cursor:
            result = cursor.fetchone()
            cursor.close()
            return result
        return None

    def insert(self, query, params=None):
        cursor = self.execute_query(query, params)
        if cursor:
            inserted_id = cursor.lastrowid
            cursor.close()
            return inserted_id
        return None

    def initialize_database(self):
        """Inicializa la base de datos con las tablas necesarias"""
        queries = [
            """
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS destinations (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                description TEXT,
                price DECIMAL(10,2) NOT NULL,
                image_url VARCHAR(255),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS bookings (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT,
                destination_id INT,
                start_date DATE NOT NULL,
                end_date DATE NOT NULL,
                passengers INT NOT NULL,
                total_price DECIMAL(10,2) NOT NULL,
                status VARCHAR(20) DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (destination_id) REFERENCES destinations(id)
            )
            """
        ]

        for query in queries:
            self.execute_query(query)

    def seed_sample_data(self):
        """Inserta datos de ejemplo en la base de datos"""
        destinations = [
            ("Cancún, México", "Disfruta de las mejores playas del Caribe", 1299.99, "/static/img/cancun.jpg"),
            ("París, Francia", "La ciudad del amor y la luz", 1499.99, "/static/img/paris.jpg"),
            ("Tokio, Japón", "Una mezcla única de tradición y modernidad", 1799.99, "/static/img/tokyo.jpg"),
            ("Roma, Italia", "Historia, arte y gastronomía excepcional", 1399.99, "/static/img/roma.jpg")
        ]

        query = """
        INSERT INTO destinations (name, description, price, image_url)
        VALUES (%s, %s, %s, %s)
        """

        for destination in destinations:
            self.execute_query(query, destination)

if __name__ == "__main__":
    db = Database()
    if db.connect():
        db.initialize_database()
        db.seed_sample_data()
        db.disconnect()