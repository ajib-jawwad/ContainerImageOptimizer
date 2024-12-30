# main.py
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
