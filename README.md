# Unified Agent Gateway

An open architecture for routing coding agents, model inference, MCP tools, and A2A traffic through observable, policy-controlled gateways.

## Objective

Provide one operational view of:

- model and provider usage;
- request logs and distributed traces;
- token usage, latency, cost, retries, and fallbacks;
- prompt-cache reads, writes, and misses;
- ACP editor-to-agent sessions;
- MCP and A2A traffic;
- identities, access policies, and exceptions.

## Architecture

```text
Editors and agent clients
        |
        | ACP / native agent protocols
        v
ACP agents and adapters
        |
        | MCP / A2A / OpenAI-compatible APIs
        v
Agentgateway (agent and tool policy)
        |
        v
LiteLLM (central model endpoint)
        |
        +--> OpenAI
        +--> Anthropic
        +--> Gemini / Vertex
        +--> Bedrock / Azure
        +--> Local models

Agentgateway + LiteLLM --> OpenTelemetry --> logs, traces, dashboards
```

ACP is not itself a universal LLM gateway. It standardizes communication between editors and coding agents. Model calls are centralized separately through an OpenAI-compatible gateway.

## Initial implementation plan

1. Run LiteLLM as the single model endpoint.
2. Capture request IDs, identities, providers, models, token usage, cost, latency, errors, retries, fallbacks, and cache telemetry.
3. Export traces and metrics through OpenTelemetry.
4. Add Agentgateway for MCP/A2A governance and policy.
5. Add ACP adapters for supported coding agents.
6. Document clients that cannot use a custom API base URL or proxy.
7. Build a unified cache dashboard with `hit`, `write`, `miss`, and `telemetry unavailable` states.

## Research

The verified GitHub research and project comparison are in [`docs/research/acp-llm-gateways.md`](docs/research/acp-llm-gateways.md).

## Status

Research and architecture definition. Implementation begins with a minimal, locally verifiable LiteLLM deployment.

## Orchestration requirements

The [orchestration blueprint](docs/orchestration/README.md) adds public requirements, isolated-node collaboration principles and a planning register. It is documentation, not a deployed runtime or proof of operational acceptance.
