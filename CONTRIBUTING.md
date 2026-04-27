# Contributing to Tendril

Thanks for your interest in contributing! Here's how to get started.

## Getting Started

1. **Fork** the repository
2. **Clone** your fork locally
3. **Create a branch** for your feature or fix
4. **Make your changes** and test them
5. **Submit a pull request**

## Development Setup

### API (Python / FastAPI)

```bash
cd api
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
```

### Web (TypeScript / Next.js)

```bash
cd web
npm install
npm run dev
```

### ESP32 Firmware (C++ / PlatformIO)

```bash
cd esp32
cp src/config.example.h src/config.h   # Edit with your settings
pio run
```

## OpenSpec Workflow

This project uses [OpenSpec](openspec/AGENTS.md) for spec-driven development. For larger changes:

1. **Create a proposal** in `openspec/changes/` describing your change
2. **Get feedback** via a PR or discussion before implementing
3. **Implement** once the proposal is approved
4. **Archive** the change after it ships

See [openspec/AGENTS.md](openspec/AGENTS.md) for the full workflow.

## Guidelines

- Keep PRs focused — one feature or fix per PR
- Write tests for new functionality
- Follow existing code style and conventions
- Update documentation when changing behavior

## Reporting Issues

Open an issue with:
- A clear description of the problem or feature request
- Steps to reproduce (for bugs)
- Expected vs. actual behavior

## License

By contributing, you agree that your contributions will be licensed under the project's dual license:

- **API, Web, and infrastructure** — [AGPL-3.0](LICENSE)
- **ESP32 firmware** (`esp32/`) — [MIT](esp32/LICENSE)
