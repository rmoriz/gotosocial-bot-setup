# Contributing to GoToSocial Bot Setup

Thank you for your interest in contributing to this project! This toolkit aims to simplify GoToSocial bot creation for developers.

## Development Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/rmoriz/gotosocial-bot-setup.git
   cd gotosocial-bot-setup
   ```

2. **Set up development environment:**
   ```bash
   ./setup_venv.sh
   source gotosocial_bot_env/bin/activate
   ```

3. **Run tests:**
   ```bash
   python test_setup.py
   ```

## Project Structure

- `gotosocial_token_generator.py` - Interactive OAuth flow setup
- `gotosocial_simple.py` - Automated username/password setup
- `gotosocial_bot_helper.py` - Bot operations library
- `example_bot.py` - Example bot implementation
- `test_setup.py` - Test suite
- `setup_*.sh` - Environment setup scripts

## Contributing Guidelines

### Code Style
- Follow PEP 8 Python style guidelines
- Use meaningful variable and function names
- Include docstrings for all functions and classes
- Add type hints where appropriate

### Testing
- Add tests for new functionality in `test_setup.py`
- Ensure all existing tests pass before submitting
- Test with different GoToSocial instances if possible

### Security
- Never commit credential files or tokens
- Use environment variables for sensitive data in examples
- Validate all user inputs
- Follow OAuth best practices

### Documentation
- Update README.md for new features
- Include usage examples
- Document any new dependencies
- Update SOLUTION_SUMMARY.md if architecture changes

## Types of Contributions

### Bug Fixes
- Fix issues with token generation
- Improve error handling
- Resolve compatibility problems

### Features
- Add new bot operations to the helper library
- Improve setup automation
- Add support for additional OAuth flows
- Create new example bots

### Documentation
- Improve setup instructions
- Add more usage examples
- Create video tutorials
- Translate documentation

### Testing
- Add test cases for edge cases
- Test with different GoToSocial versions
- Create integration tests
- Add performance tests

## Submitting Changes

1. **Fork the repository**
2. **Create a feature branch:**
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. **Make your changes**
4. **Test thoroughly:**
   ```bash
   python test_setup.py
   ```
5. **Commit with clear messages:**
   ```bash
   git commit -m "Add feature: description of what you added"
   ```
6. **Push to your fork:**
   ```bash
   git push origin feature/your-feature-name
   ```
7. **Create a Pull Request**

## Pull Request Guidelines

- Provide a clear description of the changes
- Reference any related issues
- Include test results
- Update documentation as needed
- Ensure no credential files are included

## Reporting Issues

When reporting bugs or requesting features:

1. **Check existing issues** first
2. **Provide clear reproduction steps** for bugs
3. **Include system information** (Python version, OS, etc.)
4. **Sanitize any logs** to remove credentials
5. **Use issue templates** when available

## Code of Conduct

- Be respectful and inclusive
- Focus on constructive feedback
- Help newcomers learn
- Maintain a welcoming environment

## Getting Help

- Check the README.md for common issues
- Look at existing issues and discussions
- Ask questions in new issues with the "question" label
- Test your setup with the provided test suite

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

Thank you for helping make GoToSocial bot setup easier for everyone! 🤖