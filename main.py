#!/usr/bin/env python
import asyncio
import os
import json
from pathlib import Path

from mistralai import Mistral
from mistralai.extra.run.context import RunContext
from mistralai.extra.mcp.stdio import MCPClientSTDIO
from mcp import StdioServerParameters
from dotenv import load_dotenv

from typing import List
from pydantic import BaseModel

load_dotenv()
cwd = Path(__file__).parent
MODEL = "mistral-small-latest"  # or your preferred model

class Alert(BaseModel):
    id: str
    application: str
    severity: str
    message: str
    timestamp: str
    action_required: bool
    acknowledged: bool

class Incident(BaseModel):
    incident_name: str
    application: str
    description: str
    alerts: List[Alert]
    summary: str
    resolved: bool

class MetricData(BaseModel):
    timestamp: str
    error_count: int
    warning_count: int
    latency_ms: int
    throughput_rps: int

class Metric(BaseModel):
    application: str
    data: List[MetricData]

class Event(BaseModel):
    name: str
    application: str
    timestamp: str

class ObservabilityOutput(BaseModel):
    error_logs: List[str]
    info_logs: List[str]
    warning_alerts: List[Alert]
    critical_alerts: List[Alert]
    resolved_incidents: List[Incident]
    unresolved_incidents: List[Incident]
    metrics: List[Metric]
    events: List[Event]

run_ctx = None

async def main() -> None:
    api_key = os.environ.get("MISTRAL_API_KEY")
    if not api_key:
        raise RuntimeError("Missing MISTRAL_API_KEY in environment")

    client = Mistral(api_key)

    cwd = Path(__file__).parent

    # MCP Server setup
    server_params = StdioServerParameters(
        command="python",
        args=[str((cwd / "server.py").resolve())],
        env=None,
    )
    mcp_client = MCPClientSTDIO(stdio_params=server_params)
    await print_with_spinner("Initialized MCP Client ...")

    # Agent setup
    observability_agent = client.beta.agents.create(
        model=MODEL,
        name="observability assistant",
        instructions="You are an observability assistant. Use the available tools to investigate logs and incidents.",
        description="",
    )

    await print_with_spinner("✅ Observability Agent ready.\n")

    while True:
        try:
            cmd = input("\n🔎 Command (type 'exit' to quit): ").strip()
            if cmd.lower() in ("exit", "quit"):
                print("👋 Exiting.")
                break
            await print_with_spinner("Processing query...")
            await process_input(client, observability_agent, mcp_client, query=cmd)
            
        except KeyboardInterrupt:
            print("\n👋 Exiting.")
            break
        except Exception as e:
            print(f"❗ Error: {e}")

async def spinner(msg="Loading..."):
    symbols = ['|', '/', '-', '\\']
    idx = 0
    while True:
        print(f"\r{msg} {symbols[idx % len(symbols)]}", end="", flush=True)
        idx += 1
        try:
            await asyncio.sleep(0.1)
        except asyncio.CancelledError:
            print("\r", end="", flush=True)  # clear line
            break

async def print_with_spinner(text: str):
    spinner_task = asyncio.create_task(spinner())
    # Simulate or await some async work that leads to the print
    # Here we just sleep shortly to simulate that processing
    await asyncio.sleep(1)  # Adjust or replace with real awaited event if needed
    spinner_task.cancel()
    try:
        await spinner_task
    except asyncio.CancelledError:
        pass
    print(text)

async def run_with_spinner(coro, msg="Loading..."):
    spinner_task = asyncio.create_task(spinner(msg))
    try:
        result = await coro
    finally:
        spinner_task.cancel()
        try:
            await spinner_task
        except asyncio.CancelledError:
            pass
    return result

async def process_input(client: Mistral, observability_agent, mcp_client, query: str):
    global run_ctx

    # We will use the previous run context if it exists
    if run_ctx is None:
        # Create a new run context
        await print_with_spinner("Creating new run context...")
        run_ctx = RunContext(
            agent_id=observability_agent.id,
            output_format=ObservabilityOutput,
            continue_on_fn_error=True,
        )
    else:
        await print_with_spinner("Using existing run context ...")
        
    # Register the MCP client with the run context
    await run_ctx.register_mcp_client(mcp_client=mcp_client)
    await print_with_spinner("MCP Client registered.")
    await print_with_spinner(f"Submitted query to LLM: {query} ...")
    run_result = await run_with_spinner(
        client.beta.conversations.run_async(run_ctx=run_ctx, inputs=query),
        msg=f"Processing query ...",
    )
    # Print the results
    # print("\n=== Run Result ===")
    # for entry in run_result.output_entries:
    #     # Only print assistant message outputs
    #     if entry.type == "message.output" and getattr(entry, "role", None) == "assistant":
    #         try:
    #             content_json = json.loads(entry.content)
    #             # Pretty-print JSON content
    #             pretty_content = json.dumps(content_json, indent=2)
    #             print("Assistant:")
    #             print(pretty_content)
    #             print()
    #         except (json.JSONDecodeError, TypeError):
    #             print("Assistant:")
    #             print(entry.content)
    summary = await summarize_observability(client, run_result.output_entries, MODEL)
    print("\n=== LLM Summary ===")
    print(summary)
                    
async def summarize_observability(client: Mistral, data_json, model: str = MODEL):
    # Format the prompt with the raw JSON data embedded
    prompt = f"""
    You are an observability expert assistant. You will be given observability data comes in the form of alerts, events, incidents, metrics and logs.
    These data might be correlated with each other, so please look for patterns and relationships.
    Please analyse and summarise the data concisely, and provide actionable solutions for each incident/alert.

    {data_json}
    """

    # Pass the prompt to the LLM for summarization
    await print_with_spinner(f"Passing data to LLM for summarization ...")
    response = client.chat.complete(
        model= model,
        messages = [
            {
                "role": "user",
                "content": prompt,
            },
        ]
    )

    # Extract assistant's reply
    summary = response.choices[0].message.content
    return summary

if __name__ == "__main__":
    asyncio.run(main())