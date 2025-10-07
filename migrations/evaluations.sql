CREATE TYPE evaluation_status AS ENUM ('queued', 'processing', 'completed');

CREATE TABLE IF NOT EXISTS evaluations (
	id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
	upload_id uuid NOT NULL,
	cv_match_rate FLOAT DEFAULT NULL,
	cv_feedback TEXT DEFAULT NULL,
	project_score FLOAT DEFAULT NULL,
	overall_summary TEXT DEFAULT NULL, 
	status evaluation_status,
	created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
	FOREIGN KEY (upload_id) REFERENCES uploads(id)
)

CREATE INDEX evaluations_id_idx ON evaluations (id);
CREATE INDEX evaluations_upload_id_idx ON evaluations (upload_id);
ALTER TYPE evaluation_status ADD VALUE 'uploaded' BEFORE 'queued';