.PHONY: help install setup run clean api-key

# Default target
help:
	@echo "╔════════════════════════════════════════════════════════════════╗"
	@echo "║     Semantic Search Module with Gemini Enhancement             ║"
	@echo "╚════════════════════════════════════════════════════════════════╝"
	@echo ""
	@echo "Available commands:"
	@echo ""
	@echo "  make setup      - Install dependencies and configure Gemini API key"
	@echo "  make run        - Run the application on http://localhost:8000"
	@echo "  make install    - Install Python dependencies only"
	@echo "  make api-key    - Prompt for and save Gemini API key"
	@echo "  make clean      - Remove virtual environment and cache files"
	@echo "  make help       - Show this help message"
	@echo ""

# Install dependencies
install:
	@echo "📦 Installing Python dependencies..."
	@pip install --upgrade pip setuptools wheel
	@pip install -r requirements.txt
	@echo "✅ Dependencies installed successfully!"

# Setup API key
api-key:
	@echo "🔑 Gemini API Key Configuration"
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
	@echo ""
	@read -p "Enter your Gemini API key in order to  enhance retrieval quality through intelligent query rewriting before embedding generation (or press Enter to skip): " api_key; \
	if [ -n "$$api_key" ]; then \
		echo "GEMINI_API_KEY=$$api_key" > .env; \
		echo ""; \
		echo "✅ API key saved to .env file!"; \
	else \
		echo ""; \
		echo "⚠️  No API key provided. LLM features will be disabled."; \
	fi
	@echo ""

# Full setup: install dependencies and configure API key
setup: install api-key
	@echo ""
	@echo "╔════════════════════════════════════════════════════════════════╗"
	@echo "║              Setup Complete! 🎉                               ║"
	@echo "║                                                                ║"
	@echo "║  You can now run the application with: make run               ║"
	@echo "╚════════════════════════════════════════════════════════════════╝"
	@echo ""

# Run the application
run:
	@if [ ! -f ".env" ]; then \
		echo "⚠️  .env file not found!"; \
		echo "Running: make api-key"; \
		echo ""; \
		make api-key; \
	fi
	@echo ""
	@echo "🚀 Starting Semantic Search Application..."
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
	@echo ""
	@echo "📍 Application running at: http://localhost:8000"
	@echo ""
	@echo "📚 API Documentation available at:"
	@echo "   • Swagger UI: http://localhost:8000/docs"
	@echo "   • ReDoc: http://localhost:8000/redoc"
	@echo ""
	@echo "Press Ctrl+C to stop the server"
	@echo ""
	@uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Clean up
clean:
	@echo "🧹 Cleaning up..."
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete
	@find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	@rm -rf .env
	@echo "✅ Cleanup complete!"
	@echo ""
