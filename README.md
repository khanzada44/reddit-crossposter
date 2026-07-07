# Reddit Crosspost Bot

A professional, production-ready Reddit bot for automated crossposting with intelligent features like random flair selection, ban detection, and comprehensive database tracking.

---

## Table of Contents

- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Database](#database)
- [Logging](#logging)
- [Project Structure](#project-structure)
- [Error Handling](#error-handling)
- [Rate Limiting](#rate-limiting)
- [Deployment](#deployment)
- [Support](#support)

---

## Features

- Crosspost from source subreddit to multiple target subreddits
- Random flair selection for each crosspost
- Ban detection - automatically skips subreddits where user is banned
- Crosspost disabled handling - skips subreddits with disabled crossposts
- SQLite database for tracking posted submissions
- Duplicate prevention - prevents reposting same content
- Detailed logging with rotation
- Rate limiting - respects Reddit's API rate limits
- Error recovery with automatic retry
- Statistics tracking for success rates and performance

---

## Prerequisites

Before you begin, ensure you have the following:

- Python 3.8 or higher
- Reddit Account
- Reddit API Access (must request approval from Reddit)

Minimum Requirements:
- Python 3.8+
- pip 20.0+
- Internet connection for API calls
- 100MB free storage space

---

## Installation

Step 1: Create Project Directory

mkdir reddit-bot
cd reddit-bot

Step 2: Create Virtual Environment

Windows:
python -m venv venv
venv\Scripts\activate

Mac/Linux:
python3 -m venv venv
source venv/bin/activate

Step 3: Install Dependencies

pip install -r requirements.txt

Step 4: Create Required Directories

mkdir data logs

---

## Configuration

Step 1: Create Reddit App

1. Go to https://www.reddit.com/prefs/apps
2. Click "Create App"
3. Fill in the details:
   - Name: CrosspostBot
   - App Type: Script
   - Description: Optional
   - Redirect URI: http://localhost:8080
4. Note down client_id and client_secret

Step 2: Request API Access

IMPORTANT: As per Reddit's Responsible Builder Policy, you must get approval before using the API.

1. Go to https://support.reddithelp.com/hc/en-us/requests/new
2. Select "Data Access Request"
3. Fill in the form with your project details
4. Wait for approval (2-3 days)

Step 3: Configure Environment Variables

Create .env file in the root directory:

# Reddit API Credentials
- REDDIT_CLIENT_ID=your_client_id_here
- REDDIT_CLIENT_SECRET=your_client_secret_here
- REDDIT_USERNAME=your_reddit_username
- REDDIT_PASSWORD=your_reddit_password
- REDDIT_USER_AGENT=MyRedditBot/1.0 (by /u/your_username)

# Bot Configuration
- SOURCE_SUBREDDIT=python
- TARGET_SUBREDDITS=learnpython,programming,coding
- POST_LIMIT=10
- DELAY_BETWEEN_POSTS=60
- MAX_RETRIES=3

# Database
- DATABASE_URL=sqlite:///data/bot.db

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/bot.log

# Environment
ENVIRONMENT=development
DEBUG=true

---

## Usage

Quick Start:

Activate virtual environment:
Windows: venv\Scripts\activate
Mac/Linux: source venv/bin/activate

Run the bot:
python src/main.py

Create Run Script (Windows) - save as run.bat:

@echo off
echo Starting Reddit Bot...
cd /d "%~dp0"
call venv\Scripts\activate
python src/main.py
pause

Create Run Script (Mac/Linux) - save as run.sh:

#!/bin/bash
echo "Starting Reddit Bot..."
cd "$(dirname "$0")"
source venv/bin/activate
python src/main.py

Make run script executable (Mac/Linux):
chmod +x run.sh
./run.sh

---

## Database

Database Location:
data/bot.db

Tables Structure:

subreddits - Subreddit information (name, allow_crossposts, user_banned)
submissions - Tracked posts (reddit_id, title, subreddit)
crossposts - Crosspost history (target_subreddit, status, flair_used)
subreddit_stats - Performance metrics (success_rate, total_crossposts)
subreddit_flairs - Flair tracking (flair_text, usage_count)

View Database:

Using SQLite Browser:
1. Download DB Browser for SQLite from https://sqlitebrowser.org/
2. Open data/bot.db

Command Line:
sqlite3 data/bot.db

Show tables: .tables
Query data: SELECT * FROM subreddits;
Exit: .quit

---

## Logging

Log Location:
logs/bot.log

Log Format:
2024-01-15 10:30:00 - INFO - src.core.reddit_client - Successfully authenticated with Reddit
2024-01-15 10:30:00 - INFO - src.core.crossposter - Reddit Crosspost Bot Started
2024-01-15 10:30:01 - INFO - src.core.crossposter - Fetched 10 submissions from r/python

Log Rotation:
- Size: 10 MB
- Retention: 30 days
- Compression: Automatic

---

## Project Structure
```text
reddit-bot/
├── src/
│   ├── __init__.py
│   ├── main.py                  # Entry point
│   ├── config/
│   │   ├── __init__.py
│   │   └── settings.py          # Configuration
│   ├── core/
│   │   ├── __init__.py
│   │   ├── reddit_client.py    # Reddit API wrapper
│   │   └── crossposter.py      # Main bot logic
│   ├── services/
│   │   ├── __init__.py
│   │   ├── database_service.py # Database operations
│   │   ├── flair_service.py    # Flair management
│   │   └── ban_service.py      # Ban detection
│   ├── models/
│   │   ├── __init__.py
│   │   ├── database.py
│   │   ├── submission.py
│   │   └── subreddit.py
│   ├── utils/
│   │   ├── __init__.py
│   │   └── logger.py
│   └── exceptions/
│       ├── __init__.py
│       └── custom_exceptions.py
├── data/
│   └── bot.db
├── logs/
│   └── bot.log
├── .env
├── .gitignore
├── requirements.txt
└── README.md
```
---

## Error Handling

Common Errors and Solutions:

AuthenticationError - Invalid credentials
Solution: Check .env file credentials

SubredditBannedError - User is banned
Solution: Bot skips automatically

CrosspostDisabledError - Crossposts disabled
Solution: Bot skips automatically

RateLimitError - Rate limit hit
Solution: Bot waits and retries

ModuleNotFoundError - Missing dependency
Solution: pip install -r requirements.txt

DatabaseError - Database issue
Solution: Ensure data/ directory exists

---

## Rate Limiting

Reddit API Limits:
- Requests per minute: 60 per client
- Requests per 10 minutes: 600 aggregate
- Retry After: 60 seconds on rate limit hit

The bot automatically handles rate limiting with:
- Configurable delays between posts (default: 60 seconds)
- Automatic retry with exponential backoff
- Rate limit detection and waiting

---

## Deployment

Development Environment:
python src/main.py
tail -f logs/bot.log (to watch logs)

Production Environment:

Linux/Mac Cron Job:
0 * * * * cd /path/to/reddit-bot && source venv/bin/activate && python src/main.py >> logs/cron.log 2>&1

Windows Task Scheduler:
1. Open Task Scheduler
2. Create Basic Task
3. Trigger: Daily (Repeat every 1 hour)
4. Action: Start program -> python
5. Arguments: C:\path\to\reddit-bot\src\main.py
6. Start in: C:\path\to\reddit-bot

---

## Quick Commands Summary

Setup:
python -m venv venv
venv\Scripts\activate (Windows)
source venv/bin/activate (Mac/Linux)
pip install -r requirements.txt

Create directories:
mkdir data logs

Run bot:
python src/main.py

View logs:
tail -f logs/bot.log (Mac/Linux)
type logs\bot.log (Windows)

View database:
sqlite3 data/bot.db

---

## Important Notes

Reddit Rules Compliance:

Do's:
- Respect rate limits (60 requests/minute)
- Use proper user-agent
- Follow subreddit rules
- Keep delays between posts
- Use for non-commercial purposes

Don'ts:
- No vote manipulation
- No karma farming
- No spam (limit crossposts)
- No data mining
- No AI training
- No data selling
- No privacy violations

Best Practices:
1. Test with 1-2 subreddits first
2. Monitor logs regularly
3. Keep delays at 60+ seconds
4. Backup database periodically
5. Stay within rate limits
6. Follow Responsible Builder Policy

---

## Support

Documentation:
- PRAW Documentation: https://praw.readthedocs.io/
- Reddit API Documentation: https://www.reddit.com/dev/api/
- Responsible Builder Policy: https://support.reddithelp.com/hc/en-us/articles/42728983564564-Responsible-Builder-Policy

Community Support:
- r/redditdev: https://www.reddit.com/r/redditdev/
- r/learnpython: https://www.reddit.com/r/learnpython/

Contact:
- Email: minhamhussain@gmail.com

---

## Version History

v1.0.0 - 2024-01-15 - Initial release with core features

---

## License

This project is licensed under the MIT License.

---

Made for the Reddit community

Happy Crossposting