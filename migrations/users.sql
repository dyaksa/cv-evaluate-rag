CREATE TABLE IF NOT EXISTS users(
	id uuid primary key default uuid_generate_v4(),
	email VARCHAR(100) not NULL,
	password VARCHAR(255) NOT NULL,
	created_at TIMESTAMP default CURRENT_TIMESTAMP
);

CREATE INDEX users_id_idx ON users (id);
CREATE INDEX users_email_idx ON users (email);
