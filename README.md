# Dockerfile Analyzer and Optimizer

A powerful tool that uses LLMs to analyze, secure, and optimize your Dockerfiles. The tool provides detailed security recommendations, optimization suggestions, and automatically generates an improved version of your Dockerfile.

## Features

- 🔍 Deep analysis of Dockerfile security issues
- ⚡ Performance optimization recommendations
- 🎯 Best practices compliance checking
- 📊 Security and optimization scoring
- 📝 Detailed markdown reports
- 🔄 Automatic generation of optimized Dockerfiles

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/dockerfile-analyzer
cd dockerfile-analyzer
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install langchain-openai pyyaml
```

4. Set up your OpenAI API key:
```bash
export OPENAI_API_KEY='your-api-key-here'  # On Windows: set OPENAI_API_KEY=your-api-key-here
```

## Usage

### Basic Usage

1. Place your Dockerfile in the project directory
2. Run the analyzer:
```bash
python dockerfile_analyzer.py
```

The tool will generate:
- A detailed analysis report (`dockerfile_analysis_report.md`)
- An optimized version of your Dockerfile (`Dockerfile.optimized`)

### Using as a Library

```python
from dockerfile_analyzer import DockerfileAnalyzer

# Initialize the analyzer
analyzer = DockerfileAnalyzer(api_key='your-api-key-here')

# Analyze a Dockerfile
result = analyzer.analyze_dockerfile('path/to/your/Dockerfile')

# Generate a report
report = analyzer.generate_report(result)

# Save the optimized Dockerfile
analyzer.save_optimized_dockerfile(result, 'Dockerfile.optimized')
```

## Analysis Features

The tool checks for:

### Security
- Base image security
- Root user usage
- Secure package installation
- Secret handling
- Permission settings
- Known vulnerabilities

### Optimization
- Multi-stage builds
- Layer optimization
- Cache utilization
- Image size reduction
- Build time improvement

### Best Practices
- Documentation
- Maintainability
- Version pinning
- Health checks
- Resource management

## Understanding the Results

### Security Score
The security score (0-100) considers:
- Critical security issues
- Base image security
- Permission configurations
- Secret management
- Network security

### Optimization Score
The optimization score (0-100) evaluates:
- Build efficiency
- Image size
- Layer management
- Cache usage
- Resource efficiency

## Example Report

The generated report includes:
```markdown
# Dockerfile Analysis Report

## Scores
Security Score: 85/100
Optimization Score: 78/100

## Issues Found

### HIGH Severity Issues
**security**
- Description: Running as root user
- Recommendation: Add 'USER nonroot' instruction
- Line Number: 1

[...]
```
