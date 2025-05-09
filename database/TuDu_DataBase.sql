-- ======= TuDu_DataBase =======
-------------------------------------------------------------------------------------------------------------------
-- PraxisprojektSQL: To Do Liste:  ===== TuDu_DataBase =====
-- Catarina, Laura, Jo
-- Beginn: 250507
-------------------------------------------------------------------------------------------------------------------

-- Erstellen der TuDu Database:
-- Copy/Paste folgende Codezeilen in ein anderes postgreSQL Skript: 
-- Verbinde mit TuDu DataBase,
-- Dann Run Skript

/* 

-- Beende alle Verbindungen zur Datenbank "TuDu", außer der eigenen Verbindung 
SELECT pg_terminate_backend(pid)
FROM pg_stat_activity
WHERE datname = 'TuDu'
  AND pid <> pg_backend_pid();


-- und jetzt die DataBase droppen::   
DROP DATABASE "TuDu";


-- die Datenbank "TuDu" erstellen:
CREATE DATABASE "TuDu";

*/

-----------------------------------------------------------------------------------------------------------------
-- User Table erstellen:
CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    "password" VARCHAR(255)
);

------------------------------------------------------------------------------------------------------------------
-- lists Tabelle erstellen:
-- Fremdschlüssel wird gleich mit erstellt mit REFERENCES users(user_id)
-- ON DELETE CASCADE bedeutet: 
-- wenn users gelöscht werden, werden alle Zeilen mit dieser user_id mitgelöscht
CREATE TABLE lists (
    list_id SERIAL PRIMARY KEY,
    list_name TEXT NOT NULL,
    user_id INTEGER REFERENCES users(user_id) ON DELETE CASCADE
);

------------------------------------------------------------------------------------------------------------------
-- tasks Tabelle erstellen:
CREATE TABLE tasks (
    task_id SERIAL PRIMARY KEY,
    task_name VARCHAR(255) NOT NULL,
    description VARCHAR(255),
    deadline TIMESTAMP,
    last_update TIMESTAMP DEFAULT CURRENT_TIME,
    priority SMALLINT CHECK (priority IN (1, 2, 3)),
    list_id INTEGER REFERENCES lists(list_id),
    user_id INTEGER REFERENCES users(user_id),
    completed BOOLEAN DEFAULT FALSE,
    repeat BOOLEAN DEFAULT FALSE,
    reminder TIMESTAMP DEFAULT NULL
);

-------------------------------------------------------------------------------------------------------------------
-- Beispieldaten einfügen:


-- Insert into users:
INSERT INTO users (first_name, last_name, email, "password")
VALUES 
	('Catarina', 'Boecker', 'cabo@gmail.com',1234),
	('Laura', 'Richter', 'lari@gmail.com',1234),
	('Aleksei', 'Assmus', 'alas@gmail.com',1234),
	('Jo', 'Jauch', 'joja@gmail.com',1234);


-- Insert into lists:
INSERT INTO lists (list_name, user_id)
VALUES 
	('Einkaufliste', 4),
	('Anrufliste', 4);


-- Insert into tasks:
INSERT INTO tasks 
    (task_name, description, deadline, last_update, priority, list_id, user_id, completed, repeat, reminder) 
VALUES
	('Einkaufen', 'Milch, Brot, Eier besorgen', '2025-05-08', CURRENT_DATE, 2, 1, 4, FALSE, FALSE, NULL),
	('Praxisprojekt SQL', 'Präsentation fertigstellen', '2025-05-14', CURRENT_DATE, 1, 2, 4, FALSE, FALSE, NULL),
	('Trinken', 'Trinken', '2025-05-07', CURRENT_DATE, 3, 2, 4, FALSE, TRUE, NULL),
	('Steuererklärung', 'Formulare ausfüllen und abgeben', '2025-06-01', CURRENT_DATE, 1, 2, 4, FALSE, FALSE, NULL),
	('Kita Termin vereinbaren', 'Generelles Update', '2025-05-07', CURRENT_DATE, 2, 2, 4, FALSE, FALSE, NULL);


-------------------------------------------------------------------------------------------------------------------

SELECT * FROM tasks;
SELECT * FROM users;
SELECT * FROM lists;

-------------------------------------------------------------------------------------------------------------------

-- Spalte hinzufügen:
-- ALTER TABLE users
-- ADD COLUMN password VARCHAR(255);

-- Spalte entfernen:
-- ALTER TABLE tasks
-- DROP COLUMN IF EXISTS reminder;

-- Spalte umbennen:
-- ALTER TABLE tasks
-- RENAME COLUMN reminder TO reminder_time;


--------------------------------------------------------------------------------------------------------------------
-- Trigger für last_update = NOW()
CREATE OR REPLACE FUNCTION last_update()
RETURNS TRIGGER AS $$
BEGIN 
	NEW.last_update = NOW();
	RETURN NEW;
END
$$ LANGUAGE plpgsql;

CREATE TRIGGER last_update_trigger
BEFORE UPDATE ON tasks
FOR EACH ROW
EXECUTE FUNCTION last_update();

---------------------------------------------------------------------------------------------------------------------





