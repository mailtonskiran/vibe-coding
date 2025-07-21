# Mutual Fund Portfolio Management System

A web-based application to help investors create and manage their mutual fund portfolios.

## Features

- Investor registration and profile management
- Portfolio creation and management
- Fund recommendation based on risk profile
- Investment tracking and analysis
- Performance monitoring

## Setup Instructions

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Run the Flask application:
```bash
python app.py
```

3. The application will be available at http://localhost:5000

## Project Structure

- `app.py`: Main Flask application
- `requirements.txt`: Python dependencies
- `mutual_funds.db`: SQLite database file

## API Endpoints

- POST `/api/investors`: Create new investor
- POST `/api/portfolios/<investor_id>`: Create new portfolio
- GET `/api/recommendations/<investor_id>`: Get fund recommendations

## Tech Stack

- Backend: Python Flask
- Database: SQLite
- Frontend: React (to be implemented)

## Future Enhancements

- Real-time mutual fund data integration
- Portfolio rebalancing suggestions
- Performance analytics dashboard
- Risk assessment tools
- Historical performance tracking
