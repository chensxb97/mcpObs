## MCP Observability
A project that explores the Model Context Provider (MCP) architecture for integrating different sources of observability data (alerts, incidents, events, logs and metrics) to power AI Agents for observability.

### Objective
The goal for this repo is to implement a simple POC that integrates a few observability datasources with a Mistral LLM to achieve the following functions:

- Summarize alerts and incidents.
- Perform RCA by correlating incidents, alerts, metrics, and logs.
- Recommend actionable solutions for each incident/alert.

### What you need
- [Python3](https://www.python.org/downloads/)
- [Mistral AI](https://mistral.ai/)

You will need a Mistral API key — the free-tier is sufficient for this POC. No billing info is required unless used in production.

This project follows the instructions outlined in Mistral's documentation for the MCP setup.

- [Model Context Protocol](https://modelcontextprotocol.io/introduction)
- [Mistral MCP docs](https://docs.mistral.ai/agents/mcp/)

### Components
- server.py — MCP Server (mock interface to observability data)

- main.py — MCP Client + AI Agent + Terminal UI

- /datasources/ — Mock Observability Data (alerts, incidents, metrics, logs)

### Usage
1. Clone Repo
```
git clone https://github.com/chensxb97/mcpObs.git
cd mcpObs
```

2. Setup python virtual environment.
```
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt
```

3. Setup .env with your MISTRAL_API_KEY. This file is currently ignored in the `.gitignore` file, do not ever commit this file.

```
touch .env
```

Add this line:
```
MISTRAL_API_KEY=<YOUR_API_KEY>
```

3. Run the main script. This will setup the LLM, MCP server and AI agent. 

You will be prompted to enter a command (e.g. “summarize recent alerts” or “what caused the latest incident?”). The agent will:
- Use the MCP server tools to retrieve relevant observability data
- Pass the data to a summarizer LLM
- Return a concise diagnosis or recommendation

```
python3 main.py
```