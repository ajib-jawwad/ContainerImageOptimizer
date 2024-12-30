import json
import re
from dataclasses import dataclass
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.runnables import RunnablePassthrough

@dataclass
class OptimizationMetrics:
    layer_count: int
    estimated_size: str
    cache_efficiency: int
    build_time_score: int
    maintainability_score: int

@dataclass
class AnalysisResult:
    security_score: int
    optimization_score: int
    optimization_metrics: OptimizationMetrics
    detailed_report: str
    optimized_dockerfile: str

class DockerfileAnalyzer:
    def __init__(self, openai_api_key):
        self.llm = ChatOpenAI(
            temperature=0,
            openai_api_key=openai_api_key,
            model_name="gpt-4"
        )
        self.output_parser = JsonOutputParser()

    def analyze_dockerfile(self, dockerfile_path):
        """Analyzes a Dockerfile and provides optimization and security insights."""
        try:
            with open(dockerfile_path, 'r') as f:
                dockerfile_content = f.read()
        except FileNotFoundError:
            raise FileNotFoundError(f"Dockerfile not found at path: {dockerfile_path}")
        except Exception as e:
            raise Exception(f"Error reading Dockerfile: {str(e)}")

        prompt_template = """
        You are a Dockerfile expert. Analyze the following Dockerfile and provide your analysis in the exact JSON format specified below.

        Dockerfile to analyze:
        {dockerfile_content}

        Provide a JSON response with this exact structure:
        {{
            "security_score": <number between 0-100>,
            "optimization_score": <number between 0-100>,
            "optimization_metrics": {{
                "layer_count": <positive integer>,
                "estimated_size": "<string with size estimate>",
                "cache_efficiency": <number between 0-100>,
                "build_time_score": <number between 0-100>,
                "maintainability_score": <number between 0-100>
            }},
            "detailed_report": "<detailed analysis string>",
            "optimized_dockerfile": "<optimized dockerfile string>"
        }}
        """

        prompt = PromptTemplate(
            input_variables=["dockerfile_content"],
            template=prompt_template
        )

        try:
            # Create the chain using the new pipe syntax
            chain = (
                {"dockerfile_content": RunnablePassthrough()}
                | prompt
                | self.llm
                | self.output_parser
            )

            # Invoke the chain
            response_data = chain.invoke(dockerfile_content)

            # Create a result object
            result = AnalysisResult(
                security_score=response_data["security_score"],
                optimization_score=response_data["optimization_score"],
                optimization_metrics=OptimizationMetrics(
                    layer_count=response_data["optimization_metrics"]["layer_count"],
                    estimated_size=response_data["optimization_metrics"]["estimated_size"],
                    cache_efficiency=response_data["optimization_metrics"]["cache_efficiency"],
                    build_time_score=response_data["optimization_metrics"]["build_time_score"],
                    maintainability_score=response_data["optimization_metrics"]["maintainability_score"],
                ),
                detailed_report=response_data["detailed_report"],
                optimized_dockerfile=response_data["optimized_dockerfile"],
            )

            return result

        except json.JSONDecodeError as e:
            print(f"Error parsing JSON response: {str(e)}")
            print("Falling back to regex parsing...")
            return self._extract_data_from_response(str(response_data))
        except Exception as e:
            raise Exception(f"Error during analysis: {str(e)}")

    def _extract_data_from_response(self, response):
        """Extracts data from the LLM response using regex as a fallback."""
        data = {
            "security_score": 0,
            "optimization_score": 0,
            "optimization_metrics": {
                "layer_count": 0,
                "estimated_size": "unknown",
                "cache_efficiency": 0,
                "build_time_score": 0,
                "maintainability_score": 0
            },
            "detailed_report": "",
            "optimized_dockerfile": ""
        }

        patterns = {
            "security_score": r"Security Score:?\s*(\d+)",
            "optimization_score": r"Optimization Score:?\s*(\d+)",
            "layer_count": r"Layer Count:?\s*(\d+)",
            "estimated_size": r"Estimated Size:?\s*([^\n]+)",
            "cache_efficiency": r"Cache Efficiency:?\s*(\d+)",
            "build_time_score": r"Build Time Score:?\s*(\d+)",
            "maintainability_score": r"Maintainability Score:?\s*(\d+)"
        }

        for key, pattern in patterns.items():
            match = re.search(pattern, response, re.IGNORECASE)
            if match:
                if key == "estimated_size":
                    data["optimization_metrics"][key] = match.group(1).strip()
                elif key in data["optimization_metrics"]:
                    data["optimization_metrics"][key] = int(match.group(1))
                else:
                    data[key] = int(match.group(1))

        detailed_report_match = re.search(r"Detailed Report:?\s*(.+?)(?=Optimized Dockerfile:|$)", response, re.DOTALL)
        if detailed_report_match:
            data["detailed_report"] = detailed_report_match.group(1).strip()

        optimized_dockerfile_match = re.search(r"Optimized Dockerfile:?\s*(.+)$", response, re.DOTALL)
        if optimized_dockerfile_match:
            data["optimized_dockerfile"] = optimized_dockerfile_match.group(1).strip()

        return AnalysisResult(
            security_score=data["security_score"],
            optimization_score=data["optimization_score"],
            optimization_metrics=OptimizationMetrics(**data["optimization_metrics"]),
            detailed_report=data["detailed_report"],
            optimized_dockerfile=data["optimized_dockerfile"]
        )

    def generate_report(self, result):
        """Generates a detailed report based on the analysis results."""
        return f"""
## Dockerfile Analysis Report

### Scores
- Security Score: {result.security_score}/100
- Optimization Score: {result.optimization_score}/100

### Optimization Metrics
- Layer Count: {result.optimization_metrics.layer_count}
- Estimated Size: {result.optimization_metrics.estimated_size}
- Cache Efficiency: {result.optimization_metrics.cache_efficiency}/100
- Build Time Score: {result.optimization_metrics.build_time_score}/100
- Maintainability Score: {result.optimization_metrics.maintainability_score}/100

### Detailed Report
{result.detailed_report}

### Optimized Dockerfile
```dockerfile
{result.optimized_dockerfile}
```
"""
