# NOVA (Neuro-symbolic Optimized Versatile Agent)

NOVA is a knowledge distillation system that extracts domain-specific knowledge and trains compact models while maintaining high performance.

## Features

- 🧠 Knowledge Extraction: Extract structured knowledge from any domain
- 🎯 Model Distillation: Train compact models that preserve essential knowledge
- 📊 Performance Validation: Ensure models meet accuracy and efficiency targets
- 💾 Caching System: Optimize performance with intelligent caching
- 🔄 Streaming Support: Process large-scale data efficiently

## Installation

### Using Docker

```bash
# Build the Docker image
docker build -t nova .

# Run NOVA with Docker
docker run -it --rm \
  -v $(pwd)/.nova_cache:/app/.nova_cache \
  -e OPENROUTER_API_KEY=your_key_here \
  nova distill \
  --domain "computer_science" \
  --prompt "Explain distributed systems" \
  --architecture transformer_tiny
```

### Manual Installation

```bash
# Clone the repository
git clone <repository-url>
cd nova

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
export OPENROUTER_API_KEY=your_key_here

# Run NOVA
python -m nova.distillation.cli distill \
  --domain "computer_science" \
  --prompt "Explain distributed systems" \
  --architecture transformer_tiny
```

## Configuration

### Environment Variables

- `OPENROUTER_API_KEY`: Your OpenRouter API key for LLM access
- `E2B_API_KEY`: (Optional) E2B API key for sandbox environments
- `SLACK_BOT_TOKEN`: (Optional) Slack integration for notifications
- `EMAIL_SMTP_SERVER`: (Optional) SMTP server for email notifications

### Model Architectures

- `transformer_tiny`: 60M parameters, optimized for efficiency
  - Quantization: int8
  - Pruning: magnitude-based
  - Distillation: progressive
  
- `transformer_small`: 250M parameters, balanced performance
  - Quantization: float16
  - Pruning: structured
  - Distillation: vanilla

## Usage Examples

### Basic Knowledge Distillation

```bash
python -m nova.distillation.cli distill \
  --domain "computer_science" \
  --prompt "Explain distributed systems" \
  --architecture transformer_tiny
```

### List Available Models

```bash
python -m nova.distillation.cli list
```

### Show Model Information

```bash
python -m nova.distillation.cli info transformer_tiny
```

## Performance Thresholds

- Accuracy: Minimum 0.7 (target 0.85)
- Latency: Maximum 200ms (target 100ms)
- Memory Usage: Maximum 2000MB (target 1000MB)
- Knowledge Coverage: Minimum 0.6 (target 0.8)

## Development

### Running Tests

```bash
pytest tests/
```

### Code Style

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run linters
flake8 nova/
black nova/
isort nova/
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
