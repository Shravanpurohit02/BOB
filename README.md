# Vidhi Builder (BOB)

**Production AI Software Engineering Platform**

Status: Stage 1 - Builder Kernel (Alpha)

## Overview

Vidhi Builder is an advanced software engineering platform that leverages AI to assist with code generation, analysis, and autonomous development workflows. It provides a comprehensive suite of tools for understanding, analyzing, and transforming codebases.

## Features

- **Code Analysis**: Deep AST parsing and symbol resolution
- **Dependency Management**: Comprehensive dependency tracking and graph analysis
- **Context Intelligence**: Smart context retrieval for code generation
- **Autonomous Runtime**: Execute autonomous code development workflows
- **Repository Engineering**: Advanced repository analysis and transformation
- **Code Generation**: AI-powered code generation and refactoring
- **Testing Framework**: Integrated testing and regression suites
- **Configuration Management**: Environment-based configuration system

## Project Structure

```
builder/
  ├── ast/              AST parsing and symbol extraction
  ├── bootstrap/        Application initialization
  ├── cli/              Command-line interface
  ├── config/           Configuration management
  ├── context/          Context intelligence engine
  ├── core/             Core data structures
  ├── dependency/       Dependency graph management
  ├── domain/           Domain models
  ├── engineering/      Code engineering operations
  ├── execution/        Execution runtime
  ├── filesystem/       File system operations
  ├── graph/            Graph data structures
  ├── guardrails/       Safety validators
  ├── intelligence/     Symbol and dependency intelligence
  ├── kernel/           Kernel operations
  ├── knowledge/        Knowledge base
  ├── logging/          Logging configuration
  ├── models/           Data models
  ├── orchestrator/     Workflow orchestration
  ├── patch/            Code patching utilities
  ├── pipeline/         Processing pipelines
  ├── planning/         Task planning
  ├── project/          Project management
  ├── project_graph/    Project-wide graph
  ├── providers/        Provider implementations
  ├── reflection/       Code reflection and indexing
  ├── regression/       Regression test suites
  ├── repository/       Repository operations
  ├── review/           Code review tools
  ├── runtime/          Runtime environment
  ├── self_improvement/ Self-improvement mechanisms
  ├── staging/          Staging area management
  ├── testing/          Testing utilities
  ├── tools/            Tool implementations
  ├── utils/            Utility functions
  └── validation/       Input validation

tests/
  ├── unit/             Unit tests
  ├── integration/       Integration tests
  └── regression/        Regression tests
```

## Installation

### Prerequisites

- Python 3.12 or higher
- pip or uv package manager

### Setup

1. Clone the repository:
```bash
git clone https://github.com/Shravanpurohit02/BOB.git
cd BOB
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -e .
```

### Configuration

Copy `.env.example` to `.env` and configure as needed:

```bash
cp .env.example .env
```

Edit `.env` with your settings:
```env
ENV=development
LOG_LEVEL=INFO
STATE_DIR=state
CACHE_DIR=cache
WORKSPACE_DIR=workspace
```

## Usage

### Running the Application

```bash
vidhi-builder
```

### Using as a Library

```python
from builder.context import ContextEngine
from builder.intelligence import SymbolIndexer

# Initialize components
context_engine = ContextEngine()
indexer = SymbolIndexer()

# Use the APIs
```

## Development

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=builder tests/

# Run specific test file
pytest tests/unit/test_context.py

# Run in watch mode
pytest-watch
```

### Code Quality

```bash
# Format code
black builder/ tests/

# Lint
ruff check builder/ tests/

# Type checking
mypy builder/
```

## Architecture

### Core Concepts

1. **Context Engine**: Manages contextual information for code generation
2. **Intelligence System**: Analyzes code structure, dependencies, and relationships
3. **Repository Operations**: Handles repository analysis and transformation
4. **Execution Runtime**: Executes autonomous development workflows
5. **Orchestrator**: Coordinates multi-step development tasks

### Data Flow

```
Repository Input
    ↓
Repository Indexing (reflection/)
    ↓
Symbol Analysis (intelligence/)
    ↓
Context Assembly (context/)
    ↓
Code Generation (codegen/)
    ↓
Validation (guardrails/, validation/)
    ↓
Execution (execution/)
    ↓
Output
```

## Dependencies

Key dependencies are managed in `pyproject.toml`:

- **typer** (0.16+): CLI framework
- **pydantic** (2.11+): Data validation
- **networkx** (3.5+): Graph algorithms
- **sqlalchemy** (2.0+): Database ORM
- **httpx** (0.28+): Async HTTP client
- **loguru** (0.7+): Logging
- **pyyaml** (6.0+): Configuration parsing

## Contributing

Please see [CONTRIBUTING.md](CONTRIBUTING.md) for contribution guidelines.

## License

Proprietary - See LICENSE file for details

## Support

For issues and questions, please open an issue on the [GitHub repository](https://github.com/Shravanpurohit02/BOB/issues).
