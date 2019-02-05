-- -----------------------------------------------------
-- Table for storing images sent from mobile app
-- -----------------------------------------------------
DROP TABLE IF EXISTS File CASCADE;

CREATE TABLE IF NOT EXISTS File (
  file_id SERIAL PRIMARY KEY NOT NULL,
  file bytea NOT NULL
);


-- -----------------------------------------------------
-- Table for storing the information about a user
-- -----------------------------------------------------
DROP TABLE IF EXISTS UserInfo;

CREATE TABLE IF NOT EXISTS UserInfo (
  email VARCHAR(255) PRIMARY KEY NOT NULL,
  password VARCHAR(255) NOT NULL,
  fiken_username VARCHAR(255) NOT NULL,
  fiken_password VARCHAR(255) NOT NULL,
  first_name VARCHAR(45) NOT NULL,
  last_name VARCHAR(45) NOT NULL
  );
