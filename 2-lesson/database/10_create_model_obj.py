from sqlalchemy import MetaData
from sqlalchemy.orm import declarative_base

Base = declarative_base(Metadata())

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]

Session = sessionmaker()

with Session() as session:
    user = User(name="John")
    # Bind object to session, now stored in the database
    session.add(user)
    # Generate primary key, send to database, but it's not saved yet
    session.flush()
    # Commit
    session.commit()


