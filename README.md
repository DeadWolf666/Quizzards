# QUIZZARDS 1.0

Source code for a web application serving quizzes on any topic, using Flask, SQLite3, VueJS, Celery and Redis.

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [Features](#features)

## Installation

Install [Redis for Windows](https://github.com/microsoftarchive/redis/releases/download/win-3.2.100/Redis-x64-3.2.100.msi), and add it to your PATH variable. Make sure you have the latest release of Python and NodeJS installed, along with npm and utilities like Babel, ESLint and Prettier. You may need to add Python and NodeJS to your PATH variable to ensure the following commands run smoothly.

```bash
# Clone the repository
git clone https://github.com/21f1004172/Quizzards.git

# Navigate to the project directory
cd Quizzards

# Install dependencies
python -m venv .env
pip install -r requirements.txt
cd frontend
npm install
```

## Usage

To run the project, make sure you select the .env virtual environment as the default Python interpreter, so all the following terminals will open with the virtual environment activated, else activate the virtual environment by running the ```.env\Scripts\activate``` command in each terminal before you input any other command.

```cmd terminal 1
redis-server
```

```cmd terminal 2
celery -A main.celery worker --loglevel=info --pool=solo
```

```cmd terminal 3
celery -A main.celery beat --loglevel=info
```

```cmd terminal 4
python main.py
```

```cmd terminal 5
cd frontend
npx prettier --write .
npm run serve
```

## Features

- Admin user functions as the quizmaster, creating new quizzes, subjects and chapters. Use the credentials admin@quizzards.com, password: admin#123 to login as admin.
- Admin can make a CSV export of the performance of all users, and view the CSV in an "exports" folder created in the root directory. The folder will be created automatically, no need to create it yourself.
- Users can give quizzes created by admin as timed attempts, view their past attempts, and receive daily reminders and monthly reports on their email.
- Both admin and users can search for subjects, chapters and quizzes. Additionally, admin can also search for users and view their records.