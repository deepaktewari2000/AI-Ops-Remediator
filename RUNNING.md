# How to Run AI-Ops-Remediator

## Prerequisites
- Python 3.11 or higher
- pip (Python package manager)

## Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd AI-Ops-Remediator
   ```

2. **Create a virtual environment (Optional but recommended)**
   ```bash
   python -m venv venv
   # Windows
   .\venv\Scripts\activate
   # Linux/macOS
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

## Configuration

1. **Environment Variables**
   Copy the example environment file to create your local configuration:
   ```bash
   # Windows
   copy .env.example .env
   # Linux/macOS
   cp .env.example .env
   ```

2. **Edit .env**
   Open `.env` and populate the following variables:
   - `GEMINI_API_KEY`: Your Google Gemini API key.
   - `SLACK_BOT_TOKEN`: Your Slack Bot Token.
   - `SNOW_URL`, `SNOW_USER`, `SNOW_PASS`: ServiceNow credentials.

   *Note: For local testing without real services, you can use dummy values.*

## Running the Application

Start the server using `uvicorn`:

```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`.

## Running Tests

To run the test suite (including integration tests):

```bash
# Install test dependencies if not already installed
pip install pytest pytest-asyncio

# Run tests
pytest
```

## API Documentation

Once the application is running, you can access the interactive API docs at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
