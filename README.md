# Laptop Intelligence Engine

A comprehensive laptop comparison and recommendation system built with AI-powered insights, specification analysis, and intelligent recommendations based on user reviews and technical specifications.

## 🏗️ Architecture Overview

- **Frontend**: Next.js React application with TypeScript
- **Backend API**: FastAPI with PostgreSQL database
- **AI Service**: LangGraph agent with vector search capabilities
- **Database**: PostgreSQL with ChromaDB for vector storage
- **Deployment**: Docker containerized services

## 📋 Features

- **Laptop Catalog**: Compare 4 professional laptops (Lenovo ThinkPad E14 Gen 5, HP ProBook series)
- **AI-Powered Chat**: Natural language queries about laptops
- **Smart Recommendations**: Personalized suggestions based on requirements
- **Price Tracking**: Historical price trends and availability monitoring (Not Developed)
- **Review Intelligence**: Semantic search through user reviews and Q&A
- **Detailed Specifications**: Technical specs extracted from official PDFs

## 🚀 Quick Start (Demo Mode)

For a quick demo using pre-populated data:

### Prerequisites

- Docker and Docker Compose installed
- Git installed
- OpenAI API key

### 1. Clone Repository

```bash
git clone https://github.com/HimashaRandil/laptop-intelligence-engine.git
cd laptop-intelligence-engine
```

### 2. Environment Setup

Create a `.env` file in the project root:

```bash
# Database Configuration
DB_USER=myuser
DB_PASSWORD=mysecretpassword
DB_NAME=laptops_db

# AI Configuration
OPENAI_API_KEY=your-actual-openai-key-here
DEFAULT_MODEL=gpt-4
TEMPERATURE=0.1
```

### 3. Start All Services

```bash
# Build and start all services
docker-compose up --build

# Or run in background
docker-compose up --build -d
```

### 4. Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000/docs
- **AI Service**: http://localhost:8001/ai/docs
- **Database**: localhost:5432

### 5. Test the AI Chat

```bash
curl -X POST "http://localhost:8001/ai/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "What laptops are under $1000?"}'
```

## 🔧 Development Setup

### Local Development (Without Docker)

#### Backend Setup

```bash
# Install dependencies
pip install -e .

# Set environment variables
export DATABASE_URL="postgresql://myuser:mysecretpassword@localhost:5432/laptops_db"
export OPENAI_API_KEY="your-key-here"

# Start backend
python -m backend.src.app.main
```

#### AI Service Setup

```bash
# Start AI service
python -m ai_services.src.main
```

#### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Create .env.local
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local
echo "NEXT_PUBLIC_AI_API_URL=http://localhost:8001" >> .env.local

# Start frontend
npm run dev
```

## 📊 Database Setup

### Option 1: Use Pre-populated Data (Recommended)

The docker-compose setup automatically loads a database backup with sample data.

### Option 2: Full Data Pipeline

To rebuild all data from scratch:

```bash
# 1. Start database
docker-compose up db -d

# 2. Run PDF extraction
python -m scripts.ingest_data
python -m scripts.structure_data #LLM would structure data into predefined formats
python -m scripts.consolidated_specs #Preprocessing on the database

# 3. Run web scraping (Most of the scrapers does not work due to anti-bot manuvers)
# Strongly recommend against runing these scripts due to ToS from the product websites
python -m scripts.lenovo_scraper 
python -m scripts.integrated_scraper 

# 3.a Insted run this sample data uploader 
python -m scripts.database_reset_script
python -m  scripts.sample_data_loader


# 4. Index vector database
python backend/scripts/index_vector_data.py
```

## 🎯 API Endpoints

### Backend API (Port 8000)

- `GET /laptops` - List all laptops
- `GET /laptops/{id}` - Detailed laptop information
- `GET /laptops/{id}/specifications` - Laptop specifications
- `GET /laptops/{id}/reviews` - Customer reviews
- `GET /laptops/{id}/questions` - Q&A data
- `GET /laptops/compare?ids=1,2,3` - Compare multiple laptops

### AI Service (Port 8001)

- `POST /ai/chat` - General chat with AI assistant
- `POST /ai/recommend` - Get laptop recommendations
- `GET /ai/health` - Service health check

## 🤖 AI Features

### Chat Examples

```bash
# Budget queries
curl -X POST "http://localhost:8001/ai/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "Show me laptops under $1200"}'

# Specification queries
curl -X POST "http://localhost:8001/ai/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "I need a laptop with Intel i7 processor"}'

