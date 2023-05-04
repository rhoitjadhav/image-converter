from .models import FilesTable

from .database import db_instance

conn = db_instance._engine.connect()
conn.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')
db_instance.base.metadata.create_all(db_instance._engine)
print("Database created")
