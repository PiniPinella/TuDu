
-----------------------------------------------------------------------------------------------------------
-- Praxisprojekt TuDu-Liste 
-- Catarina, Laura, Aleksej, Jo
-- Beginn: 250507
-----------------------------------------------------------------------------------------------------------

-- Erstellt die Datenbank "TuDu"
CREATE DATABASE "TuDu";

-- Falls man die DB nochmal droppen muss:
DROP DATABASE "TuDu";

-- Beende alle Verbindungen zur Datenbank "TuDu", außer der eigenen Verbindung
SELECT pg_terminate_backend(pid)
FROM pg_stat_activity
WHERE datname = 'TuDu'
  AND pid <> pg_backend_pid();



------------------------------------------------------------------------------------------
-- tasks Tabelle erstellen:
CREATE TABLE tasks (
    task_id SERIAL PRIMARY KEY,
    task_name VARCHAR(255) NOT NULL,
    description VARCHAR(255),
    deadline DATE,
    last_update DATE DEFAULT CURRENT_DATE,
    priority SMALLINT CHECK (priority IN (1, 2, 3)),
    category_id INTEGER,
    user_id INTEGER,
    completed BOOLEAN DEFAULT FALSE,
    repeat BOOLEAN DEFAULT FALSE
);

SELECT * FROM tasks;


-----------------------------------------------------------------------------------------
-- User Table erstellen:
CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL
);

SELECT * FROM users;

-- Fremdschlüssel in tasks setzen:
ALTER TABLE tasks
ADD CONSTRAINT fk_user
FOREIGN KEY (user_id)
REFERENCES users(user_id);


-----------------------------------------------------------------------------------------
-- category Table erstellen:
CREATE TABLE category (
    category_id SERIAL PRIMARY KEY,
    category_name VARCHAR(100) NOT NULL
);

SELECT * FROM category;


-- und Fremdschlüssel definieren
ALTER TABLE tasks
ADD CONSTRAINT fk_category
FOREIGN KEY (category_id)
REFERENCES category(category_id);


-----------------------------------------------------------------------------------------
-- lists Tabelle erstellen:
-- Fremdschlüssel wird gleich mit erstellt mit REFERENCES users(user_id)
-- ON DELETE CASCADE bedeutet: wenn users gelöscht werden, werden alle Zeilen mit dieser user_id mitgelöscht
CREATE TABLE lists (
    list_id SERIAL PRIMARY KEY,
    list_name TEXT NOT NULL,
    user_id INTEGER REFERENCES users(user_id) ON DELETE CASCADE
);

SELECT * FROM lists;


-- Neue Spalte list_id in category einfügen:
ALTER TABLE category
ADD COLUMN list_id INTEGER;


-- und Fremdschlüssel definieren:
ALTER TABLE category
ADD CONSTRAINT fk_list
FOREIGN KEY (list_id)
REFERENCES lists(list_id) ON DELETE CASCADE;


------------------------------------------------------------------------------------------------------------
-- Beispieldaten einfügen:

SELECT * FROM tasks;
SELECT * FROM users;
SELECT * FROM category;
SELECT * FROM lists;


-- Insert into users:
INSERT INTO users (first_name, last_name, email)
VALUES 
	('Catarina', 'Boecker', 'cabo@gmail.com'),
	('Laura', 'Richter', 'lari@gmail.com'),
	('Aleksei', 'Assmus', 'alas@gmail.com'),
	('Jo', 'Jauch', 'joja@gmail.com');

SELECT user_id, first_name, last_name FROM users;


-- Insert into Categories:
INSERT INTO category (category_name)
VALUES 
	('family'),
	('official'),
	('today'),
	('personel'),
	('official'),
	('hobby'),
	('contact');


-- Insert into tasks:
INSERT INTO tasks 
    (task_name, description, deadline, last_update, priority, category_id, user_id, completed, repeat) 
VALUES
	('Einkaufen', 'Milch, Brot, Eier besorgen', '2025-05-08', CURRENT_DATE, 2, 1, 4, FALSE, FALSE),
	('Praxisprojekt SQL', 'Präsentation fertigstellen', '2025-05-14', CURRENT_DATE, 1, 2, 4, FALSE, FALSE),
	('Trinken', 'Trinken', '2025-05-07', CURRENT_DATE, 3, 3, 4, FALSE, TRUE),
	('Steuererklärung', 'Formulare ausfüllen und abgeben', '2025-06-01', CURRENT_DATE, 1, 4, 4, FALSE, FALSE),
	('Kita Termin vereinbaren', 'Generelles Update', '2025-05-07', CURRENT_DATE, 2, 2, 4, FALSE, FALSE);


-- Insert into lists:
INSERT INTO lists (list_name, user_id)
VALUES 
	('Einkaufliste', 4),
	('Anrufliste', 4);













