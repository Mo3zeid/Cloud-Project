# Cloud Computing Project - Research Cloud Portal

<div align="center">

[![Python](https://img.shields.io/badge/python-v3.8+-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/flask-3.0.0-green.svg)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](#license)

A comprehensive Flask-based web application for managing research computing resources through **OpenNebula** cloud infrastructure.

[Features](#features) • [Installation](#installation) • [Usage](#usage) • [Architecture](#architecture) • [Contributing](#contributing)

</div>

---

## 📋 Overview

The Research Cloud Portal is a modern cloud resource management system designed for academic and research institutions. It provides an intuitive interface for researchers to submit computational jobs, monitor resource usage, and interact with enterprise cloud infrastructure seamlessly.

Built with **Flask**, **SQLAlchemy**, and **PyONE**, this platform bridges the gap between researchers and complex cloud infrastructure, making high-performance computing accessible to all users.

## ✨ Features

### 🔐 Authentication & Security
- Secure user registration and login system
- Session-based authentication with Flask-Login
- Password hashing and validation
- Role-based access control framework

### 💼 Job Management
- Submit computing jobs with custom parameters
- Real-time job status monitoring
- Job history and archival
- Batch job processing capabilities
- Job result retrieval and download

### ☁️ Cloud Integration
- Direct integration with **OpenNebula** platform
- Virtual machine provisioning and management
- Resource allocation and monitoring
- Live infrastructure status dashboard

### 📊 Analytics & Monitoring
- Real-time resource utilization tracking
- Job execution statistics and metrics
- System health monitoring
- Resource usage reports

### 🎨 User Interface
- Responsive dashboard with Bootstrap styling
- Intuitive job submission wizard
- Job details and status pages
- Clean, modern design

## 🏗️ Project Architecture

### Directory Structure

```
Cloud-Project/
├── app/                              # Flask application package
│   ├── __init__.py                  # Application factory
│   ├── extensions.py                # Database and extension initialization
│   ├── models.py                    # SQLAlchemy data models
│   │
│   ├── auth/                        # Authentication module
│   │   ├── __init__.py
│   │   └── routes.py                # Login, register, logout routes
│   │
│   ├── portal/                      # Main portal module
│   │   ├── __init__.py
│   │   └── routes.py                # Dashboard and job routes
│   │
│   ├── services/                    # Business logic layer
│   │   ├── __init__.py
│   │   ├── job_runner.py           # Job execution engine
│   │   └── opennebula_service.py   # OpenNebula API wrapper
│   │
│   ├── static/                      # Frontend assets
│   │   ├── css/
│   │   │   └── style.css           # Application styles
│   │   └── js/
│   │       └── app.js              # Client-side JavaScript
│   │
│   └── templates/                   # Jinja2 HTML templates
│       ├── base.html                # Base template layout
│       ├── auth/
│       │   ├── login.html
│       │   └── register.html
│       └── portal/
│           ├── dashboard.html
│           ├── job_detail.html
│           └── new_job.html
│
├── config.py                        # Application configuration
├── run.py                           # Application entry point
├── requirements.txt                 # Python dependencies
├── README.md                        # This file
└── .gitignore                       # Git ignore rules
```

## 📦 Tech Stack

| Technology | Version | Purpose |
|-----------|---------|---------|
| **Python** | 3.8+ | Core programming language |
| **Flask** | 3.0.0 | Web framework |
| **Flask-Login** | 0.6.3 | Authentication |
| **SQLAlchemy** | 3.1.1 | ORM & Database |
| **PyONE** | 6.8.0 | OpenNebula API client |
| **Werkzeug** | 3.0.1 | WSGI utilities |
| **Gunicorn** | 21.2.0 | WSGI HTTP server |
| **Paramiko** | 3.4.0 | SSH protocol support |

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- pip package manager
- OpenNebula server (for production)
- Git (for cloning)

### Installation Steps

1. **Clone the repository**
   ```bash
   git clone https://github.com/Mo3zeid/Cloud-Project.git
   cd Cloud-Project
   ```

2. **Create and activate virtual environment**
   ```bash
   # On Windows
   python -m venv venv
   venv\Scripts\activate
   
   # On macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure the application**
   ```bash
   # Edit config.py with your settings
   # Set OpenNebula credentials and database configuration
   ```

5. **Run the development server**
   ```bash
   python run.py
   ```
   The application will be available at `http://localhost:5000`

## ⚙️ Configuration

### Environment Variables

Configure these settings in `config.py`:

```python
# OpenNebula Configuration
OPENNEBULA_HOST = "your-opennebula-server.com"
OPENNEBULA_USER = "your_username"
OPENNEBULA_PASSWORD = "your_password"
OPENNEBULA_PORT = 2633

# Flask Configuration
FLASK_ENV = "development"  # or "production"
DEBUG = True
SECRET_KEY = "your-secret-key-here"

# Database
SQLALCHEMY_DATABASE_URI = "sqlite:///cloud_portal.db"
SQLALCHEMY_TRACK_MODIFICATIONS = False
```

### .env File (Optional)

Create a `.env` file in the project root for sensitive data:

```
OPENNEBULA_HOST=your-server.com
OPENNEBULA_USER=admin
OPENNEBULA_PASSWORD=secure_password
SECRET_KEY=your-secret-key
```

## 📖 Usage

### User Registration
1. Navigate to `/auth/register`
2. Enter username, email, and password
3. Confirm registration

### Submitting a Job
1. Log in to your account
2. Go to Dashboard → New Job
3. Fill in job parameters (name, description, resources)
4. Select data files and submit
5. Monitor job status in real-time

### Viewing Job Results
1. Go to Dashboard → My Jobs
2. Click on a job to view details
3. Download results when job completes

## 🔌 API Endpoints

### Authentication Routes
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/login` | User login |
| POST | `/auth/register` | User registration |
| GET | `/auth/logout` | User logout |

### Portal Routes
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/portal/dashboard` | Main dashboard view |
| GET | `/portal/jobs` | List all user jobs |
| POST | `/portal/jobs` | Submit new job |
| GET | `/portal/job/<id>` | View job details |
| GET | `/portal/job/<id>/status` | Get job status (JSON) |
| DELETE | `/portal/job/<id>` | Cancel/delete job |

## 🛠️ Development

### Setting Up Development Environment

```bash
# Install development dependencies
pip install -r requirements.txt

# Run in debug mode
python run.py

# With hot reload (install flask-reload if needed)
pip install flask-reload
```

### Running Tests

```bash
# Unit tests
python -m pytest tests/

# With coverage
pytest --cov=app tests/
```

### Database Migrations

```bash
# If using Flask-Migrate
flask db init
flask db migrate -m "description"
flask db upgrade
```

## 📊 Datasets

The project includes sample datasets for testing:

- **research_dataset_large.csv**: Large dataset for benchmarking (287KB)
- **sample_dataset.csv**: Small dataset for quick testing (754B)

## 🐛 Troubleshooting

### Connection Issues
- Verify OpenNebula server is running
- Check credentials in `config.py`
- Ensure network connectivity

### Port Already in Use
```bash
# Change port in run.py or use
python run.py --port 5001
```

### Database Errors
```bash
# Reset database
rm cloud_portal.db
python -c "from app import create_app, db; app = create_app(); db.create_all()"
```

## 📝 Project Documentation

See `OpenNebula Project.pdf` for detailed project specifications and architecture documentation.

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Commit your changes (`git commit -m 'Add amazing feature'`)
5. Push to the branch (`git push origin feature/amazing-feature`)
6. Open a Pull Request

### Code Style

- Follow PEP 8 Python style guide
- Use meaningful variable names
- Add docstrings to functions and classes
- Comment complex logic

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👥 Authors & Contributors

- **Cloud Computing Course - Group Project**
- Developed as part of the 8th Semester Cloud Computing course
- Fourth Year, University Project

## 📞 Support

For issues and questions:
- Open an issue on GitHub
- Check existing documentation
- Review OpenNebula Project.pdf for architecture details

## 🔗 Related Links

- [OpenNebula Documentation](https://docs.opennebula.io/)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)

---

<div align="center">

Made with ❤️ for cloud computing enthusiasts

</div>
