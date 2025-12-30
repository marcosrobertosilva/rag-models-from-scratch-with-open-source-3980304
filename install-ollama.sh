#!/bin/bash

set -e

echo "======================================"
echo "Ollama Installation Script for Codespace"
echo "======================================"
echo ""

# Check if Ollama is already installed
if command -v ollama &> /dev/null; then
    echo "✓ Ollama is already installed"
    ollama --version
else
    echo "Installing Ollama..."
    curl -fsSL https://ollama.ai/install.sh | sh
    echo "✓ Ollama installed successfully"
fi

echo ""
echo "======================================"
echo "Pulling Mistral model..."
echo "======================================"
echo ""

# Start Ollama service in the background
echo "Starting Ollama server..."
ollama serve &
OLLAMA_PID=$!

# Wait for Ollama to be ready
echo "Waiting for Ollama to start..."
for i in {1..30}; do
    if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
        echo "✓ Ollama is ready"
        break
    fi
    echo "  Waiting... ($i/30)"
    sleep 1
done

# Pull the Mistral model
echo ""
echo "Downloading Mistral model (this may take a few minutes)..."
ollama pull mistral
echo "✓ Mistral model ready"

echo ""
echo "======================================"
echo "Setup Complete!"
echo "======================================"
echo ""
echo "Your Ollama server is running with the Mistral model loaded."
echo ""
echo "Next steps:"
echo "  1. Run your Java application:"
echo "     mvn exec:java -D\"exec.mainClass\"=\"com.example.OpenAIApp\""
echo ""
echo "To stop Ollama, run:"
echo "  kill $OLLAMA_PID"
echo ""
echo "To manually start Ollama in another terminal:"
echo "  ollama serve"
echo ""
