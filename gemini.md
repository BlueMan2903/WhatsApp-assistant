# Podiatrist Clinic AI Assistant

## Project Goal
The primary goal of this project is to develop a model-agnostic AI agent that can communicate with customers of a podiatrist clinic via WhatsApp. The agent's main function is to guide users based on their symptoms and recommend the most suitable treatment type to book.

## Key Features
- **Model Agnostic:** Designed to easily switch between different Large Language Models (LLMs) with minimal code changes, leveraging the Langchain framework.
- **Symptom-Based Guidance:** Provides recommendations for podiatry treatments based on user-described symptoms.
- **WhatsApp Integration (Future):** Planned integration with a WhatsApp API to enable direct communication with customers.

## Current Technologies
- **Python:** The core programming language for the agent.
- **Langchain:** Used as the framework for interacting with various LLMs, ensuring model agnosticism.
- **Google Gemini (via Langchain):** The current LLM integrated for natural language understanding and generation.

## Standards
- Utilize a Test Driven Development cycle
- Implement proper error handling
- Follow REST API conventions
- Utilize modern software design patters
- Utilize OOP concepts and designs where fitting
- Always remove redundant and/or unutilized code blocks

## Tools Preference
- Prefer web_fetch for documentation
- Enable auto-accept for safe operations

## Project Status
- **Date:** August 20, 2025
- **Status:** Actively being developed and refined.

## Setup and Running
1.  **Clone the repository:**
    ```bash
    git clone <repository_url>
    cd openai-test
    ```
2.  **Create and activate a virtual environment:**
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    ```
3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
4.  **Set up Google API Key:**
    The application requires a `GEMINI_API_KEY`. You will need to set it as an environment variable.
    ```bash
    export GEMINI_API_KEY="YOUR_API_KEY_HERE"
    ```

5.  **Run the agent:**
    ```bash
    python3 ai_assistant.py
    ```
    Type your symptoms in Hebrew, and the agent will respond. Type `quit` to exit.

## Future Enhancements
- **Actual WhatsApp API Integration:** Implement a robust connection to a WhatsApp Business API for real-time customer interaction.
- **Comprehensive Symptom-Treatment Mapping:** Expand the knowledge base (`context.py`) with more detailed symptom-to-treatment mappings and decision-making logic.
- **Database Integration:** Store conversation history and customer information for better personalization and follow-up.
- **Error Handling and Robustness:** Improve error handling for API calls and unexpected user inputs.
- **Deployment:** Containerize the application for easier deployment to cloud platforms.