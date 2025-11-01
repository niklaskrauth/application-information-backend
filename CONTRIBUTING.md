# Contributing to Application Information Backend

Thank you for considering contributing to this project! Here are some guidelines to help you get started.

## Development Setup

1. Fork the repository
2. Clone your fork:
   ```bash
   git clone https://github.com/YOUR_USERNAME/application-information-backend.git
   cd application-information-backend
   ```

3. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

5. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

6. Run validation tests:
   ```bash
   python validate.py
   ```

## Code Style

- Follow PEP 8 style guide
- Use type hints where appropriate
- Write docstrings for all functions and classes
- Keep functions small and focused

### Formatting Tools

```bash
# Install formatting tools
pip install black isort flake8

# Format code
black app/
isort app/

# Check for issues
flake8 app/
```

## Testing

- Write tests for new features
- Ensure all tests pass before submitting PR
- Aim for good test coverage

```bash
pytest
```

## Pull Request Process

1. Create a feature branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes and commit:
   ```bash
   git add .
   git commit -m "Description of your changes"
   ```

3. Push to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```

4. Open a Pull Request on GitHub

### PR Guidelines

- Provide a clear description of the changes
- Reference any related issues
- Ensure code is properly formatted
- Update documentation if needed
- Add tests for new functionality

## Reporting Issues

- Use the GitHub issue tracker
- Provide a clear description of the issue
- Include steps to reproduce
- Mention your environment (OS, Python version, etc.)

## Questions?

Feel free to open an issue for any questions or concerns!
