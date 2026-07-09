from app import create_app
from app.extensions import db
from app.models import User

app = create_app()

with app.app_context():
    print("Tables known to SQLAlchemy:")
    print(db.metadata.tables.keys())

    db.create_all()

    print("Tables created!")