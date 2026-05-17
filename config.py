import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    """Application configuration."""

    # Flask
    SECRET_KEY = os.environ.get("SECRET_KEY", "research-cloud-portal-secret-key-change-me")
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", f"sqlite:///{os.path.join(BASE_DIR, 'instance', 'portal.db')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # File uploads
    UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
    RESULTS_FOLDER = os.path.join(BASE_DIR, "results")
    MAX_CONTENT_LENGTH = 500 * 1024 * 1024  # 500 MB

    # ── OpenNebula Configuration ─────────────────────────────────────
    # Set DEMO_MODE = True to run without a live OpenNebula instance.
    # The portal will simulate VM provisioning and job execution.
    DEMO_MODE = False  # Live mode — connects to real OpenNebula at ONE_RPC_URL

    ONE_RPC_URL = os.environ.get("ONE_RPC_URL", "http://192.168.56.101:2633/RPC2")
    ONE_USERNAME = os.environ.get("ONE_USERNAME", "oneadmin")
    ONE_PASSWORD = os.environ.get("ONE_PASSWORD", "changeme123")

    # Default virtual network ID for VM NICs
    ONE_NETWORK_ID = int(os.environ.get("ONE_NETWORK_ID", "0"))

    # ── Compute Presets ──────────────────────────────────────────────
    CPU_OPTIONS = [1, 2, 4, 8]
    RAM_OPTIONS = [
        {"value": 512, "label": "512 MB (Micro)"},
        {"value": 1024, "label": "1 GB"},
        {"value": 2048, "label": "2 GB"},
        {"value": 4096, "label": "4 GB"},
        {"value": 8192, "label": "8 GB"},
        {"value": 16384, "label": "16 GB"},
    ]
    STORAGE_OPTIONS = [
        {"value": 1, "label": "1 GB"},
        {"value": 2, "label": "2 GB"},
        {"value": 5, "label": "5 GB"},
        {"value": 10, "label": "10 GB"},
        {"value": 20, "label": "20 GB"},
        {"value": 50, "label": "50 GB"},
        {"value": 100, "label": "100 GB"},
    ]

    # ── OS Images ────────────────────────────────────────────────────
    OS_IMAGES = {
        "ubuntu": {
            "name": "Ubuntu 22.04 LTS",
            "icon": "🐧",
            "description": "Popular Linux distribution for general-purpose computing",
            "image_id": 4,  # Replaced with actual OpenNebula Image ID (Ubuntu 24.04 MP)
        },
        "centos": {
            "name": "CentOS 8 Stream",
            "icon": "🐧",
            "description": "Enterprise-class Linux for servers and HPC",
            "image_id": 1,
        },
        "windows": {
            "name": "Windows 10 Pro",
            "icon": "🪟",
            "description": "Desktop environment for Windows-based research tools",
            "image_id": 2,
        },
        "winserver": {
            "name": "Windows Server 2022",
            "icon": "🖥️",
            "description": "Enterprise server environment for heavy workloads",
            "image_id": 3,
        },
    }

    # ── Software Stacks ─────────────────────────────────────────────
    SOFTWARE_STACKS = {
        "matlab": {
            "name": "MATLAB / Octave",
            "icon": "📐",
            "description": "Scientific computing, numerical analysis, and simulation",
            "packages": "MATLAB R2024a or GNU Octave 8.x",
        },
        "python_ds": {
            "name": "Python Data Science",
            "icon": "🐍",
            "description": "NumPy, Pandas, Scikit-learn, TensorFlow, Jupyter",
            "packages": "Python 3.11, NumPy, Pandas, Matplotlib, Scikit-learn, TensorFlow",
        },
        "mapreduce": {
            "name": "MapReduce / Hadoop",
            "icon": "🗺️",
            "description": "Large-scale distributed data processing framework",
            "packages": "Apache Hadoop 3.x, Apache Spark 3.x",
        },
    }
