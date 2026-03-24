import MySQLdb
from config import Config
from werkzeug.security import generate_password_hash, check_password_hash
import datetime

class Database:
    def __init__(self):
        self.host = Config.MYSQL_HOST
        self.user = Config.MYSQL_USER
        self.password = Config.MYSQL_PASSWORD
        self.db = Config.MYSQL_DB
    
    def get_connection(self):
        try:
            conn = MySQLdb.connect(
                host=self.host,
                user=self.user,
                passwd=self.password,
                db=self.db,
                charset='utf8mb4',
                use_unicode=True
            )
            return conn
        except MySQLdb.Error as e:
            print(f"Database connection error: {e}")
            return None
    
    # USER FUNCTIONS
    def register_user(self, username, email, password):
        """Register a new user"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            hashed_password = generate_password_hash(password)
            
            cursor.execute(
                "INSERT INTO users (username, email, password) VALUES (%s, %s, %s)",
                (username, email, hashed_password)
            )
            conn.commit()
            cursor.close()
            conn.close()
            return True
        except MySQLdb.IntegrityError:
            return False
    
    def login_user(self, username, password):
        """Verify user credentials"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("SELECT id, password FROM users WHERE username = %s", (username,))
            result = cursor.fetchone()
            cursor.close()
            conn.close()
            
            if result and check_password_hash(result[1], password):
                return result[0]  # Return user_id
            return None
        except MySQLdb.Error as e:
            print(f"Login error: {e}")
            return None
    
    def get_user_by_id(self, user_id):
        """Get user information"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor(MySQLdb.cursors.DictCursor)
            
            cursor.execute("SELECT id, username, email FROM users WHERE id = %s", (user_id,))
            result = cursor.fetchone()
            cursor.close()
            conn.close()
            
            return result
        except MySQLdb.Error as e:
            print(f"Error: {e}")
            return None
    
    # EMAIL FUNCTIONS
    def save_email(self, user_id, subject, body, recipient, email_type, tone):
        """Save generated email to database"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute(
                """INSERT INTO emails 
                   (user_id, subject, body, recipient, email_type, tone) 
                   VALUES (%s, %s, %s, %s, %s, %s)""",
                (user_id, subject, body, recipient, email_type, tone)
            )
            conn.commit()
            email_id = cursor.lastrowid
            cursor.close()
            conn.close()
            return email_id
        except MySQLdb.Error as e:
            print(f"Save email error: {e}")
            return None
    
    def get_email_history(self, user_id):
        """Get all emails for a user"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor(MySQLdb.cursors.DictCursor)
            
            cursor.execute(
                """SELECT id, subject, body, recipient, email_type, tone, created_at 
                   FROM emails WHERE user_id = %s 
                   ORDER BY created_at DESC""",
                (user_id,)
            )
            result = cursor.fetchall()
            cursor.close()
            conn.close()
            return result
        except MySQLdb.Error as e:
            print(f"Get history error: {e}")
            return []
    
    def delete_email(self, email_id, user_id):
        """Delete an email"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute(
                "DELETE FROM emails WHERE id = %s AND user_id = %s",
                (email_id, user_id)
            )
            conn.commit()
            cursor.close()
            conn.close()
            return True
        except MySQLdb.Error as e:
            print(f"Delete error: {e}")
            return False
    
    # API LOGGING FUNCTIONS
    def log_api_usage(self, user_id, tokens_used, response_time):
        """Log API usage"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute(
                "INSERT INTO api_logs (user_id, tokens_used, response_time) VALUES (%s, %s, %s)",
                (user_id, tokens_used, response_time)
            )
            conn.commit()
            cursor.close()
            conn.close()
        except MySQLdb.Error as e:
            print(f"Logging error: {e}")