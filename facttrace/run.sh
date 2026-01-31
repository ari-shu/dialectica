#!/bin/bash
# FactTrace - Run both backend and frontend

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo -e "${CYAN}"
echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║                        FactTrace                              ║"
echo "║          Multi-Agent Fact Verification System                 ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Check for .env file
if [ ! -f .env ]; then
    echo -e "${YELLOW}Creating .env template...${NC}"
    echo "OPENAI_API_KEY=your-api-key-here" > .env
    echo -e "${YELLOW}Please edit .env and add your OpenAI API key${NC}"
    exit 1
fi

# Check if API key is set
if grep -q "your-api-key-here" .env; then
    echo -e "${YELLOW}Please set your OPENAI_API_KEY in .env${NC}"
    exit 1
fi

# Cleanup function
cleanup() {
    echo -e "\n${YELLOW}Shutting down FactTrace...${NC}"
    kill $BACKEND_PID 2>/dev/null || true
    kill $FRONTEND_PID 2>/dev/null || true
    exit 0
}
trap cleanup SIGINT SIGTERM

# Start backend
echo -e "${GREEN}Starting FastAPI backend...${NC}"
python -m uvicorn api.server:app --reload --port 8000 --host 0.0.0.0 &
BACKEND_PID=$!
sleep 2

# Start frontend
echo -e "${GREEN}Starting React frontend...${NC}"
cd "$SCRIPT_DIR/ui"
npm run dev -- --host &
FRONTEND_PID=$!

echo ""
echo -e "${GREEN}FactTrace is running!${NC}"
echo -e "  ${CYAN}Frontend:${NC} http://localhost:5173"
echo -e "  ${CYAN}Backend:${NC}  http://localhost:8000"
echo -e "  ${CYAN}API Docs:${NC} http://localhost:8000/docs"
echo ""
echo -e "Press ${YELLOW}Ctrl+C${NC} to stop"
echo ""

wait
