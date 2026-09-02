CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS documents (
    id SERIAL PRIMARY KEY,
    filename TEXT NOT NULL,
    department TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS document_chunks (
    id SERIAL PRIMARY KEY,
    document_id INTEGER NOT NULL
        REFERENCES documents(id)
        ON DELETE CASCADE,

    content TEXT NOT NULL,
    page_number INTEGER,
    chunk_index INTEGER NOT NULL,

    embedding vector(1536),

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);