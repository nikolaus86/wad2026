from sqlalchemy import insert
session.execute(insert(User), [{"name": "John"}, {"name": "Jane"}])
# INSERT INTO users (name) VALUES (?, ?) [(John), (Jane)]


session.execute(insert(User).values(role_id=1), [{"name": "John"}, {"name": "Jane"}])
# INSERT INTO users (name, role_id) VALUES (?, 1), (?, 1) [(John), (Jane)]

session.execute(insert(User),
    [
        {"name": "John", role_id: select(Role.id).filter(Role.name == "admin")}
    ],
)
# INSERT INTO users (name, role_id) VALUES 
#(?, (SELECT roles.id FROM roles WHERE roles.name = 'admin'))
#["(John)"]



from sqlalchemy import update
session.execute(update(User), {"id": 1, "name": "John"}, ["id": 2, "name": "Jane"])
# UPDATE users SET name = ? WHERE id = ? [('John', 1), ('Jane', 2)]


from sqlalchemy import bindparam
session.execute(update(User).where(User.name == bindparam("old_name")),
 [{"old_name": "John", "name": "John1"}, {"old_name": "Jane", "name": "Jane1"}])
# UPDATE users SET name = ? WHERE name = ? [('John1', 'John'), ('Jane1', 'Jane')]


from sqlalchemy import delete
session.execute(delete(User).where(User.role_id == 1))
# DELETE FROM users WHERE role_id = 1

session.execute(delete(User).where(User.role_id == select(Role.id).filter(Role.name == "admin")))
# DELETE FROM users WHERE role_id = (SELECT roles.id FROM roles WHERE roles.name = 'admin')


from sqlalchemy import text
session.execute(text("UPDATE users SET name = :name WHERE id = :id"), {"name": "John", "id": 1})
# UPDATE users SET name = 'John' WHERE id = 1

session.execute(text("SELECT * FROM users WHERE role_id = 2")).fetchall()
# SELECT * FROM users WHERE role_id = 2

session.execute(text("DELETE FROM users WHERE id = :id"), {"id": 1})
# DELETE FROM users WHERE id = 1

session.execute(text("DELETE FROM users WHERE id = :id"), {"id": 1})
# DELETE FROM users WHERE id = 1
