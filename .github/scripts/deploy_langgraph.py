#!/usr/bin/env python3
"""
LangGraph Platform Cloud Deployment Script
Uses LangSmith Control Plane API to deploy the application
"""

import os
import sys
import json
import requests
from typing import Dict, Any, Optional

# Configuration
CONTROL_PLANE_BASE_URL = "https://gtm.smith.langchain.dev/api-host/v2"
DEPLOYMENT_NAME = "forjador-v5-pipeline"
GRAPH_NAME = "forjador_v5_pipeline"


class DeploymentError(Exception):
    """Custom exception for deployment failures"""
    pass


def get_api_headers(api_key: str) -> Dict[str, str]:
    """Construct API request headers with authentication"""
    return {
        "X-Api-Key": api_key,
        "Content-Type": "application/json"
    }


def create_deployment(api_key: str, google_api_key: str) -> Dict[str, Any]:
    """
    Create or update deployment via LangSmith Control Plane API

    Args:
        api_key: LangSmith API key for authentication
        google_api_key: Google API key for Gemini

    Returns:
        Deployment response data

    Raises:
        DeploymentError: If deployment fails
    """
    headers = get_api_headers(api_key)

    # Deployment configuration
    payload = {
        "name": DEPLOYMENT_NAME,
        "source_type": "github",  # Using GitHub repository as source
        "source_config": {
            "repo_url": "https://github.com/chicoronny/forjador-langchain-cloud",
            "branch": "main",
            "cpu": 1,
            "memory": 2048,  # 2GB memory for document processing
            "min_instances": 1,
            "max_instances": 5,
            "scaling": {
                "min_instances": 1,
                "max_instances": 5
            }
        },
        "graph_id": GRAPH_NAME,
        "env_vars": {
            # LangSmith configuration
            "LANGCHAIN_TRACING_V2": "true",
            "LANGCHAIN_ENDPOINT": "https://api.smith.langchain.com",
            "LANGCHAIN_PROJECT": "forjador-v5-spec01",

            # Language settings
            "PRIMARY_LANGUAGE": "pt-BR",

            # Pipeline settings
            "QUALITY_GATE_THRESHOLD": "0.85",
            "CHUNK_SIZE": "3500",
            "CHUNK_OVERLAP": "250",

            # File queue directories
            "INPUT_DIR": "./queue/input",
            "OUTPUT_DIR": "./queue/output"
        },
        "secrets": {
            "LANGCHAIN_API_KEY": api_key,
            "GOOGLE_API_KEY": google_api_key
        }
    }

    # Make API request
    url = f"{CONTROL_PLANE_BASE_URL}/deployments"

    print(f"Creating deployment '{DEPLOYMENT_NAME}'...")
    print(f"API endpoint: {url}")

    try:
        response = requests.post(
            url,
            headers=headers,
            json=payload,
            timeout=120
        )

        response.raise_for_status()

        deployment_data = response.json()
        print(f"✓ Deployment created successfully!")
        print(f"Deployment ID: {deployment_data.get('id', 'N/A')}")

        return deployment_data

    except requests.exceptions.HTTPError as e:
        error_detail = ""
        try:
            error_detail = e.response.json()
        except:
            error_detail = e.response.text

        raise DeploymentError(
            f"HTTP {e.response.status_code} error creating deployment: {error_detail}"
        )
    except requests.exceptions.RequestException as e:
        raise DeploymentError(f"Network error creating deployment: {str(e)}")


def wait_for_deployment(api_key: str, deployment_id: str, timeout: int = 600) -> None:
    """
    Wait for deployment to complete

    Args:
        api_key: LangSmith API key
        deployment_id: ID of deployment to monitor
        timeout: Maximum wait time in seconds

    Raises:
        DeploymentError: If deployment fails or times out
    """
    import time

    headers = get_api_headers(api_key)
    url = f"{CONTROL_PLANE_BASE_URL}/deployments/{deployment_id}"

    print(f"Waiting for deployment to complete (timeout: {timeout}s)...")

    start_time = time.time()
    while True:
        elapsed = time.time() - start_time
        if elapsed > timeout:
            raise DeploymentError(f"Deployment timed out after {timeout}s")

        try:
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()

            deployment = response.json()
            status = deployment.get("status", "unknown")

            print(f"Status: {status} (elapsed: {int(elapsed)}s)")

            if status == "ready":
                print("✓ Deployment is ready!")
                deployment_url = deployment.get("url")
                if deployment_url:
                    print(f"Deployment URL: {deployment_url}")
                return
            elif status in ["failed", "error"]:
                error_msg = deployment.get("error_message", "Unknown error")
                raise DeploymentError(f"Deployment failed: {error_msg}")

            # Wait before checking again
            time.sleep(10)

        except requests.exceptions.RequestException as e:
            print(f"Warning: Error checking deployment status: {e}")
            time.sleep(10)


def main():
    """Main deployment function"""
    # Get required environment variables
    api_key = os.getenv("LANGCHAIN_API_KEY")
    google_api_key = os.getenv("GOOGLE_API_KEY")

    if not api_key:
        print("Error: LANGCHAIN_API_KEY environment variable not set")
        sys.exit(1)

    if not google_api_key:
        print("Error: GOOGLE_API_KEY environment variable not set")
        sys.exit(1)

    try:
        # Create deployment
        deployment = create_deployment(api_key, google_api_key)
        deployment_id = deployment.get("id")

        if not deployment_id:
            raise DeploymentError("No deployment ID returned from API")

        # Wait for deployment to complete
        wait_for_deployment(api_key, deployment_id)

        print("\n" + "="*60)
        print("Successfully deployed to LangGraph Platform Cloud")
        print(f"Graph: {GRAPH_NAME}")
        print(f"Entry point: src.agent:graph")
        print("="*60)

        sys.exit(0)

    except DeploymentError as e:
        print(f"\n✗ Deployment failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
