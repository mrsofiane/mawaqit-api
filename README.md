# Mawaqit API

Mawaqit API is a REST API developed using the FastAPI framework, designed to interface with the [mawaqit.net](https://mawaqit.net) website. Mawaqit.net provides prayer times for over 8,000 mosques worldwide. This API aims to serve as a web application that fetches prayer times from mawaqit.net, delivering them in a streamlined JSON format. Unlike the current PHP-based website, which returns complete HTML pages for each request, this API focuses on delivering only the essential information.

## Local Setup

### Clone the Project

To get started, clone the repository to your local machine:

```bash
git clone https://github.com/mrsofiane/mawaqit-api.git
```

Navigate to the project directory:

```bash
cd mawaqit-api
```

### Setup with Python

Ensure the following libraries are installed before setting up a virtual environment:

- uvicorn
- requests
- fastapi
- httpx
- pytest
- bs4
- redis

Create a virtual environment:

```bash
python -m venv env
```

Activate the virtual environment:

```bash
source env/bin/activate
```

Install the required dependencies:

```bash
pip install -r requirements.txt
```

To start the server, execute:

```bash
uvicorn main:app
```

Upon successfully starting the server, you should see:

```plaintext
INFO:     Started server process [6684]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```

By default, the server address is http://127.0.0.1:8000. For API usage, refer to the **Documentation** section for available `GET` paths, or access known paths directly in the browser. Ensure to add the path-prefix to `<SERVER-ADDRESS>` to access the API, Otherwise it will not function correctly.

### Setup with Docker

To build the Docker image:

```bash
docker build . -t mawaqit-api:1.0
```

To run the Docker container:

```bash
docker run -d --name mawaqit-api -p 80:80 mawaqit-api:1.0
```

## Running Tests

Execute the following command to run tests:

```bash
pytest
```

## Running Redis with Docker

To run a Redis instance with Docker:

```bash
docker run --name mawaqit-api--redis -p 6379:6379 -d redis:alpine3.18
```

## Documentation

Documentation is available at `<SERVER-ADDRESS>/docs`, providing automatically generated OpenAPI documentation courtesy of FastAPI.

## Roadmap

- Implement Redis for caching to enhance response times. The goal is to improve upon the original site's 276 ms response time. ✅

## License

This project is licensed under the [MIT License](https://github.com/mrsofiane/mawaqit-api/blob/main/LICENSE.md).
