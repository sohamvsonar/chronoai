# ChronoLog & AI: A Scalable, Collaborative Solution for LLM Conversation Logging

## Overview

This repository contains Python inference files and benchmarking code that demonstrate an integrated solution combining ChronoLog—a scalable, high-performance distributed log store—with AI inference interfaces. The goal is to create a fully traceable, end-to-end system for logging and retrieving conversations with large language models (LLMs), ensuring reproducibility, accountability, and efficient management of the exponentially growing chat interactions.

## Features

- **Real-Time Logging:** Captures both prompts and responses in real time.
- **Dual LLM Integration:**  
  - **Local LLM:** Uses LLAMA 3.2 via Ollama for internal inference.  
  - **External LLM:** Utilizes ChatGPT 3.5 Turbo via OpenAI API for external inference.
- **Scalable Architecture:** Employs ChronoLog’s distributed logging with physical time stamps for accurate event ordering.
- **Benchmarking:** Provides scripts to compare performance with and without ChronoLog logging.
- **Open-Source:** Explore and contribute to the project; see details below.

## Prerequisites

- **Python 3.7+**
- **ChronoLog Server:** Ensure the ChronoLog server is running and accessible.
- **Ollama Server:** For local inference with LLAMA 3.2.
- **OpenAI API Key:** For accessing ChatGPT 3.5 Turbo.
- Python packages listed in `requirements.txt`.

## Installation

1. **Clone the repository:**

   ```bash
   git clone https://github.com/sohamvsonar/chronoai.git
   cd chronoai

2. To be updated.

## Future Work

- Multi-node Deployment:
Expand ChronoLog to a multi-node setup for improved scalability and fault tolerance.

- Real-Time Monitoring Dashboard:
Develop a web-based interface for live visualization and analysis of conversation logs.

- Semantic Log Retrieval:
Implement advanced search capabilities (e.g., using embeddings or vector search) to retrieve relevant conversations.

- Enhanced Logging Controls:
Introduce role-based and selective logging to manage privacy and optimize performance.

- Integration with RAG Pipelines:
Extend logging to support retrieval-augmented generation systems, capturing both retrieved content and generated responses.

## Contributing

- Contributions are welcome! Please fork this repository and open a pull request with your changes. For major modifications, feel free to open an issue first to discuss your ideas.
