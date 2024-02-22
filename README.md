
# Mawaqit Api

Mawaqi Api is a Rest Api for [mawaqit.net](https://mawaqit.net) using FastApi framework,
the mawaqit.net website gives you the prayer times for more than 8000 mosques around the world,
the idea behind this api is to create an api web app that uses the mawaqit website as data source
to fetch prayer times and return them in json with the minimum information needed,
the current website is using php so it's returning the whole html every get request.



## Run Locally

Clone the project

```bash
git clone https://github.com/mrsofiane/mawaqit-api.git
```

Go to the project directory

```bash
cd mawaqit-api
```

### With Python

Create virtual environment

```bash
python -m  venv env
```

Create virtual environment

```bash
source env/bin/activate
```

Install dependencies

```bash
pip install -r requirements.txt
```

Start the server

```bash
uvicorn main:app
```

### With Docker

Build docker image

```bash
docker build . -t mawaqit-api:1.0
```

Run docker image

```bash
docker run -d  --name mawaqit-api -p 80:80 mawaqit-api:1.0
```
## Running Tests

To run tests, run the following command

```bash
pytest
```
## Run Redis With Docker
```bash
docker run --name mawaqit-api--redis -p 6379:6379 -d redis:alpine3.18
```
## Documentation

You can find the documentation on the path `/docs`,
it's an openapi documentation generated automatically from FastApi.

## Roadmap

- Add redis database to store cache and reduce the response time, the original website use 276 ms. ✅

## License

[MIT](https://github.com/mrsofiane/mawaqit-api/blob/main/LICENSE.md)

