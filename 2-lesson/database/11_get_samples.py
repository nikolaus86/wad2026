with Session() as session:
    data = session.execute(select(User).order_by(User.id)).first() # => result.user.name, result.user.id
    # SELECT user.id, user.name FROM users ORDER BY user.id


with Session() as session:
    data = session.scalars(select(User).order_by(User.id)).first() # => result.name, result.id

with Session() as session:
    data = session.exec(select(User, Role).join(User.role)) # => result.User, result.Role
    # SELECT user.id, user.name, role.id, role.name FROM users JOIN roles ON users.role_id = roles.id



with Session() as session:
    data = session.execute(select(User.id, Role.name).join(User.role).order_by(User.name)).scalars()
    # => result.id, result.name
    # SELECT user.id, role.name FROM users JOIN roles ON users.role_id = roles.id ORDER BY user.name
    
select(User).filter(User.id == 1)
# SELECT user.id, user.name FROM users WHERE user.id = 1

select(User)
        .filter(User.id.in_([1, 2]))
        .filter(User.name.like("John%"))
# SELECT user.id, user.name FROM users WHERE user.id IN (1, 2) AND user.name LIKE 'John%'

from sqlalchemy import or_
select(User).filter(or_(User.id == 1, User.name like "John%"))
# SELECT user.id, user.name FROM users WHERE user.id = 1 OR user.name LIKE 'John%'



select(User).join(User.role)
select(User).join(Role, Role.id == User.role_id)
# SELECT user.id, user.name, role.id, role.name FROM users JOIN roles ON users.role_id = roles.id

select(User).join(User.role).join(Department, Department.id == User.department_id)
# SELECT user.id, user.name, role.id, role.name, department.id, department.name 
# FROM users JOIN roles ON users.role_id = roles.id JOIN departments ON users.department_id = departments.id


select(User).join(User.role.and_(Role.is_admin == True))
# SELECT user.id, user.name, role.id, role.name FROM users JOIN roles ON users.role_id = roles.id AND role.is_admin = TRUE



role_alias_1 = aliased(Role)
role_alias_2 = aliased(Role)

select(User)
        .join(role_alias_1, User.role)
            .where(role_alias_1.is_admin == True)
        .join(role_alias_2, User.role)
            .where(role_alias_2.is_staff == True)
# SELECT user.id, user.name, role_alias_1.id, role_alias_1.name, role_alias_2.id, role_alias_2.name 
# FROM users JOIN roles AS role_alias_1 ON users.role_id = role_alias_1.id AND role_alias_1.is_admin = TRUE 
# JOIN roles AS role_alias_2 ON users.role_id = role_alias_2.id AND role_alias_2.is_staff = TRUE


select(User).join(User.role).order_by(User.name)
# SELECT user.id, user.name, role.id, role.name FROM users JOIN roles ON users.role_id = roles.id ORDER BY user.name

select(User).join(User.role).order_by(User.name).limit(10)




sub_role = select(Role)
        .filter(Role.id == 1)
        .subquery()

select(User).join(sub_role, User.role_id == sub_role.id)
# SELECT user.id, user.name
# FROM users JOIN (SELECT roles.id, roles.name FROM roles WHERE roles.id = 1) AS anon_1 
# ON users.role_id = anon_1.id