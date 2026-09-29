# ACP and Logged LLM Gateways

Verified: 2026-09-29

## Decision

ACP is not a universal LLM gateway. It standardizes communication between code editors and coding agents. Centralized model routing and logging require a separate OpenAI-compatible LLM gateway.

Recommended architecture:

1. ACP adapters connect compatible editors to coding agents.
2. Agentgateway governs MCP, A2A, and agent-to-LLM traffic.
3. LiteLLM provides the central OpenAI-compatible inference endpoint.
4. OpenTelemetry and gateway dashboards collect logs, traces, costs, latency, retries, fallbacks, and cache metrics.

For the smallest practical deployment, start with LiteLLM alone. Add Agentgateway when MCP/A2A policy and agent traffic also need central governance.

## Important distinction

| Layer | Purpose | Examples |
|---|---|---|
| ACP | Editor-to-coding-agent interoperability | ACP, Codex ACP, Claude Agent ACP |
| LLM gateway | Model routing, authentication, logs, costs, cache telemetry | LiteLLM, Portkey, Bifrost |
| Agent/tool gateway | MCP, A2A, policy, identity, telemetry | Agentgateway |
| Observability | Traces, sessions, latency, costs, debugging | Helicone, OpenTelemetry |

## Compared projects

| Project | Role | Logging and telemetry | Self-hosted | License |
|---|---|---|---|---|
| [Agent Client Protocol](https://github.com/agentclientprotocol/agent-client-protocol) | Official editor-to-agent protocol | Not its main purpose | N/A | Apache-2.0 |
| [Agentgateway](https://github.com/agentgateway/agentgateway) | MCP, A2A, and LLM traffic gateway | OpenTelemetry metrics, logs, and traces | Yes | Apache-2.0 |
| [LiteLLM](https://github.com/BerriAI/litellm) | OpenAI-compatible gateway for 100+ providers | Spend, requests, failures, dashboard, prompt-cache metrics | Yes | Verify applicable components |
| [Portkey Gateway](https://github.com/Portkey-AI/gateway) | Multi-provider LLM and MCP gateway | Local log console, analytics, cache-hit indicators | Yes | MIT |
| [Helicone](https://github.com/Helicone/helicone) | LLM gateway and observability | Traces, sessions, costs, latency | Yes | Apache-2.0 |
| [Bifrost](https://github.com/maximhq/bifrost) | OpenAI-compatible multi-provider gateway | Monitoring, analytics, tracing, semantic cache | Yes | Apache-2.0 |

## Cache visibility

The dashboard should preserve separate states:

- Cache read or hit: provider reports cached input tokens.
- Cache write or creation: provider reports newly cached input tokens.
- Cache miss: no cached input tokens were reported for an eligible request.
- Telemetry unavailable: the provider or client did not expose cache metadata.

A request can contain both a cache read and a cache write. LiteLLM has the clearest request-level implementation found in this review: its prompt-caching management code distinguishes `all`, `injected`, and `hits`.

## Verified evidence

- [ACP README](https://github.com/agentclientprotocol/agent-client-protocol/blob/main/README.md)
- [ACP registry](https://github.com/agentclientprotocol/registry/blob/main/README.md)
- [ACP agent adapters](https://github.com/agentclientprotocol/agent-client-protocol/blob/main/docs/get-started/agents.mdx)
- [Agentgateway README](https://github.com/agentgateway/agentgateway/blob/main/README.md)
- [LiteLLM README](https://github.com/BerriAI/litellm/blob/main/README.md)
- [LiteLLM prompt-cache endpoint](https://github.com/BerriAI/litellm/blob/main/litellm/proxy/management_endpoints/prompt_caching_requests.py)
- [LiteLLM cache dashboard](https://github.com/BerriAI/litellm/blob/main/ui/litellm-dashboard/src/app/%28dashboard%29/caching/_components/cache_dashboard.tsx)
- [Portkey README](https://github.com/Portkey-AI/gateway/blob/main/README.md)
- [Portkey cache guide](https://github.com/Portkey-AI/gateway/blob/main/cookbook/getting-started/enable-cache.md)
- [Helicone README](https://github.com/Helicone/helicone/blob/main/README.md)
- [Bifrost README](https://github.com/maximhq/bifrost/blob/main/README.md)

## Limitations

- A gateway centralizes inference only when a client allows its API base URL, proxy, or provider configuration to be changed.
- Closed SaaS agents may call models from their own backend and bypass the local gateway.
- OAuth-based agents may require agent-specific adapters.
- A client can use ACP while its underlying agent still calls a model directly.
- Prompt logging requires redaction, retention controls, access controls, and a metadata-only option.

## Tags

`ACP`, `LLM gateway`, `OpenAI-compatible`, `Agentgateway`, `LiteLLM`, `MCP`, `A2A`, `OpenTelemetry`, `logging`, `tracing`, `cost tracking`, `prompt caching`, `self-hosting`
