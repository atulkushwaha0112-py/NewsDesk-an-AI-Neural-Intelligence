# NewsDesk

NewsDesk is a comprehensive web application built with FastAPI that aggregates news from the Economic Times, providing an intuitive tracking timeline, user authentication, customizable news preferences, an AI-powered chat interface using Ollama, and a dedicated admin dashboard.

## Features

- **Automated News Scraping**: Fetches the latest articles continuously from Economic Times RSS feeds using `ET_fetch.py`.
- **User Authentication**: Secure login and registration system with Bcrypt password hashing.
- **Personalized Dashboard**: Users can set up category preferences and read news curated for them.
- **News Tracking**: Track specific articles in a customized timeline.
- **Interactive AI Chat**: Deep dive into news articles using a conversational AI interface powered by locally-hosted Ollama (`llama3.2:latest`).
- **Admin Panel**: Monitor application statistics, total users, and post distributions directly from the admin dashboard.

## Prerequisites

Before starting, ensure you have the following installed on your system:
- **Python 3.8+**
- **Ollama**: For running the local AI chat feature.

## Setup Instructions

### 1. Clone the Repository
Clone the project to your local machine:
```bash
git clone <your-repository-url>
cd <repository-directory>
```

### 2. Set up a Virtual Environment (Recommended)
Create and activate a Python virtual environment:
```bash
# On Windows
python -m venv venv
venv\Scripts\activate

# On macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
Install the required Python packages from `requirements.txt`:
```bash
pip install -r requirements.txt
```

### 4. Configure Local AI with Ollama
The AI chat functionality relies on the `llama3.2` model running via Ollama. 
1. Install [Ollama](https://ollama.com/) if you haven't already.
2. Download and run the required model in your terminal:
```bash
ollama run llama3.2:latest
```
Ensure Ollama is running in the background (by default on `http://localhost:11434`) before using the chat features.

### 5. Running the Application
The application uses two main processes: the web server and the background scraper.

**To run the FastAPI web server:**
```bash
uvicorn main:app --reload
```
The application will be accessible at: `http://localhost:8000`

**To run the news scraper (in a separate terminal):**
```bash
python ET_fetch.py
```
This script runs continuously, fetching RSS feeds and scraping articles into the local JSON storage.

## Usage

### User Panel
- Navigate to `http://localhost:8000` to be redirected to the user login page.
- Register a new account, set up your news preferences, and access your personalized dashboard.

### Admin Panel
The admin account is created from environment variables; the repository does not contain a default admin password.

1. Copy `.env.example` to `.env`.
2. Set `NEWS_DESK_SECRET_KEY` to a unique random value.
3. Set `NEWS_DESK_ADMIN_USERNAME` and `NEWS_DESK_ADMIN_PASSWORD` to your chosen admin credentials.
4. Start the application and open `http://localhost:8000/admin/login`.

Generate a signing key with:
```bash
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

Use the same environment variables in your deployment provider. Never commit `.env` or real credentials. Admin passwords are stored using bcrypt.

## Project Structure
- `main.py`: Main FastAPI application initialization and router configuration.
- `config.py`: Global application configuration, paths, and AI settings.
- `ET_fetch.py`: Background scraper for pulling news from Economic Times.
- `requirements.txt`: Python package dependencies.
- `login/`: Authentication mechanisms and user management.
- `admin/`: Modular admin panel and dashboard logic.
- `tracking/`: Timeline and article tracking functionalities.
- `dashboard/`: User dashboard and article view mechanisms.
- `profile/`: User profile management.
