# 3rd-devs: Kompletny Python Ecosystem dla AI

Pełny system integracji OpenAI API w Pythonie z 14 specjalizowanymi modułami.

## 📋 Spis Treści

1. [Struktura Projektu](#struktura-projektu)
2. [Instalacja](#instalacja)
3. [Moduły](#moduły)
4. [Szybki Start](#szybki-start)
5. [Konfiguracja](#konfiguracja)

---

## 🏗️ Struktura Projektu

```
3rd-devs/
├── database/          # Persistence & ORM
├── thread/            # Conversation management
├── completion/        # Task categorization
├── embedding/         # Vector search & RAG
├── chat/              # Conversational AI
├── streaming/         # SSE streaming
├── vision/            # Image processing
├── naive_rag/         # Basic RAG system
├── better_rag/        # Advanced RAG
├── tools/             # Function calling
├── agent/             # Autonomous agents
├── fine-tuning/       # Model training
└── requirements.txt   # Dependencies
```

---

## 🚀 Instalacja

### Wymagania
- Python 3.10+
- pip lub conda
- OpenAI API key
- (Opcjonalnie) Qdrant vector DB
- (Opcjonalnie) Firecrawl API key

### Krok 1: Clone repository

```bash
git clone https://github.com/grabowski-d/3rd-devs.git
cd 3rd-devs
```

### Krok 2: Utwórz virtual environment

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# lub
venv\Scripts\activate  # Windows
```

### Krok 3: Zainstaluj zależności

```bash
pip install -r requirements.txt
```

### Krok 4: Ustaw zmienne środowiskowe

```bash
cp .env.example .env
```

Wypełnij `.env`:

```env
# OpenAI
OPENAI_API_KEY=sk-...
OPENAI_ORG_ID=org-...

# Qdrant (opcjonalnie)
QDRANT_URL=http://localhost:6333
QDRANT_API_KEY=

# Firecrawl (opcjonalnie)
FIRECRAWL_API_KEY=

# Database
DATABASE_URL=sqlite:///db.sqlite3

# Langfuse (opcjonalnie)
LANGFUSE_PUBLIC_KEY=
LANGFUSE_SECRET_KEY=
```

---

## 📦 Moduły

### 1. **database** - SQLite ORM
- Persistence layer z SQLAlchemy
- Document storage
- Query interface

```python
from database.py.database_service import DatabaseService
db = DatabaseService()
await db.save_document(doc)
```

### 2. **thread** - Conversation Management
- Thread creation & management
- Conversation history
- Message summarization

```python
from thread.py.thread_service import ThreadService
thread = ThreadService()
await thread.create_thread(user_id)
```

### 3. **completion** - Task Categorization
- LLM-based task routing
- Intent detection
- Category assignment

```python
from completion.py.completion_service import CompletionService
completion = CompletionService()
await completion.categorize(text)
```

### 4. **embedding** - Vector Search
- Text embedding creation
- Vector similarity search
- Semantic retrieval

```python
from embedding.py.embedding_service import EmbeddingService
embed = EmbeddingService()
await embed.search(query)
```

### 5. **chat** - Conversational AI
- Multi-turn conversations
- Memory management
- Context preservation

```python
from chat.py.chat_service import ChatService
chat = ChatService()
await chat.send_message(message, thread_id)
```

### 6. **streaming** - SSE Streaming
- Server-Sent Events
- Real-time responses
- Stream management

```python
from streaming.py.streaming_service import StreamingService
stream = StreamingService()
async for chunk in stream.stream_completion(prompt):
    print(chunk)
```

### 7. **vision** - Image Processing
- Image analysis
- OCR support
- Token counting for images

```python
from vision.py.vision_service import VisionService
vision = VisionService()
await vision.analyze_image(image_url)
```

### 8. **naive_rag** - Basic RAG
- Vector embeddings
- Semantic search
- Document retrieval

```python
from naive_rag.py.rag_service import RAGService
rag = RAGService()
results = await rag.search(query)
```

### 9. **better_rag** - Advanced RAG
- Query expansion
- Result re-ranking
- Semantic similarity

```python
from better_rag.py.rag_service import BetterRAGService
rag = BetterRAGService(openai, vector)
results = await rag.search_with_expansion(query)
```

### 10. **tools** - Function Calling
- Multi-tool orchestration
- Function calling
- Tool execution

```python
from tools.py.assistant_service import AssistantService
assistant = AssistantService(config)
result = await assistant.process_request(message)
```

### 11. **agent** - Autonomous Agents
- Agent planning
- Web search integration
- Autonomous task execution

```python
from agent.py.agent_service import AgentService
agent = AgentService(state)
plan = await agent.plan()
```

### 12. **fine-tuning** - Model Training
- Data preparation
- Training job management
- Model evaluation

```python
from fine_tuning.py.training_service import TrainingService
training = TrainingService(config)
job_id = await training.start_training(training_file_id)
```

---

## ⚡ Szybki Start

### Przykład 1: Chat

```python
import asyncio
from chat.py.chat_service import ChatService

async def main():
    chat = ChatService()
    response = await chat.send_message(
        "Cześć, jak się masz?",
        thread_id="thread_123"
    )
    print(response)

asyncio.run(main())
```

### Przykład 2: Web Search Agent

```python
import asyncio
from agent.py.agent_service import AgentService
from agent.py.types import State

async def main():
    state = State(
        messages=[{
            'role': 'user',
            'content': 'Jakie są ostatnie trendy w AI?'
        }]
    )
    
    agent = AgentService(state)
    plan = await agent.plan()
    
    if plan:
        params = await agent.describe(plan['tool'], plan['query'])
        await agent.use_tool(plan['tool'], params, 'conv_123')
        answer = await agent.generate_answer()
        print(answer)

asyncio.run(main())
```

### Przykład 3: RAG Search

```python
import asyncio
from better_rag.py.rag_service import BetterRAGService
from better_rag.py.openai_service import OpenAIService
from better_rag.py.vector_service import VectorService

async def main():
    openai = OpenAIService()
    vector = VectorService(openai)
    rag = BetterRAGService(openai, vector)
    
    await vector.ensure_collection('documents')
    
    results = await rag.search_with_expansion(
        'documents',
        'Jak zacząć z machine learning?',
        limit=3
    )
    
    for result in results:
        print(f"- {result['payload']['text']}")

asyncio.run(main())
```

---

## ⚙️ Konfiguracja

### OpenAI API Key

```python
import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
```

### Qdrant Setup (opcjonalnie)

```bash
# Docker
docker run -p 6333:6333 qdrant/qdrant

# Lub lokalnie
qdrant-server
```

### Firecrawl Setup (opcjonalnie)

```bash
npm install -g @mendable/firecrawl
firecrawl serve
```

---

## 📚 Dokumentacja API

### OpenAIService

```python
from database.py.openai_service import OpenAIService

openai = OpenAIService()

# Embeddings
embedding = await openai.create_embedding(text)

# Completions
response = await openai.completion(
    messages=[...],
    model='gpt-4o',
    json_mode=True
)
```

### VectorService

```python
from embedding.py.vector_service import VectorService

vector = VectorService(openai_service)

# Ensure collection exists
await vector.ensure_collection('my_collection')

# Add points
await vector.add_points('my_collection', points)

# Search
results = await vector.perform_search('my_collection', query)
```

### DatabaseService

```python
from database.py.database_service import DatabaseService

db = DatabaseService()

# Save
await db.save_document(document)

# Query
docs = await db.query_documents(filters)

# Delete
await db.delete_document(doc_id)
```

---

## 🧪 Testing

```bash
# Run all tests
pytest

# With coverage
pytest --cov=.

# Specific module
pytest tests/test_chat.py -v
```

---

## 🐛 Troubleshooting

### "OpenAI API key not found"
```bash
export OPENAI_API_KEY=sk-...
```

### "Qdrant connection failed"
```bash
docker run -p 6333:6333 qdrant/qdrant
```

### "Firecrawl API error"
Upewnij się, że `FIRECRAWL_API_KEY` jest ustawiony w `.env`

---

## 📝 Licencja

MIT License - See LICENSE file

---

## 👤 Autor

[Darek Grabowski](https://github.com/grabowski-d)

---

## 🙏 Dziękuję za użytkowanie 3rd-devs!
