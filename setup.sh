#!/bin/bash
set -e

echo "=== The Negotiator — Setup ==="

echo "Installing Python dependencies..."
pip install -r requirements.txt --quiet

echo "Creating data directories..."
mkdir -p data/job_specs data/quotes data/price_movements data/ledgers data/transcripts

if [ ! -f .env ]; then
  echo "Creating .env from template..."
  cp .env.example .env
  echo "⚠️  Add your ELEVENLABS_API_KEY to .env before continuing."
fi

echo ""
echo "Setup complete. Next steps:"
echo "1. Add your ElevenLabs API key to .env"
echo "2. Start the tool server:  uvicorn tools.server:app --host 0.0.0.0 --port 8000"
echo "3. Make port 8000 public in the VS Code 'Ports' tab"
echo "4. Set TOOL_SERVER_URL in .env to that public URL"
echo "5. Create agents:  python agents/create_agents.py"
echo "6. Run:  python run_demo.py"