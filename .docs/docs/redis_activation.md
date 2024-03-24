## Installing and Activating Redis

If you wish to use Redis for caching and improving response times, you can activate it by following these steps:

1. **Ensure Redis is Installed:**

   - Before proceeding, ensure that Redis is installed on your system or a remote server. You can download and install Redis from the [official website](https://redis.io/download).
   - If you prefer to use Docker, you can run Redis in a Docker container:
     ```bash
     docker run -d --name mawaqit-redis -p 6379:6379 redis:alpine3.18
     ```

2. **With Python:**

   - Before running the API, ensure that Redis is installed and running on your system or a remote server.
   - Set the environment variables for Redis host and port:
     ```bash
     export REDIS_HOST=your_redis_host
     export REDIS_PORT=your_redis_port
     export USE_REDIS=true
     ```
     Replace `your_redis_host` and `your_redis_port` with the appropriate values for your Redis host and port.
   - Start the API using the following command:
     ```bash
     uvicorn main:app --host 0.0.0.0 --port 8000
     ```
   - The API will be accessible at `http://localhost:8000`.

3. **With Docker:**

   - If you're building the Docker image locally, ensure that Redis is installed and running on your system or a remote server.
   - Set the environment variables when running the Docker container:
     ```bash
     docker run -d --name mawaqi-api-with-redis \
     -e REDIS_HOST=your_redis_host \
     -e REDIS_PORT=your_redis_port \
     -e USE_REDIS=true \
     -p 8000:80 mawaqi-api
     ```
   - This command runs the Docker container named `mawaqi-api-with-redis` with the specified environment variables. Ensure to replace `your_redis_host` and `your_redis_port` with your Redis host and port respectively.
   - The API will be accessible at `http://localhost:8000`.

## Docker Compose Configuration

If you prefer to manage your Mawaqi API and Redis containers together using Docker Compose, you can use the existing `docker-compose.yml` file in your project directory.

1. **Navigate to Your Project Directory**:

   Open a terminal or command prompt and navigate to the directory where your `docker-compose.yml` file is located.

2. **Run Docker Compose**:

   Execute the following command to start both the Mawaqi API and Redis containers using Docker Compose:

   ```bash
   docker-compose up -d
   ```

By following these steps, you can activate Redis for caching in your Mawaqi API deployment, enhancing its performance.
