# Academic Research Assistant Project

This project is an Academic Research Assistant that fetches research papers from the arXiv API, stores them in a PostgreSQL database, and allows users to query and generate answers using a generative model (T5). This README provides instructions for setting up and running the project locally.

## Prerequisites

- **Python 3.8 or higher** – [Download Python](https://www.python.org/downloads/)
- **PostgreSQL** – [Download PostgreSQL](https://www.postgresql.org/download/)
- **pgAdmin4** (optional, for managing your PostgreSQL database)
- **Git** – [Download Git](https://git-scm.com/)

## Step 1: Clone the Repository

Open a terminal (or Command Prompt) and run:

```bash
git clone https://github.com/kealankuar/academic-research-assistant.git
cd academic-research-assistant
```
## Step 2 : Create and Activate a Virtual Environment

### On Windows (CMD):
```bash
python -m venv rag-env
rag-env\Scripts\activate
```

### On Windows (PowerShell):
```bash
python -m venv rag-env
.\rag-env\Scripts\Activate.ps1
```
