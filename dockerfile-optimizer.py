import os
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
import json
import re
from pathlib import Path

@dataclass
class DockerfileIssue:
    severity: str
    category: str
    description: str
    recommendation: str
    line_number: Optional[int] = None

@dataclass
class OptimizationMetrics:
    layer_count: int
    estimated_size: str
    cache_efficiency: int
    build_time_score: int
    maintainability_score: int

@dataclass
class AnalysisResult:
    issues: List[DockerfileIssue]
    optimized_dockerfile: str
    security_score: int
    optimization_score: int
    optimization_metrics: OptimizationMetrics

class DockerfileOptimizer:
    """Advanced Dockerfile optimization strategies"""
    
    @staticmethod
    def optimize_apt_commands(dockerfile_content: str) -> str:
        """Optimize apt-get commands for better caching and smaller layers."""
        # Combine multiple apt-get commands
        apt_pattern = r'RUN apt-get update.*?(?=\n[^\n]|$)'
        apt_commands = re.findall(apt_pattern, dockerfile_content, re.DOTALL)
        
        if apt_commands:
            combined_command = 'RUN apt-get update && \\\n'
            combined_command += '    DEBIAN_FRONTEND=noninteractive \\\n'
            combined_command += '    apt-get install -y --no-install-recommends \\\n'
            
            # Extract package names from all commands
            packages = set()
            for cmd in apt_commands:
                pkg_matches = re.findall(r'install -y\s+(.+?)[\s\\]*\n', cmd)
                packages.update(pkg_matches[0].split() if pkg_matches else [])
            
            # Add packages and cleanup
            combined_command += '        ' + ' \\\n        '.join(sorted(packages)) + ' \\\n'
            combined_command += '    && apt-get clean \\\n'
            combined_command += '    && rm -rf /var/lib/apt/lists/*'
            
            # Replace all apt commands with optimized version
            for cmd in apt_commands:
                dockerfile_content = dockerfile_content.replace(cmd, '')
            dockerfile_content = re.sub(r'\n\n+', '\n\n', dockerfile_content)
            
            # Insert optimized command after FROM
            from_idx = dockerfile_content.find('\n', dockerfile_content.find('FROM'))
            dockerfile_content = dockerfile_content[:from_idx] + '\n' + combined_command + dockerfile_content[from_idx:]
            
        return dockerfile_content

    @staticmethod
    def optimize_pip_commands(dockerfile_content: str) -> str:
        """Optimize pip install commands for better caching."""
        # Combine multiple pip install commands
        pip_pattern = r'RUN (?:pip|pip3) install.*?(?=\n[^\n]|$)'
        pip_commands = re.findall(pip_pattern, dockerfile_content, re.DOTALL)
        
        if pip_commands:
            # Create requirements.txt approach
            combined_command = 'COPY requirements.txt /tmp/\n'
            combined_command += 'RUN pip install --no-cache-dir -r /tmp/requirements.txt && \\\n'
            combined_command += '    rm /tmp/requirements.txt'
            
            # Extract package names
            packages = set()
            for cmd in pip_commands:
                pkg_matches = re.findall(r'install\s+(.+?)[\s\\]*\n', cmd)
                packages.update(pkg_matches[0].split() if pkg_matches else [])
            
            # Create requirements.txt
            with open('requirements.txt', 'w') as f:
                f.write('\n'.join(sorted(packages)))
            
            # Replace pip commands
            for cmd in pip_commands:
                dockerfile_content = dockerfile_content.replace(cmd, '')
            dockerfile_content = re.sub(r'\n\n+', '\n\n', dockerfile_content)
            
            # Insert optimized command after FROM
            from_idx = dockerfile_content.find('\n', dockerfile_content.find('FROM'))
            dockerfile_content = dockerfile_content[:from_idx] + '\n' + combined_command + dockerfile_content[from_idx:]
            
        return dockerfile_content

    @staticmethod
    def optimize_copy_commands(dockerfile_content: str) -> Tuple[str, List[str]]:
        """Optimize COPY commands and generate .dockerignore entries."""
        dockerignore_entries = [
            '.git',
            '.gitignore',
            'Dockerfile',
            '.dockerignore',
            '__pycache__',
            '*.pyc',
            '*.pyo',
            '*.pyd',
            '.Python',
            'env',
            'pip-log.txt',
            'pip-delete-this-directory.txt',
            '.tox',
            '.coverage',
            '.coverage.*',
            'htmlcov',
            '.pytest_cache',
            '.env',
            '.venv',
            'venv',
            'node_modules',
            'npm-debug.log'
        ]
        
        # Optimize COPY commands
        copy_pattern = r'COPY\s+(.+?)\s+(.+?)[\s\\]*\n'
        copy_commands = re.findall(copy_pattern, dockerfile_content)
        
        if copy_commands:
            # Group COPY commands by destination
            copy_groups = {}
            for src, dest in copy_commands:
                if dest not in copy_groups:
                    copy_groups[dest] = []
                copy_groups[dest].append(src)
            
            # Replace with optimized COPY commands
            for cmd_src, cmd_dest in copy_commands:
                dockerfile_content = dockerfile_content.replace(
                    f'COPY {cmd_src} {cmd_dest}',
                    ''
                )
            
            # Add optimized commands
            optimized_copies = []
            for dest, sources in copy_groups.items():
                if len(sources) == 1:
                    optimized_copies.append(f'COPY {sources[0]} {dest}')
                else:
                    sources_str = ' '.join(sources)
                    optimized_copies.append(f'COPY {sources_str} {dest}/')
            
            # Insert optimized commands
            copy_insert_point = dockerfile_content.find('CMD')
            if copy_insert_point == -1:
                copy_insert_point = len(dockerfile_content)
            
            dockerfile_content = (
                dockerfile_content[:copy_insert_point] +
                '\n'.join(optimized_copies) +
                '\n' +
                dockerfile_content[copy_insert_point:]
            )
        
        return dockerfile_content, dockerignore_entries

    @staticmethod
    def add_build_optimization_args(dockerfile_content: str) -> str:
        """Add ARG instructions for build optimization."""
        build_args = """# Build arguments for optimization
ARG BUILDKIT_INLINE_CACHE=1
ARG DOCKER_BUILDKIT=1
"""
        return build_args + dockerfile_content

