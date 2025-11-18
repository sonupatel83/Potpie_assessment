"""
Service for comparing files using Ollama
"""
import json
import time
from typing import Dict, Any
from ..config import Config
from ..logger import logging
from ..services.ollama_service import OllamaService


class ComparisonService:
    def __init__(self):
        self.ollama_service = OllamaService()
    
    def generate_comparison_prompt(self, file_a_content: str, file_b_content: str, 
                                   file_a_name: str, file_b_name: str, 
                                   diff_text: str) -> str:
        """Generate the comparison prompt for Ollama"""
        
        # Truncate files if too large (keep first 5000 chars each)
        max_file_length = 5000
        file_a_preview = file_a_content[:max_file_length] + ("..." if len(file_a_content) > max_file_length else "")
        file_b_preview = file_b_content[:max_file_length] + ("..." if len(file_b_content) > max_file_length else "")
        diff_preview = diff_text[:3000] + ("..." if len(diff_text) > 3000 else "")
        
        prompt = f"""You are a precise, conservative code-comparison agent. Always explain assumptions, never invent code, and return structured JSON.

Task: Compare two specific source files and produce a focused, useful report that a software engineer can act on.

File A: {file_a_name}
File B: {file_b_name}

File A content (first {max_file_length} chars):
```
{file_a_preview}
```

File B content (first {max_file_length} chars):
```
{file_b_preview}
```

Unified diff (first 3000 chars):
```
{diff_preview}
```

Analyze these files and provide:

1. Semantic differences (what changed in behavior/logic, not just text)
2. Potential bugs or risky changes (missing error handling, wrong comparisons, unsafe defaults)
3. Concrete improvements or refactorings (code-style suggestions, performance tips, tests to add)
4. API contract differences (function signatures, return types, exceptions)
5. Estimated severity for each issue: "info", "minor", "major", "critical"

Return ONLY valid JSON with this exact structure:

{{
  "analysis": [
    {{
      "file_section": "<function or region name or line range>",
      "type": "style|bug|performance|api|security|best_practice",
      "severity": "info|minor|major|critical",
      "description": "<short human-readable>",
      "suggestion": "<concrete fix or code fragment (<=200 chars) or link to linter rule>",
      "lines": {{"start": <int|null>, "end": <int|null>}}
    }}
  ],
  "summary": {{
    "total_issues": <int>,
    "critical": <int>,
    "major": <int>,
    "minor": <int>,
    "info": <int>,
    "recommendation": "<one-paragraph top-level recommendation>"
  }}
}}

Constraints:
- NEVER invent code or claims; if uncertain, say "uncertain — needs human check"
- Keep each suggestion short, actionable, and reference exact line numbers where possible
- Include references to linters, test ideas, or commands (e.g., "run `pytest tests/test_client.py`" or "run `flake8`")
- Return ONLY the JSON object, no markdown, no code blocks, no explanations outside the JSON

Return the JSON now:"""
        
        return prompt
    
    def analyze_comparison(self, file_a_content: str, file_b_content: str,
                          file_a_name: str, file_b_name: str,
                          diff_text: str) -> Dict[str, Any]:
        """Analyze file comparison using Ollama"""
        
        prompt = self.generate_comparison_prompt(
            file_a_content, file_b_content,
            file_a_name, file_b_name,
            diff_text
        )
        
        try:
            # Get analysis from Ollama
            response_text = self.ollama_service.generate_text(prompt, max_tokens=4000)
            
            # Try to extract JSON from response
            # Remove markdown code blocks if present
            response_text = response_text.strip()
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.startswith("```"):
                response_text = response_text[3:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]
            response_text = response_text.strip()
            
            # Try to find JSON object
            start_idx = response_text.find("{")
            end_idx = response_text.rfind("}") + 1
            
            if start_idx >= 0 and end_idx > start_idx:
                json_text = response_text[start_idx:end_idx]
                analysis_data = json.loads(json_text)
                return analysis_data
            else:
                # Fallback: return error in expected format
                return {
                    "analysis": [],
                    "summary": {
                        "total_issues": 0,
                        "critical": 0,
                        "major": 0,
                        "minor": 0,
                        "info": 0,
                        "recommendation": "Could not parse LLM response. Raw response: " + response_text[:500]
                    }
                }
                
        except json.JSONDecodeError as e:
            logging.error(f"JSON decode error: {e}. Response: {response_text[:500]}")
            return {
                "analysis": [],
                "summary": {
                    "total_issues": 0,
                    "critical": 0,
                    "major": 0,
                    "minor": 0,
                    "info": 0,
                    "recommendation": f"JSON parsing error: {str(e)}. Please check the LLM response format."
                }
            }
        except Exception as e:
            logging.error(f"Error in comparison analysis: {e}")
            return {
                "analysis": [],
                "summary": {
                    "total_issues": 0,
                    "critical": 0,
                    "major": 0,
                    "minor": 0,
                    "info": 0,
                    "recommendation": f"Analysis error: {str(e)}"
                }
            }

