from sqlalchemy import create_engine
from sqlalchemy import text

engine = create_engine("postgresql://user:admin@localhost:5432/webdev")

with engine.connect() as conn:
    result = conn.execute(text("SELECT 'Hello World'"))
    print(result.all())


engine.dispose()

