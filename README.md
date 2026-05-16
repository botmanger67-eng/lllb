# TaskMaster - Efficient Task Management Application

A modern web application demonstrating efficient task management using Python, Flask, SQLAlchemy, and responsive HTML/CSS.

## Features

- **Create Tasks**: Add new tasks with title, description, priority, and due date
- **Task Management**: Update, complete, and delete tasks
- **Priority Levels**: High, Medium, Low priority categorization
- **Search & Filter**: Find tasks by title, status, or priority
- **Responsive Design**: Works seamlessly on desktop and mobile devices
- **RESTful API**: Full CRUD operations with JSON endpoints
- **Database Persistence**: SQLite database with SQLAlchemy ORM

## Tech Stack

- **Backend**: Python 3.9+, Flask 2.3+
- **Database**: SQLAlchemy 2.0 with SQLite
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **Testing**: pytest, coverage
- **Deployment**: Gunicorn, Docker support

## Prerequisites

- Python 3.9 or higher
- pip (Python package manager)
- Virtual environment (recommended)
- Git (for version control)

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/taskmaster.git
cd taskmaster
```

### 2. Create Virtual Environment

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the project root:

```env
FLASK_APP=run.py
FLASK_ENV=development
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///taskmaster.db
```

### 5. Initialize Database

```bash
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

### 6. Run the Application

**Development Server:**
```bash
flask run
```

**Production Server (using Gunicorn):**
```bash
gunicorn -w 4 -b 0.0.0.0:8000 run:app
```

The application will be available at `http://localhost:5000` (development) or `http://localhost:8000` (production).

## Project Structure

```
taskmaster/
├── app/
│   ├── __init__.py          # Flask application factory
│   ├── models.py            # SQLAlchemy models
│   ├── routes.py            # Route handlers
│   ├── forms.py             # WTForms definitions
│   ├── templates/           # HTML templates
│   │   ├── base.html        # Base template
│   │   ├── index.html       # Home page
│   │   ├── create.html      # Create task form
│   │   ├── edit.html        # Edit task form
│   │   └── task.html        # Task details
│   └── static/
│       ├── css/
│       │   └── style.css    # Custom styles
│       └── js/
│           └── main.js      # Client-side logic
├── migrations/              # Database migrations
├── tests/                   # Unit tests
│   ├── conftest.py          # Test configuration
│   ├── test_models.py       # Model tests
│   └── test_routes.py       # Route tests
├── .env                     # Environment variables
├── .gitignore               # Git ignore file
├── config.py                # Application configuration
├── requirements.txt         # Python dependencies
├── run.py                   # Application entry point
└── README.md                # This file
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/tasks` | List all tasks |
| GET | `/api/tasks/<id>` | Get task by ID |
| POST | `/api/tasks` | Create new task |
| PUT | `/api/tasks/<id>` | Update existing task |
| DELETE | `/api/tasks/<id>` | Delete task |
| GET | `/api/tasks/search?q=term` | Search tasks |

### API Request/Response Examples

**Create Task:**
```bash
curl -X POST http://localhost:5000/api/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Complete project report",
    "description": "Finish the quarterly report",
    "priority": "high",
    "due_date": "2024-12-31"
  }'
```

**Response:**
```json
{
  "id": 1,
  "title": "Complete project report",
  "description": "Finish the quarterly report",
  "priority": "high",
  "status": "pending",
  "due_date": "2024-12-31",
  "created_at": "2024-01-15T10:30:00",
  "updated_at": "2024-01-15T10:30:00"
}
```

## Running Tests

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=app tests/

# Run specific test file
pytest tests/test_models.py -v
```

## Docker Deployment

### Build Docker Image

```bash
docker build -t taskmaster:latest .
```

### Run Docker Container

```bash
docker run -d -p 8000:8000 \
  -e SECRET_KEY=your-secret-key \
  -e DATABASE_URL=sqlite:///app/taskmaster.db \
  --name taskmaster-app \
  taskmaster:latest
```

### Docker Compose (Recommended)

```yaml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "8000:8000"
    environment:
      - FLASK_ENV=production
      - SECRET_KEY=${SECRET_KEY}
      - DATABASE_URL=sqlite:///app/taskmaster.db
    volumes:
      - ./data:/app/data
    restart: unless-stopped
```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `FLASK_APP` | Application entry point | `run.py` |
| `FLASK_ENV` | Environment mode | `development` |
| `SECRET_KEY` | Flask secret key | Required |
| `DATABASE_URL` | Database connection string | `sqlite:///taskmaster.db` |
| `MAX_CONTENT_LENGTH` | Max request size | `16 MB` |

### Application Settings (config.py)

```python
class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///taskmaster.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB
```

## Troubleshooting

### Common Issues

1. **Database errors**: Run `flask db upgrade` to apply migrations
2. **Port already in use**: Change port with `flask run --port=5001`
3. **Module not found**: Activate virtual environment and run `pip install -r requirements.txt`
4. **Permission denied**: Use `chmod +x run.py` on Unix systems

### Debug Mode

Enable debug mode for detailed error information:

```bash
export FLASK_DEBUG=1  # Unix
set FLASK_DEBUG=1     # Windows
flask run
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines

- Follow PEP 8 style guide
- Write unit tests for new features
- Update documentation as needed
- Use meaningful commit messages
- Keep pull requests focused and concise

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Flask documentation and community
- SQLAlchemy ORM documentation
- Bootstrap for responsive design inspiration
- All contributors and testers

## Support

For issues, questions, or feature requests:

- Open an issue on GitHub
- Contact: support@taskmaster.app
- Documentation: https://docs.taskmaster.app

---

**TaskMaster** - Making task management efficient and enjoyable.