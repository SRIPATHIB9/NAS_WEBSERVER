import os
from dotenv import load_dotenv

# Load environment variables from .env file (optional)
load_dotenv()

# MySQL Database Configuration
MYSQL_HOST = os.getenv('MYSQL_HOST', 'localhost')
MYSQL_USER = os.getenv('MYSQL_USER', 'root')
MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD', 'yourpassword')  # Change this securely!
MYSQL_DB = os.getenv('MYSQL_DB', 'nas_server')

# Upload/Backup Folders
UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'uploads')
BACKUP_FOLDER = os.getenv('BACKUP_FOLDER', 'backups')

# Max file size (optional)
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max upload size
