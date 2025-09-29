# Resume Evaluation System

A Flask-based API system that evaluates resumes against job descriptions using Google's Generative AI and LangChain. The system processes PDF resumes, extracts text, generates embeddings, and provides AI-powered scoring based on provided rubrics.

## 🚀 Features

- **AI-Powered Resume Evaluation**: Uses Google Generative AI (Gemini) to evaluate resumes
- **PDF Text Extraction**: Automatic text extraction from PDF resumes
- **Vector Embeddings**: Generate and store embeddings for semantic search
- **Asynchronous Processing**: Redis-based message queue for background processing
- **JWT Authentication**: Secure API endpoints with JWT tokens
- **RESTful API**: Clean REST API for integration
- **Bulk Operations**: Efficient bulk insertion of embedding data

## 🏗️ Architecture & Design Choices

### Overall Architecture

The system follows a **Clean Architecture** pattern with clear separation of concerns:

```
├── app/                    # Application layer (Controllers)
├── bootstrap/              # Application initialization
├── core/                   # Configuration and settings
├── usecases/              # Business logic layer
├── repositories/          # Data access layer
├── model/                 # Domain models
├── rag/                   # RAG (Retrieval-Augmented Generation) components
├── helpers/               # Utility functions
└── internal/              # Infrastructure components
```

### Key Design Decisions

#### 1. **Layered Architecture**

- **Controllers**: Handle HTTP requests/responses
- **Use Cases**: Business logic and orchestration
- **Repositories**: Data access abstraction
- **Models**: Domain entities and database schema

#### 2. **Asynchronous Processing**

- **Redis Streams**: Used for reliable message queuing
- **Background Workers**: Separate thread for processing evaluations
- **Non-blocking API**: Immediate response for long-running operations

#### 3. **AI/ML Integration**

- **Google Generative AI**: Chosen for its advanced capabilities and embedding models
- **LangChain**: Framework for building AI applications with modular components
- **Tiktoken**: Efficient tokenization for text processing
- **Backoff Strategy**: Retry mechanism for API rate limiting

#### 4. **Data Storage**

- **SQLite**: Lightweight database for development/small deployments
- **Vector Embeddings**: Stored as binary blobs with custom similarity functions
- **Indexing**: Optimized database indexes for performance

#### 5. **Security**

- **JWT Authentication**: Stateless authentication tokens
- **Bcrypt Password Hashing**: Secure password storage
- **Environment Variables**: Sensitive configuration externalized

#### 6. **Text Processing**

- **Recursive Character Text Splitter**: Intelligent text chunking
- **PDF Processing**: PyPDF for reliable text extraction
- **Text Normalization**: Unicode normalization for consistent processing

## 📋 Prerequisites

- Python 3.8+
- Redis server
- Google AI API key
- Docker
- Virtual environment (recommended)

## 🛠️ Installation & Setup

### 1. Clone the Repository

```bash
git clone <repository-url>
cd cv-evaluate-rag
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Environment Configuration

Copy the example environment file and configure:

```bash
cp .env.example .env
```

Edit `.env` with your configurations:

```bash
# Application Settings
APP_NAME="Resume Evaluator"
APP_VERSION=1.0.0
APP_PORT=8080
DEBUG=true

# Google AI
GOOGLE_API_KEY=your_google_ai_api_key_here
GOOGLE_LLM_MODEL=gemini-2.5-flash-lite
GOOGLE_EMBEDDING_MODEL=models/text-embedding-004

# Database
DATABASE_URL=sqlite:///./storage/app.db

# upload folder
UPLOAD_FOLDER="storage/files"

# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=
REDIS_DB=0
REDIS_STREAM_KEY=ingest_stream
REDIS_CONSUMER_GROUP=ingest_group

# Security
JWT_SECRET_KEY=your-secret-key-here
```

This will create the database tables and start the application.

## 🚀 Running the Application

### Using Docker Compose

```bash
docker-compose up -d
```

The application will be available at `http://localhost:8080`

## 📚 API Documentation

### Authentication Endpoints

#### Register User

```http
POST /auth/register
Content-Type: application/json

{
    "email": "user@example.com",
    "password": "securepassword"
}
```

#### Login

```http
POST /auth/login
Content-Type: application/json

{
    "email": "user@example.com",
    "password": "securepassword"
}
```

**Response:**

