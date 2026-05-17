# Cloud Computing Project - Research Cloud Portal

A Flask-based web application for managing research computing resources through OpenNebula cloud infrastructure.

## Features

- **User Authentication**: Secure login and registration system
- **Job Management**: Submit and monitor computing jobs
- **OpenNebula Integration**: Direct integration with OpenNebula cloud platform
- **Dashboard**: Real-time view of job status and system resources
- **REST API**: Programmatic access to cloud resources

## Project Structure

```
├── app/                          # Flask application package
│   ├── auth/                     # Authentication routes and logic
│   ├── portal/                   # Main portal routes
│   ├── services/                 # Business logic services
│   │   ├── job_runner.py        # Job execution and management
│   │   └── opennebula_service.py # OpenNebula API wrapper
│   ├── static/                   # Static files (CSS, JS)
│   └── templates/                # HTML templates
├── config.py                     # Application configuration
├── run.py                        # Application entry point
├── requirements.txt              # Python dependencies
└── research_dataset_large.csv   # Sample research dataset
```

## Requirements

- Python 3.8+
- Flask 3.0.0
- SQLAlchemy 3.1.1
- PyONE (OpenNebula Python client) 6.8.0

## Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Cloud-Project-main
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   - Update `config.py` with your OpenNebula credentials
   - Create a `.env` file if needed for sensitive configuration

## Running the Application

```bash
python run.py
```

The application will start on `http://localhost:5000`

## Environment Variables

Configure the following in `config.py` or `.env`:
- `OPENNEBULA_HOST`: OpenNebula server address
- `OPENNEBULA_USER`: OpenNebula username
- `OPENNEBULA_PASSWORD`: OpenNebula password
- `FLASK_ENV`: Environment (development/production)

## API Endpoints

### Authentication
- `POST /auth/login` - User login
- `POST /auth/register` - User registration
- `GET /auth/logout` - User logout

### Portal
- `GET /portal/dashboard` - View dashboard
- `GET /portal/jobs` - List user jobs
- `POST /portal/jobs` - Create new job
- `GET /portal/job/<id>` - View job details

## Development

For local development:
1. Ensure you have a local OpenNebula instance or test server
2. Update credentials in `config.py`
3. Run `python run.py` with debug mode enabled

## License

This is a university project. See LICENSE file for details.

## Authors

Cloud Computing Course - Group Project