class DockerfileAnalyzer:
    def __init__(self, api_key: str):
        self.llm = ChatOpenAI(
            model_name="gpt-4",
            openai_api_key=api_key,
            temperature=0.2
        )
        self.optimizer = DockerfileOptimizer()
        self._init_prompts()

    def _init_prompts(self):
        """Initialize the analysis and optimization prompts."""
        self.analysis_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a Dockerfile security and optimization expert. Analyze the provided Dockerfile and provide:
            1. Security issues and recommendations
            2. Optimization opportunities
            3. Best practices violations
            4. An improved version of the Dockerfile
            
            Consider these advanced optimization strategies:
            - Multi-stage builds for compiled languages
            - Layer optimization and caching
            - Proper ordering of commands
            - Use of build arguments
            - Efficient package management
            - Resource constraints
            - Build context optimization
            
            Format your response as a JSON with this structure:
            {
                "issues": [
                    {
                        "severity": "high/medium/low",
                        "category": "security/optimization/best_practices",
                        "description": "Detailed description of the issue",
                        "recommendation": "Specific fix recommendation",
                        "line_number": optional_line_number
                    }
                ],
                "optimized_dockerfile": "Complete improved Dockerfile content",
                "security_score": "1-100 score",
                "optimization_score": "1-100 score",
                "optimization_metrics": {
                    "layer_count": "number of layers",
                    "estimated_size": "estimated image size",
                    "cache_efficiency": "1-100 score",
                    "build_time_score": "1-100 score",
                    "maintainability_score": "1-100 score"
                }
            }"""),
            ("user", "{dockerfile_content}")
        ])

    def analyze_dockerfile(self, dockerfile_path: str) -> AnalysisResult:
        """Analyze and optimize a Dockerfile."""
        try:
            # Read Dockerfile
            with open(dockerfile_path, 'r') as file:
                content = file.read()
            
            # Apply optimization strategies
            content = self.optimizer.optimize_apt_commands(content)
            content = self.optimizer.optimize_pip_commands(content)
            content, dockerignore_entries = self.optimizer.optimize_copy_commands(content)
            content = self.optimizer.add_build_optimization_args(content)
            
            # Save .dockerignore if it doesn't exist
            dockerignore_path = Path(dockerfile_path).parent / '.dockerignore'
            if not dockerignore_path.exists():
                with open(dockerignore_path, 'w') as f:
                    f.write('\n'.join(dockerignore_entries))
            
            # Get analysis from LLM
            response = self.llm.invoke(
                self.analysis_prompt.format(dockerfile_content=content)
            )
            
            # Parse response
            analysis = json.loads(response.content)
            
            # Convert to AnalysisResult
            issues = [DockerfileIssue(**issue) for issue in analysis["issues"]]
            metrics = OptimizationMetrics(**analysis["optimization_metrics"])
            
            return AnalysisResult(
                issues=issues,
                optimized_dockerfile=analysis["optimized_dockerfile"],
                security_score=analysis["security_score"],
                optimization_score=analysis["optimization_score"],
                optimization_metrics=metrics
            )
            
        except Exception as e:
            raise Exception(f"Error analyzing Dockerfile: {str(e)}")

    def generate_report(self, result: AnalysisResult) -> str:
        """Generate a detailed analysis report."""
        report = "# Dockerfile Analysis Report\n\n"
        
        # Add scores and metrics
        report += "## Overall Scores\n"
        report += f"Security Score: {result.security_score}/100\n"
        report += f"Optimization Score: {result.optimization_score}/100\n\n"
        
        report += "## Optimization Metrics\n"
        report += f"- Layer Count: {result.optimization_metrics.layer_count}\n"
        report += f"- Estimated Image Size: {result.optimization_metrics.estimated_size}\n"
        report += f"- Cache Efficiency: {result.optimization_metrics.cache_efficiency}/100\n"
        report += f"- Build Time Score: {result.optimization_metrics.build_time_score}/100\n"
        report += f"- Maintainability Score: {result.optimization_metrics.maintainability_score}/100\n\n"
        
        # Add issues grouped by severity
        report += "## Issues Found\n\n"
        
        severity_order = {"high": 1, "medium": 2, "low": 3}
        sorted_issues = sorted(
            result.issues,
            key=lambda x: (severity_order.get(x.severity.lower(), 4), x.category)
        )
        
        current_severity = None
        for issue in sorted_issues:
            if issue.severity != current_severity:
                current_severity = issue.severity
                report += f"### {issue.severity.upper()} Severity Issues\n\n"
            
            report += f"**{issue.category}**\n"
            report += f"- Description: {issue.description}\n"
            report += f"- Recommendation: {issue.recommendation}\n"
            if issue.line_number:
                report += f"- Line Number: {issue.line_number}\n"
            report += "\n"
        
        return report

def main():
    # Initialize analyzer
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("Please set OPENAI_API_KEY environment variable")
    
    analyzer = DockerfileAnalyzer(api_key)
    
    # Example Dockerfile analysis
    dockerfile_path = "Dockerfile"
    if not os.path.exists(dockerfile_path):
        print(f"Creating example Dockerfile at {dockerfile_path}")
        with open(dockerfile_path, "w") as f:
            f.write("""FROM ubuntu:latest
