**InsightLink**: A URL Shortener with Real-time Analytics
A robust, multi-service URL shortener application built with a modern backend stack. InsightLink not only shortens long URLs but also tracks click analytics in real-time. The entire application stack is containerised with Docker and managed by Docker Compose, ensuring a seamless, one-command setup for development and deployment.

**->Core Features**
**->URL Shortening**: Generate a unique, short code for any long URL.

**->Fast Redirects**: Implements a Redis caching layer to ensure lightning-fast lookups and redirects for frequently accessed links.

**->Click Analytics**: Logs every click, capturing the timestamp and user agent.

**->Analytics API**: Provides a dedicated endpoint to retrieve the total click count and detailed click history for any short URL.

**->Containerized Environment**: The entire stack (API, Database, Cache) is defined in a docker-compose.yml file for guaranteed reproducibility and easy setup.

**->Robust Error Handling**: Implements professional API error handling for invalid or non-existent URLs.

**Architecture Diagram:**
The application is composed of three distinct services that communicate over a Docker network, simulating a real-world microservice architecture.

graph TD
    subgraph "User's Machine"
        U[User's Browser]
    end

    subgraph "Docker Environment"
        F[FastAPI Backend]
        R[(Redis Cache)]
        P[(PostgreSQL DB)]
    end

    U -- HTTP Request --> F
    F -- Write/Read Cache --> R
    F -- Write/Read DB --> P

    style F fill:#2a9d8f,stroke:#333,stroke-width:2px
    style R fill:#e76f51,stroke:#333,stroke-width:2px
    style P fill:#264653,stroke:#333,stroke-width:2px

**Tech Stack**
**Category Technology**
->Backend
Python 3.11, FastAPI, Uvicorn
**Database**
PostgreSQL
Caching
Redis
DevOps
Docker, Docker Compose

**Libraries**
SQLAlchemy (ORM), Pydantic (Validation), Psycopg2

**Getting Started**
This project is designed for a simple, one-command setup thanks to Docker.

**Prerequisites**
You must have Docker and Docker Compose installed on your machine. You can get them by installing Docker Desktop.

**Running the Application**
Clone the repository:

git clone [https://github.com/YOUR_USERNAME/insightlink.git](https://github.com/YOUR_USERNAME/insightlink.git)
cd insightlink

**Run with Docker Compose:**
Execute the following command from the root of the project directory. This single command will build the FastAPI image, pull the official images for Postgres and Redis, and start all three containers.

docker-compose up --build

That's it! The application is now running.

The API will be accessible at http://localhost:8001.

You can view the interactive API documentation (powered by Swagger UI) at http://localhost:8001/docs.

**API Endpoints**
The interactive documentation at /docs is the best way to test the API, but here is a quick overview:

**Method Endpoint Description**

**POST**

/url

Creates a new short URL. Expects a JSON body like {"url": "your_long_url"}

**GET**

/{short_code}

Redirects to the original long URL and logs the click event.

**GET**

/analytics/{short_code}

Retrieves the click count and detailed history for a given short URL.

**What I Learned**
Multi-Container Application Management: Orchestrating a full backend stack (API, database, cache) using Docker Compose and managing inter-service communication over a Docker network.

Implementing a Caching Strategy: Integrating Redis to reduce database load and improve response latency for read-heavy operations (redirects).

Robust API Development: Building a clean, well-documented API with FastAPI, including data validation with Pydantic and professional error handling using HTTPException.

Database Integration with an ORM: Using SQLAlchemy to define database models and interact with a PostgreSQL database in a containerized environment.
