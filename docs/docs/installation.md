## Installation

There are multiple ways to install and deploy the Mawaqi API depending on your preferences and requirements.

1. **Using Source Code and Running Python:**

   - Clone the repository from [GitHub](https://github.com/mrsofiane/mawaqit-api).
   - Ensure you have Python installed on your system (version 3.8 or higher).
   - Navigate to the project directory.
   - Create virtual environment `python -m  venv env` or `python3 -m  venv env`.
   - Activate the virtual environment `source env/bin/activate`.
   - Install dependencies using pip: `pip install -r requirements.txt` or `pip3 install -r requirements.txt`.
   - Run the API using the following command: `uvicorn main:app --host 0.0.0.0 --port 8000`.
   - The API will be accessible at `http://localhost:8000`.

2. **Using Docker to Build Image:**

   - Ensure you have Docker installed on your system.
   - Clone the repository from [GitHub](https://github.com/mrsofiane/mawaqit-api).
   - Navigate to the project directory.
   - Build the Docker image using the provided Dockerfile: `docker build -t mawaqi-api .`.
   - Run the Docker container: `docker run -d --name mawaqit-api -p 8000:80 mawaqi-api`.
   - The API will be accessible at `http://localhost:8000`.

Choose the installation method that best suits your environment and preferences.

**API Documentation:**

You can find the API documentation at the path `/docs` relative to your API's base URL. It's an OpenAPI documentation generated automatically from FastAPI.

[Activating Redis](/docs/redis_activation.md)
