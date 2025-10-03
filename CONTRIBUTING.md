# Contributing to InstaCheck 👋

Welcome! 🚀 We’re thrilled you’re considering contributing to **InstaCheck**, a privacy-first Chrome extension for real-time Instagram Reel fact-checking.

## Hacktoberfest 2025 Participation 🎉

This repository is participating in Hacktoberfest 2025! Whether you’re a student, first-timer, or seasoned developer, your contributions are valued.

- Ensure you are registered at [Hacktoberfest.com](https://hacktoberfest.com)
- All valid PRs with the `hacktoberfest` topic and label count for the event.
- Be respectful and collaborative—open-source is for everyone!

***

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How to Contribute](#how-to-contribute)
- [Reporting Issues](#reporting-issues)
- [Suggesting Enhancements](#suggesting-enhancements)
- [Making a Pull Request](#making-a-pull-request)
- [Development Guidelines](#development-guidelines)
- [Commit Messages](#commit-messages)
- [Style Guide](#style-guide)
- [Project Setup](#project-setup)
- [License](#license)

***

## Code of Conduct

Please review our [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md); we are committed to providing a welcoming and harassment-free experience for everyone.

***

## How to Contribute

**All contributions are welcome:** bug fixes, documentation improvements, new features, refactoring, tests, and security suggestions!

1. **Fork the repository**
2. **Clone your fork:**  
   ```bash
   git clone https://github.com/aniketraut16/instacheck
   ```
3. **Create your feature branch:**  
   ```bash
   git checkout -b feature/your-feature-name
   ```
4. **Commit your changes** (see [Commit Messages](#commit-messages))
5. **Push to your fork:**  
   ```bash
   git push origin feature/your-feature-name
   ```
6. **Open a Pull Request** (PR) on GitHub for review & discussion

***

## Reporting Issues

- Use [GitHub Issues](https://github.com/aniketraut16/instacheck/issues) for bugs, improvements, security concerns, and feature requests.
- Please provide:
  - Clear explanation and reproducible steps
  - System setup details: OS, Python version, browser
  - Logs, screenshots, or error messages as relevant
- No duplicate issues. Search before creating.

***

## Suggesting Enhancements

Open an issue with:
- A clear title and detailed description
- Why your suggestion improves InstaCheck for users/maintainers
- If possible, reference existing solutions or prior art

***

## Making a Pull Request

- Use descriptive titles and reference related issues (e.g. `Fixes #42`)
- Only one feature/fix per pull request
- Check your code against the [Style Guide](#style-guide)
- Write tests if applicable
- Document your changes (README, code comments)
- Include usage/setup notes for significant changes
- Small PRs = faster review!

***

## Development Guidelines

- **Python code:** Use type hints, docstrings, and follow module structure conventions.
- **Chrome Extension:** Ensure manifest and front-end JS/CSS follow best practices for privacy and security.
- **Tests:** All new features/fixes must include relevant unit or integration tests.
- **Documentation:** Add or update docstrings, Markdown docs, or comments.
- **Docker:** If changing the build/setup process, update relevant `Dockerfile` or `docker-compose` docs and instructions.

***

## Commit Messages

Follow Conventional Commits whenever possible:

```
feat: add new claim extraction method
fix: resolve error in Whisper transcription
docs: update installation instructions for Docker
test: add unit tests for vector DB integration
refactor: simplify API call structure
```

***

## Style Guide

- **Python:** PEP8 formatting, use `black` for auto-formatting, `isort` for import sorting.
- **JavaScript:** Standard JS, semicolons preferred.
- **Markdown:** Use headers, lists, and code blocks for clarity.
- **Comments:** Keep them concise and informative.

***

## Project Setup

See [README.md](README.md) for installation and usage instructions. For development:

- Configuration: Edit `core/config.py` for LLM provider settings.
- Environment: Use `.env` for keys (see example in README).

Quick start for Docker:
```bash
docker compose -f docker-compose.dev.yml up --build
```

Chrome extension development:
- Load from `extension/` folder in Chrome Dev mode

***

## License

All contributions will be governed under the [Apache-2.0](LICENSE) license.

***

## Maintainer

Maintained by [@aniketraut16](https://github.com/aniketraut16). Feel free to reach out via GitHub issues/discussions for help or collaboration!

***

Happy Hacking and Verifying! 🛡️  
**Star the repo, share with friends, and let’s make Instagram safer together.**

ributing/)
