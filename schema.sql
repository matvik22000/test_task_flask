create table tasks (
    id serial primary key,
    email char(50),
    name char(50),
    description text,
    redacted boolean,
    completed boolean
);
create table users (
    username char(50) primary key,
    password char(50),
    is_admin boolean

);

insert into users (username, password, is_admin) VALUES ('123', 'test', true);

insert into tasks (email, name, description, completed)
 VALUES ('test@mail.ru', 'test_user1', 'task 1', false),
        ('test@mail.ru', 'test_user1', 'task 2', false),
        ('test2@mail.ru', 'test_user2', 'task 132312', false)