# Dockerfile Analyzer

A Python tool that uses LangChain and OpenAI's GPT-4 to analyze Dockerfiles for security and optimization opportunities. This tool provides detailed reports including security scores, optimization metrics, and suggestions for improvements.

## Features

- Security analysis with scoring
- Optimization metrics calculation
- Cache efficiency evaluation
- Build time analysis
- Maintainability scoring
- Detailed recommendations
- Optimized Dockerfile generation

## Installation

1. Create a new directory for your project and set up a Python virtual environment:

```bash
git clone git@github.com:ajib-jawwad/dockerfile-analyzer.git
cd dockerfile-analyzer
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
```

2. Install required packages:

```bash
pip install langchain-openai langchain-core langchain-community openai
```

## Project Structure

```
dockerfile-analyzer/
├── venv/
├── dockerfile_analyzer.py
├── main.py
└── Dockerfile
```

## Configuration

Before running the analyzer, you need to set up your OpenAI API key:

```bash
# On Unix/Linux/MacOS
export OPENAI_API_KEY='your-api-key-here'

# On Windows (Command Prompt)
set OPENAI_API_KEY=your-api-key-here

# On Windows (PowerShell)
$env:OPENAI_API_KEY='your-api-key-here'
```

## Usage

1. Create a Dockerfile you want to analyze. Example:

```dockerfile
FROM python:3.9
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "app.py"]
```

2. Run the analyzer:

```bash
python main.py
```

The tool will generate a report containing:
- Security Score (0-100)
- Optimization Score (0-100)
- Optimization Metrics:
  - Layer Count
  - Estimated Size
  - Cache Efficiency
  - Build Time Score
  - Maintainability Score
- Detailed Report
- Optimized Dockerfile

## Code Components

### Main Script (main.py)

```python
import os
from dockerfile_analyzer import DockerfileAnalyzer

def main():
    # Get API key from environment variable
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        raise ValueError("Please set the OPENAI_API_KEY environment variable")

    try:
        # Initialize the analyzer
        analyzer = DockerfileAnalyzer(openai_api_key=api_key)

        # Analyze the Dockerfile
        result = analyzer.analyze_dockerfile("./Dockerfile")

        # Generate and print the report
        report = analyzer.generate_report(result)
        print(report)

    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()
```

### Analyzer Class (dockerfile_analyzer.py)

The `DockerfileAnalyzer` class handles:
- Dockerfile parsing
- LLM interaction
- Analysis processing
- Report generation

## Example Output

The tool generates a formatted report that looks like this:

```markdown
## Dockerfile Analysis Report

### Scores
- Security Score: 85/100
- Optimization Score: 78/100

### Optimization Metrics
- Layer Count: 5
- Estimated Size: 985MB
- Cache Efficiency: 90/100
- Build Time Score: 85/100
- Maintainability Score: 88/100

### Detailed Report
[Detailed analysis of the Dockerfile]

### Optimized Dockerfile
[Optimized version of the input Dockerfile]
```

## Troubleshooting

If you encounter any issues:

1. Ensure all required packages are installed:
```bash
pip install langchain-openai langchain-core langchain-community openai
```

2. Verify your OpenAI API key is set correctly in your environment variables

3. Check that your Dockerfile exists in the specified path

## Dependencies

- langchain-openai
- langchain-core
- langchain-community
- openai
- Python 3.7+
