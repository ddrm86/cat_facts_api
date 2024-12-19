# Cat Facts API

This project is a simple FastAPI application that provides an API for managing cat facts. 
Made following the official FastAPI tutorial.

## Features

- Create, read, update, and delete cat facts
- UUID generation for cat fact IDs
- Local SQLite database for data storage

## Requirements

- Python 3.10+
- FastAPI
- SQLModel

## Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/ddrm86/cat-facts-api.git
    cd cat-facts-api
    ```

2. Create a virtual environment and activate it:
    ```sh
    python -m venv .venv
    source .venv/bin/activate  # On Windows use `.venv\Scripts\activate.bat`
    ```

3. Install the dependencies:
    ```sh
    pip install -r requirements.txt
    ```

## Usage

1. Start the FastAPI server:
    ```sh
    fastapi run main.py  # use fastapi dev main.py for development
    ```

2. Open your browser and navigate to `http://127.0.0.1:8000/docs` to access the interactive API documentation.

## Endpoints

- `POST /cat_facts/`: Create a new cat fact
- `GET /cat_facts/`: Get a list of all cat facts
- `GET /cat_facts/{cat_fact_id}`: Get a specific cat fact by ID
- `PATCH /cat_facts/{cat_fact_id}`: Update a specific cat fact by ID
- `DELETE /cat_facts/{cat_fact_id}`: Delete a specific cat fact by ID

## License

This project is licensed under the GPLv3 License.
