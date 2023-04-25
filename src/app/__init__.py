from .models import UsersTable, FilesTable

from .database import db_instance

db_instance.base.metadata.create_all(db_instance._engine)
print("Database created")