RUN apt-get update && apt-get install -y python3
RUN apt-get update && apt-get install -y nginx
RUN pip3 install flask
RUN pip3 install requests
COPY app.py /app/
RUN chmod +x /app/app.py
EXPOSE 8080
CMD ["/app/app.py"]""")
    
    # Analyze Dockerfile
    print("Analyzing Dockerfile...")
    result = analyzer.analyze_dockerfile(dockerfile_path)
    
    # Generate and save report
    report = analyzer.generate_report(result)
    with open("dockerfile_analysis_report.md", "w") as f:
        f.write(report)
    
    # Save optimized Dockerfile
    with open("Dockerfile.optimized", "w") as f:
        f.write(result.optimized_dockerfile)
    
    print("\nAnalysis complete!")
    print(f"Security Score: {result.security_score}/100")
    print(f"Optimization Score: {result.optimization_score}/100")
    print("\nOptimization Metrics:")
    print(f"- Layer Count: {result.optimization_metrics.layer_count}")
    print(f"- Estimated Size: {result.optimization_metrics.estimated_size}")
    print(f"- Cache Efficiency: {result.optimization_metrics.cache_efficiency}/100")
    print(f"- Build Time Score: {result.optimization_metrics.build_time_score}/100")
    print(f"- Maintainability Score: {result.optimization_metrics.maintainability_score}/100")
    print("\nCheck dockerfile_analysis_report.md for detailed results")
    print("Check Dockerfile.optimized for the improved version")

if __name__ == "__main__":
    main()
