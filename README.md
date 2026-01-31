# EdgeLab v0.1

EdgeLab v0.1 is a lightweight, local coding lab environment for evaluating programming assignments in a secure and structured way. Users can submit code solutions, execute them in isolated sandboxes, and receive deterministic results based on public and hidden test cases. The system also optionally provides AI-assisted code feedback using local, open-source language models.


---

## System Overview

EdgeLab consists of three main components:

* **API Service (FastAPI)**
  Exposes endpoints to list assignments, submit solutions, trigger evaluation, retrieve results, and request AI feedback.

* **Runner Service**
  Executes submitted code inside isolated containers, enforces time and memory limits, runs public and hidden tests, and stores results.

* **Database (SQLite)**
  Stores submissions, uploaded files, execution status, and results to ensure consistency across restarts.

An optional **LLM Feedback Component** generates human-readable feedback using local open-source models via Ollama.

---

## Architecture

```
Client (Browser / Swagger UI)
        |
        v
     FastAPI API
        |
        v
     SQLite Database
        ^
        |
      Runner
```

The database is the central source of truth.
The API creates and reads submissions.
The runner executes code and writes results back to the database.

---

## Assignment Definition

Assignments are defined on disk and include:

* Assignment metadata (ID, language, limits)
* Problem description (`prompt.md`)
* Entry-point template (`solution_template.py`, `Main.java`, `solution.sql`)
* Public test cases (visible feedback)
* Hidden test cases (never exposed)

Sample assignments are provided for **Python**, **SQL**, and **Java**.

---

## Submission & Evaluation Flow

1. The user submits a solution using the API.
2. The submission is stored with status `created`.
3. The user triggers evaluation.
4. The runner executes the code in a sandbox and runs tests.
5. Results are stored and the status becomes `done` or `failed`.
6. The user retrieves results from the API.

Public test results and logs are visible.
Hidden tests affect scoring but are never exposed.

---

## How to Run EdgeLab

### Requirements

* Docker
* Docker Compose

---

### Start the system

From the project root (where `docker-compose.yml` is located), run:

```bash
docker compose up --build
```

This starts:

* API service
* Runner service
* Database
* Ollama (LLM service)

---

### Open the web interface

Once Docker is running, open your browser and go to:

```
http://localhost:8000/docs
```

This page (Swagger UI) lets you interact with the system without writing any client code.

---

## How to Submit and Run Code (Step by Step)

### Step 1: Submit a solution

Use **POST `/submissions`**.

You must provide:

* `assignment_id` → which problem you are solving
* `files` → your solution code

Each file has:

* `path`: the expected filename (entry point)
* `content`: the actual code

### Example: Python submission

```json
{
  "assignment_id": "py_sum_two",
  "files": [
    {
      "path": "solution.py",
      "content": "def add(a, b):\n    return a + b"
    }
  ]
}
```

Click **Execute**.
The response will return an `id`:

```json
{
  "id": "cabfbea6-9302-40a8-aeea-a3d802dd3a77",
  "status": "created"
}
```

Copy this `id`.

---

### Step 2: Run evaluation

Use **POST `/submissions/{submission_id}/evaluate`**.

Paste the `id` you received and click **Execute**.

This tells EdgeLab to run your code against public and hidden tests.

---

### Step 3: View results

Use **GET `/submissions/{submission_id}`**.

You will see:

* `status` (e.g. `done`)
* `score`
* `public` test results
* execution `logs`
* `runtime_ms`

Hidden test results are not shown, but they affect the final score.

---

## AI-Assisted Feedback (Optional)

EdgeLab provides an optional endpoint to generate AI-based feedback on submitted code.

### How it works

* Uses **Ollama** with local, open-source models
* No external APIs or paid services
* Only user-visible data is sent to the model
* Hidden tests and internal logic are never shared

---

### Request feedback

Use **POST `/submissions/{submission_id}/feedback`**.

Example request body:

```json
{
  "model": "qwen2.5-coder:1.5b"
}
```

### Recommended models

For laptops and limited resources:

* `qwen2.5-coder:1.5b` (recommended, stable)

Larger models may fail on low-memory machines:

* `phi3`
* `deepseek-coder:6.7b`

Model failures are handled gracefully and do not affect core evaluation.

---