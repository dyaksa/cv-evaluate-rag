CREATE TABLE IF NOT EXISTS uploads (
	id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
	title VARCHAR(100) not NULL,
	file_path TEXT not NULL,
	job_context TEXT not NULL,
	rubric_context TEXT NOT NULL,
	created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
CREATE INDEX uploads_id_idx ON uploads (id);