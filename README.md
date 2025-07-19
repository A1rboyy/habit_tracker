# Habit Tracker
A FastAPI-based Habit Tracker application that allows users to:

- Create and delete daily or weekly habits
- Mark habits as completed
- Track longest streaks for each habit or across all habits
- Analyze consistency over time

---

## Features

- FastAPI backend with CRUD functionality
- Analytics for habit streaks (daily or weekly)
- 🗃SQLite3 database with automatic schema setup
- Pytest-based test suite (10 tests included)

---
Before Starting you should clone the Repository, Creating a virtual Environment and installing the Dependencies.
Python 3.12 works confirmend, other versions not tested.

FastAPI Dev Environment can be run with fastapi dev or alternatively with the specified file fastapi dev .\application\main.py.

Once running, open your browser and navigate to:
http://127.0.0.1:8000/docs – Swagger API docs

<img width="1474" height="535" alt="image" src="https://github.com/user-attachments/assets/d16ddeaa-cf5e-4646-8ea7-7a5e477fb8d3" />


Test can be run with typing pytest or pytest .\tests\tests.py and should result in 10 passed tests.

<img width="1466" height="18" alt="image" src="https://github.com/user-attachments/assets/044278cb-7c77-4bb9-aad0-09bea0db1ef7" />



Project Structure for you should look like the following:

habit_tracker/
├── application/
│   ├── main.py            # FastAPI app + routes
│   ├── crud.py            # Database operations
│   ├── analytics.py       # Streak computation logic
│   ├── database.py        # SQLite schema + connection
│   ├── models.py          # Pydantic schemas
├── tests/
│   ├── tests.py           # Pytest test suite
├── requirements.txt
├── README.md
