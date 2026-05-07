# Copyright (c) Meta Platforms, Inc. and affiliates
import os
import requests
from typing import List, Dict, Any
from dataclasses import dataclass
import yaml

@dataclass
class PerplexityResponse:
    """Structured response from Perplexity API"""
    content: str
    raw_response: Dict[str, Any]

class PerplexityAPI:
    """Wrapper for Perplexity API interactions"""
    
    def __init__(self, api_key: str | None = None, config_path: str = "config/agent_config.yaml"):
        """Initialize the API wrapper.
        
        Args:
            api_key: Perplexity API key. If None, will try to get from config.
            config_path: Path to the configuration file
        """
        self.config = self._load_config(config_path)
        self.api_key = api_key or self.config.get('api_key')
        if not self.api_key:
            raise ValueError("Perplexity API key not provided and not found in config")
            
        self.base_url = "https://api.perplexity.ai/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from yaml file."""
        try:
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
                return config.get('perplexity', {})
        except Exception as e:
            print(f"Warning: Could not load config file: {e}")
            return {}
    
    def query(self, 
             question: str,
             system_prompt: str = "Be precise and concise.",
             temperature: float | None = None,
             model: str | None = None,
             max_output_tokens: int | None = 4096) -> PerplexityResponse:
        """Send a single query to Perplexity API.
        
        Args:
            question: The question to ask
            system_prompt: System prompt to guide the response
            temperature: Temperature for response generation (0.0-1.0)
            model: Model to use for generation
            max_output_tokens: Maximum tokens in response
            
        Returns:
            PerplexityResponse containing the response content and raw API response
            
        Raises:
            requests.exceptions.RequestException: If API request fails
            ValueError: If API response is invalid
        """
        payload = {
            "model": model or self.config.get('model', 'sonar'),
            "messages": [
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": question
                }
            ],
            "temperature": temperature or self.config.get('temperature', 0.1),
            "max_tokens": max_output_tokens or self.config.get('max_output_tokens', 200),
            "top_p": 0.9,
            "return_images": False,
            "return_related_questions": False
        }
        
        response = requests.post(self.base_url, json=payload, headers=self.headers)
        response.raise_for_status()
        
        response_data = response.json()
        if "choices" not in response_data or not response_data["choices"]:
            raise ValueError("Invalid API response: missing choices")
            
        content = response_data["choices"][0].get("message", {}).get("content", "")
        if not content:
            raise ValueError("Invalid API response: missing content")
            
        return PerplexityResponse(content=content, raw_response=response_data)
    
    def batch_query(self, 
                   questions: List[str],
                   system_prompt: str = "Be precise and concise.",
                   temperature: float | None = None,
                   model: str | None = None,
                   max_output_tokens: int | None = None) -> List[PerplexityResponse]:
        """Send multiple queries to Perplexity API.
        
        Args:
            questions: List of questions to ask
            system_prompt: System prompt to guide the responses
            temperature: Temperature for response generation (0.0-1.0)
            model: Model to use for generation
            max_output_tokens: Maximum tokens in response
            
        Returns:
            List of PerplexityResponse objects
        """
        responses = []
        for question in questions:
            try:
                response = self.query(
                    question=question,
                    system_prompt=system_prompt,
                    temperature=temperature,
                    model=model,
                    max_output_tokens=max_output_tokens
                )
                responses.append(response)
            except Exception as e:
                # If a query fails, add None to maintain order with input questions
                print(f"Error querying Perplexity API: {str(e)}")
                responses.append(None)
        
        return responses 