# Experience-based queries
curl -X POST "http://localhost:8001/ai/recommend" \
  -H "Content-Type: application/json" \
  -d '{"message": "Best laptop for programming work"}'
```

### AI Capabilities

- **Natural Language Processing**: Understands complex queries about laptop features
- **Vector Search**: Semantic search through reviews and Q&A content
- **Contextual Recommendations**: Suggestions based on use cases and preferences
- **Multi-tool Orchestration**: Combines database queries with vector search
- **Citation Support**: Responses include references to source data (Not implemneted in the UI)

## 🐳 Docker Deployment

### Local Deployment

```bash
# Build and start all services
docker-compose up --build

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Cloud Deployment (AWS EC2)

1. **Launch EC2 Instance** (t3.medium recommended)
2. **Install Docker**:
   ```bash
   sudo apt update && sudo apt upgrade -y
   sudo apt install -y docker.io docker-compose
   sudo usermod -aG docker $USER
   ```
3. **Clone and Deploy**:
   ```bash
   git clone https://github.com/your-username/laptop-intelligence-engine.git
   cd laptop-intelligence-engine
   
   # Create .env file with your configuration
   docker-compose up --build -d
   ```
4. **Configure Security Groups** for ports 3000, 8000, 8001

## 📁 Project Structure

```
laptop-intelligence-engine/
├── backend/                  # FastAPI backend service
│   ├── src/app/
│   │   ├── models/          # SQLAlchemy database models
│   │   ├── schemas/         # Pydantic schemas
│   │   ├── core/            # Database configuration
│   │   └── main.py          # FastAPI application
│   ├── scripts/             # Index Vector Script
│   └── Dockerfile
├── ai_services/             # AI service with LangGraph
│   ├── src/
│   │   ├── services/        # AI agent and tools
│   │   ├── core/            # Configuration and database
│   │   └── main.py          # FastAPI AI service
│   └── Dockerfile
├── frontend/                # Next.js React frontend
│   ├── src/components/      # React components
│   ├── lib/                 # API utilities and types
│   └── Dockerfile
├── data/                    # Data storage
│   ├── processed/           # Database backups
│   └── vector_db/           # ChromaDB storage
├── docker-compose.yml       # Service orchestration
└── pyproject.toml          # Python dependencies
```

## 🔍 Troubleshooting

### Common Issues

1. **CORS Errors**: Ensure frontend environment variables point to correct backend URLs
2. **Database Connection**: Verify PostgreSQL is running and credentials are correct
3. **AI Service Startup**: Check OpenAI API key is set and vector database initializes
4. **Port Conflicts**: Ensure ports 3000, 8000, 8001, 5432 are available

### Debug Commands

```bash
# Check service health
curl http://localhost:8000/health
curl http://localhost:8001/ai/health

# View container logs
docker logs laptop_backend
docker logs laptop_ai
docker logs laptop_frontend

# Check database
docker exec laptop_db psql -U myuser -d laptops_db -c "SELECT COUNT(*) FROM laptops;"
```

### Performance Tuning

- **Memory**: AI service requires ~2GB RAM for vector operations
- **Storage**: Vector database needs ~500MB for indexed reviews
- **CPU**: LLM calls may take 3-10 seconds depending on complexity

## 🧪 Testing

### API Testing

```bash
# Test backend endpoints
curl http://localhost:8000/laptops
curl http://localhost:8000/laptops/1

# Test AI service
curl -X POST "http://localhost:8001/ai/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello"}'
```

### Frontend Testing

```bash
cd frontend
npm run test
npm run build  # Test production build
```

## 📈 Monitoring

### Health Checks

All services include health check endpoints:
- Backend: `GET /health`
- AI Service: `GET /ai/health`
- Database: Built into Docker Compose

### Logging

Services log to:
- Console output (viewable with `docker-compose logs`)
- Local files in `./logs/` directory

## 🔒 Security Considerations

- Store API keys in environment variables, never in code
- Use strong database passwords
- Configure proper CORS origins for production
- Regular dependency updates via `pip update` and `npm audit`

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For issues and questions:
1. Check the troubleshooting section above
2. Review container logs for error details
3. Ensure all environment variables are set correctly
4. Verify Docker and dependencies are properly installed

## 🎯 Assignment Requirements Met

This project demonstrates:
- **Data Pipeline**: PDF extraction
- **Database Design**: Comprehensive schema with relationships
- **API Development**: RESTful endpoints with documentation
- **AI Integration**: LLM-powered chat and recommendations
- **Frontend Development**: Interactive user interface
- **DevOps**: Containerization and cloud deployment
- **Documentation**: Comprehensive setup and usage guides