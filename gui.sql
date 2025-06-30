-- Create a MindsDB engine for Groq
CREATE ML_ENGINE groq_engine
FROM groq
USING
      groq_api_key = "groq_api_key_here";  # Replace with your actual Groq API key

-- Create a MindsDB model for summarizing knowledge base content
CREATE MODEL kb_summarizer
PREDICT summary
USING
   engine = 'groq_engine',
   model_name = 'gemma2-9b-it',
   prompt_template = 'Summarize the following knowledge base content concisely and highlight key insights:\n\n{{kb_content}}\n\nSummary:';

-- Create a MindsDB connection to the PostgreSQL database with pgvector
CREATE DATABASE pvec
WITH
   ENGINE = 'pgvector',
   PARAMETERS = {
   "host": "pgvector",
   "port": 5432,
   "database": "ai",
   "user": "ai",
   "password": "ai",
   "distance": "cosine"
   };
