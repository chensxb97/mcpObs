## MCP Observability
A project that explores the [Model Context Protocol](https://modelcontextprotocol.io/introduction) architecture for integrating different sources of observability data (alerts, incidents, events, logs and metrics) to power LLMs for observability.

### Objective
The goal for this repo is to implement an end to end LLM workflow that is able to rationalise data from different observability datasources to achieve the following functions:

- Summarize alerts and incidents.
- Perform RCA by correlating incidents, alerts, metrics, and logs.
- Recommend actionable solutions post-investigation.

### Components of this repo
- `server.py` — MCP Server (mock interface to observability data)
- `main.py` — Custom MCP Client + AI Agent + Terminal UI
- `/datasources/` — Mock Observability Data (logs, alerts, incidents, metrics, events)

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

3. Connect the MCP server to a MCP Host (Github Copilot, Claude, Cursor, etc.) or run a custom MCP client + LLM programmatically.

### Github Copilot Integration

1. Open the **Ask Copilot** chat using `Command + Shift + I` and select `Agent` mode.

![Agent Mode](/screenshots/agent_mode.png)

2. Click on the **Tools** icon. Type and select `Add More Tools`. Select `Add MCP Server` afterwards.

![Select Tools](/screenshots/select_tools.png)

![Add More Tools](/screenshots/add_more_tools.png)

![Add MCP Server](/screenshots/add_mcp_server.png)

3. Select `Command (stdio)`, which is the mode of transport defined in `server.py`.

![Command (stdio)](/screenshots/command_stdio.png)

4. Provide the **run command** for your mcp server. In this case, I define the **path of the python executable** in the virtual environment and the mcp server file - `server.py`.

```py
/<path to server file>/venv/bin/<python executable> server.py
```

5. On submitting the run command, a mcp server definition* will be generated in Github Copilot's `settings.json`. You should see something similar to this.

```json
"mcp": {
    "servers": {
        "my-mcp-server-XXXXX": {
            "type": "stdio",
            "command": "<path to server file>/venv/bin/<python executable>",
            "args": [
                "<path to server file>/server.py"
            ]
        }
    }
}
```

**For newer versions of [VSCode](https://code.visualstudio.com/docs/copilot/chat/mcp-servers#_add-an-mcp-server), mcp server definitions are managed in `.vscode/mcp.json` instead of `settings.json`.*

6. You can now start prompting Github Copilot to test the MCP server! On identifying some relevance with the tools, Copilot should prompt back asking for permission to run these tools. 

![Tool Permission](/screenshots/tool_permission.png)

7. After collecting all relevant data, it combines them with its own response to generate an enhanced output below. Congratulations, you have now successfully set up your own local MCP server for observability!

![Final Result](/screenshots/final_result.png)

### Custom MCP Client Integration
Alternatively, if you wish to build a custom MCP client + LLM that programmatically connects to the MCP server, an example implementation is provided in `main.py`.

#### What you need
- [Python3](https://www.python.org/downloads/)
- [Mistral AI](https://mistral.ai/)

You will need a Mistral API key — the free-tier is sufficient for this POC. No billing info is required unless used in production.

This project follows the instructions outlined in Mistral's [docs](https://docs.mistral.ai/agents/mcp/) for the MCP Client setup.

1. Setup .env with your MISTRAL_API_KEY. This file is currently ignored in `.gitignore`, do not ever commit this file.
```
touch .env
```
```
MISTRAL_API_KEY=<YOUR_API_KEY>
```

2. Run `main.py`. This will instantiate an LLM agent with an MCP client that establishes a connection with the local MCP server - `server.py`.

```
python3 main.py
```

You will be prompted to enter a command (e.g. “summarize recent alerts” or “what caused the latest incident?”). The agent will:
- With the knowledge of tools from the MCP server, decide which tool is most relevant from the input prompt.
- Call the tools to fetch relevant observability data.
- After receiving the data, a chat completions API is called to summarise the data as an observability expert.


### Screenshots
#### Request critical alerts for an application

![Critical Alerts](/screenshots/critical_alerts.png)

#### Asking for recent error logs for an application

![Error Logs](/screenshots/error_logs.png)

#### Request for an investigation

![Investigation](/screenshots/investigation.png)