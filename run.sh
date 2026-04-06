#!/bin/bash

# Define colors
GREEN='\\033[0;32m'
BLUE='\\033[0;34m'
NC='\\033[0m' # No Color

echo -e "${BLUE}=======================================${NC}"
echo -e "${BLUE}      Starting SynapseAI Platform      ${NC}"
echo -e "${BLUE}=======================================${NC}"

# Check if .env exists
if [ ! -f .env ]; then
    echo -e "\\n⚠️  WARNING: .env file not found."
    echo "Creating one from .env.example..."
    # Touch since we didn't commit a .temp.env in git
    touch .env
    echo "Please fill in your API keys in .env!"
fi

# Function to handle shutdown
cleanup() {
    echo -e "\\n${BLUE}Shutting down services...${NC}"
    kill $BACKEND_PID
    kill $FRONTEND_PID
    exit
}

# Trap CTRL+C
trap cleanup SIGINT

echo "Cleaning up lingering processes on 8000 and 8501..."
lsof -ti :8000 | xargs kill -9 2>/dev/null || true
lsof -ti :8501 | xargs kill -9 2>/dev/null || true
sleep 1

# 1. Start FastAPI Backend in background
echo -e "${GREEN}Starting FastAPI backend on port 8000...${NC}"
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!

# Wait a second for backend to initialize
sleep 2

# 2. Start Streamlit Frontend
echo -e "${GREEN}Starting Streamlit UI...${NC}"
python3 -m streamlit run frontend/app.py &
FRONTEND_PID=$!

# Wait for all background processes
wait $BACKEND_PID $FRONTEND_PID
