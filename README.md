# Dashboard with Agent Integration

A comprehensive Streamlit dashboard with leaderboards, graphs, timelines, and detail cards for users and groups. The application is connected to a database and features agent capabilities to process various data inputs.

## Features

- **Interactive Dashboard**
  - Leaderboards for tracking performance
  - Visualizations for user and group analytics
  - Timeline views of activities
  - Detailed user and group profile cards

- **Agent Integration**
  - Process Excel files
  - Extract data from documents
  - Accept text input via chat
  - Update the database through various tools

## Setup

1. Install dependencies:
```
pip install -r requirements.txt
```

2. Run the Streamlit dashboard:
```
streamlit run app/dashboard.py
```

## Project Structure

```
windsurf-project/
├── app/
│   ├── dashboard.py         # Main Streamlit dashboard
│   ├── components/          # Dashboard components
│   │   ├── leaderboard.py
│   │   ├── graphs.py
│   │   ├── timeline.py
│   │   └── detail_cards.py
├── agents/                  # Agent implementation
│   ├── agent_manager.py
│   ├── tools/
│   │   ├── db_tools.py
│   │   ├── excel_tools.py
│   │   └── document_tools.py
├── database/
│   ├── db_manager.py
│   └── schema.py
├── requirements.txt
└── README.md
```

## Technologies

- Python
- Streamlit
- Google Vertex AI SDK
- SQLite Database