```json
{
  "access_token": "jwt_token_here"
}
```

### Evaluation Endpoints

All evaluation endpoints require JWT authentication. Include the token in the Authorization header:

```
Authorization: Bearer <jwt_token>
```

#### Upload Resume

```http
POST /api/upload
Content-Type: multipart/form-data
Authorization: Bearer <jwt_token>

title: "Software Engineer Position"
job_context: "Looking for a Python developer with 3+ years experience..."
rubric_context: "Rate based on technical skills, experience, education..."
file: <pdf_file>
```

**Response:**

```json
{
  "status": "uploaded",
  "id": "unique_id"
}
```

#### Start Evaluation

```http
POST /api/evaluate
Content-Type: application/json
Authorization: Bearer <jwt_token>

{
    "id": "unique_evaluation_id"
}
```

**Response:**

```json
{
  "id": "unique_id",
  "status": "queued"
}
```

#### Get Evaluation Result

```http
GET /api/result/<upload_id>
Authorization: Bearer <jwt_token>
```

**Response:**

```json
{
  "id": "fafe1442-7c41-4616-918f-41084be059fe",
  "result": {
    "cv_feedback": "The candidate's resume demonstrates foundational skills in digital marketing and performance marketing, particularly with Meta and Google Ads. However, it lacks depth and specific achievements related to the core responsibilities outlined in the job description, such as managing multi-million IDR budgets, driving NTB/NTP acquisition, developing advanced targeting strategies (behavioral, lookalike, segmentation), and optimizing for CPA/ROI at a strategic level. The experience is also very recent and short-term, not aligning with the 7+ years of experience required. More quantifiable results and details on strategic campaign planning and execution are needed.",
    "cv_match_rate": 0.3,
    "overall_summary": "The candidate possesses basic digital marketing skills but lacks the extensive experience, strategic depth, and quantifiable achievements required for a Digital Performance Marketing Lead role, particularly concerning budget management and advanced user acquisition strategies.",
    "project_score": 0.0
  },
  "status": "completed"
}
```

## 🔧 Configuration Options

### AI Models

- `GOOGLE_LLM_MODEL`: Gemini model for evaluation (gemini-2.5-flash-lite)
- `GOOGLE_EMBEDDING_MODEL`: Embedding model (models/text-embedding-004)

### Database

- `DATABASE_URL`: Database connection string (SQLite by default)

## 🐳 Docker Deployment

### Build Image

```bash
docker build -t resume-evaluator .
```

### Run Container

```bash
docker run -d \
  -p 8080:8080 \
  --env-file .env \
  resume-evaluator
```

### Docker Compose (Recommended)

```bash
docker-compose up -d
```

## 🧪 Testing

### Manual Testing

Use tools like Postman, curl, or HTTPie to test the API endpoints.

### Example curl commands:

```bash
# Register
curl -X POST http://localhost:8080/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}'

# Login
curl -X POST http://localhost:8080/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}'

# Upload (replace TOKEN with actual JWT)
curl -X POST http://localhost:8080/api/upload \
  -H "Authorization: Bearer TOKEN" \
  -F "title=Software Engineer" \
  -F "job_context=Python developer position" \
  -F "rubric_context=Rate technical skills" \
  -F "file=@resume.pdf"
```

## 🔍 Troubleshooting

### Common Issues

1. **Redis Connection Error**

   - Ensure Redis server is running
   - Check Redis host/port configuration

2. **Google AI API Error**

   - Verify API key is correct
   - Check API quotas and billing

3. **Database Issues**

   - Ensure storage directory exists
   - Check database file permissions

4. **Memory Issues**
   - Adjust chunk sizes for large documents
   - Monitor memory usage during processing

### Logs

Check application logs for detailed error information:

```bash
python app.py 2>&1 | tee app.log
```

## 📈 Performance Considerations

- **Chunking Strategy**: based on document sizes
- **Redis Memory**: Monitor Redis memory usage for large queues
- **Database Optimization**: Add indexes for frequent queries
- **Caching**: Consider caching embeddings for repeated evaluations

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the terms specified in the LICENCE file.

## 🔗 Related Documentation

- [Flask Documentation](https://flask.palletsprojects.com/)
- [LangChain Documentation](https://python.langchain.com/)
- [Google AI Documentation](https://ai.google.dev/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Redis Documentation](https://redis.io/documentation)
