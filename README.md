# About The Project

Welcome to Futuramaapi – your go-to platform for diving into the realms of REST and GraphQL technologies.
More than just a learning space, this project is a dynamic hub for anyone keen on mastering RESTful API design,
crafting GraphQL queries, and exploring related technologies.

But we're not just another tutorial. Futuramaapi doubles as a sandbox,
inviting you to play with the latest tools and frameworks.
It's not about theory; it's about hands-on experience, transforming what you learn into practical skills.

Join a vibrant community, engage in experimentation, and collaborate with fellow enthusiasts.
Whether you're a beginner or a seasoned developer, Futuramaapi is your space for continuous learning and innovation.

Explore the future of API mastery with Futuramaapi – where learning meets experimentation.
Join us in shaping the future of technology.

## Key Features

### RESTful API:
Explore and understand the principles of REST through our comprehensive API implementation.

### GraphQL Integration:
Dive into the world of GraphQL with seamless integration and interactive examples.

### Server-Sent Events (SSE):
Experience real-time updates and notifications through the power of Server-Sent Events.

### OpenAPI Documentation:
Easily navigate and interact with our APIs using OpenAPI documentation.

### Technologies:
Built with HTTP/2, Hypercorn, Python 3.12, FastAPI, asynchronous programming, SQLAlchemy, alembic,
PostgreSQL, CI/CD, Ruff, and more,
this project embraces cutting-edge technologies to provide a modern development experience.

## Requirements

1. Python >= 3.12
2. PostgreSQL
3. poetry

## Installation


```commandline
# Clone repo
git clone git@github.com:koldakov/futuramaapi.git
# Instal dependencies
poetry install
# Initiate pre-commit
poetry run pre-commit install
```

<p align="right">(<a href="#top">back to top</a>)</p>

## Migrations

If you create models in a new file please import it in env.py.
Because alembic does not detect child classes.

```commandline
poetry run alembic revision --autogenerate -m "Revision Name"
poetry run alembic upgrade head
```

<p align="right">(<a href="#top">back to top</a>)</p>

## Development

```commandline
# Export variables
export $(cat .env | xargs)
# Run server
bash docker-entrypoint.sh
```

### Docker

To build the project in docker you can use:

```commandline
docker-compose up --build
```

Keep in mind docker-compose.yaml is for local DEV only.
It is NOT secure to use it in production as passwords are
hardcoded there for now (but you always can create a PR to fix it).

#### Notes

- Sending emails are disabled as this feature requires real env vars to be set.
- Redis is not being used in reality, but there is a task to move background tasks to redis.

<p align="right">(<a href="#top">back to top</a>)</p>

## Contributing

1. Fork the Project
2. Open a Pull Request
3. Or just read here: [contributing](https://docs.github.com/en/get-started/quickstart/contributing-to-projects)

<p align="right">(<a href="#top">back to top</a>)</p>

## Methodology

1. Do a lot, break a lot.
2. There are no difficult tasks, only interesting.
3. Mostly TBD.

<p align="right">(<a href="#top">back to top</a>)</p>

## Important

1. Quality.
2. Security.
3. Google first.

<p align="right">(<a href="#top">back to top</a>)</p>

## License

Distributed under the Apache 2.0 License. See [LICENSE.md](LICENSE.md) for more information.

<p align="right">(<a href="#top">back to top</a>)</p>

## Buy me a coffee if you want to support me

https://www.buymeacoffee.com/aivCoffee

## Contact

Hi all,

How are you? Hope You've enjoyed the project.

There are my contacts:

- [Linkedin](https://www.linkedin.com/in/aiv/)
- [Send an Email](mailto:coldie322@gmail.com?subject=[GitHub]-qworpa)

Project Link: https://github.com/koldakov/futuramaapi

Best regards,

[Ivan Koldakov](https://www.linkedin.com/in/aiv/)
