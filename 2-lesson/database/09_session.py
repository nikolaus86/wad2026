# Without autocommit
engine = create_engine("postgresql+asyncpg://user:admin@localhost:5432/webdev")
Session = sessionmaker(engine)
with Session() as session:
    session.add(some_object)
    session.commit()

# Session with autocommit
engine = create_engine("postgresql+asyncpg://user:admin@localhost:5432/webdev").execution_options(isolation_level="AUTOCOMMIT")
Session = sessionmaker(engine)
with Session() as session:
    session.add(some_object)


    