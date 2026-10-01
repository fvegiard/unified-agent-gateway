"""Non-model installation/readiness test. Never calls Conversation.run()."""
import json
import os
import socket
import sys
from importlib.metadata import version
from pathlib import Path

# Self-contained offline settings, before ANY third-party import. LiteLLM otherwise
# retrieves its model-cost map on import. This supported setting selects the map
# bundled inside the already installed distribution, not a downloaded model.
# Source: litellm/litellm_core_utils/get_model_cost_map.py
# Docs: https://docs.litellm.ai/docs/proxy/custom_model_cost_map
runtime_offline_settings = {
    'LITELLM_LOCAL_MODEL_COST_MAP': 'True',
    'DO_NOT_TRACK': '1',
    'ANONYMIZED_TELEMETRY': 'false',
    'OPENHANDS_SUPPRESS_BANNER': '1',
}
os.environ.update(runtime_offline_settings)

# Audit DNS, connection, datagram/message transmission, and bind operations.
# Also prohibit Internet socket creation and child-process escape routes.
# This is a Python-level test guard, not an OS/network security boundary.
network_attempts = []
blocked_network_events = {
    'socket.getaddrinfo', 'socket.gethostbyname', 'socket.gethostbyaddr',
    'socket.getnameinfo', 'socket.connect', 'socket.sendto', 'socket.sendmsg',
    'socket.bind',
}
blocked_process_events = {'subprocess.Popen', 'os.system', 'os.exec', 'os.posix_spawn'}
def forbid_network(event, args):
    internet_socket = (
        event == 'socket.__new__'
        and len(args) > 1
        and args[1] in (socket.AF_INET, socket.AF_INET6)
    )
    if event in blocked_network_events or internet_socket:
        network_attempts.append({'event': event})
        raise RuntimeError('Network is disabled for this offline readiness check: ' + event)
    if event in blocked_process_events:
        raise RuntimeError('Child processes are disabled for this offline readiness check')
sys.addaudithook(forbid_network)

from pydantic import ValidationError

from openhands.sdk import Agent, Conversation, LLM, Tool
from openhands.sdk.security import AlwaysConfirm
from openhands.sdk.subagent import register_agent
from openhands.sdk.subagent.registry import get_agent_factory
from openhands.tools.task import TaskToolSet
from openhands.tools.task.definition import TaskAction

root = Path(__file__).resolve().parents[1]
workspace = root / 'checks' / 'empty-workspace'
workspace.mkdir(exist_ok=True)

# A model identifier is needed to validate configuration; this does not run it.
llm = LLM(model='openai/gpt-4o', api_key=None)
register_agent(
    name='offline_demo_worker',
    factory_func=lambda child_llm: Agent(llm=child_llm, tools=[]),
    description='A configured, tool-free child for offline schema verification only.',
)
agent = Agent(llm=llm, tools=[Tool(name=TaskToolSet.name)])
child = get_agent_factory('offline_demo_worker').factory_func(llm)
conv = Conversation(agent=agent, workspace=workspace, visualizer=None)
try:
    conv.set_confirmation_policy(AlwaysConfirm())
    task_tools = TaskToolSet.create(conv.state)
    action = TaskAction(prompt='Offline schema validation only', subagent_type='offline_demo_worker')
    child_configuration_valid = (
        isinstance(child, Agent)
        and child.tools == []
        and child.llm.model == llm.model
    )
    tool_names = [tool.name for tool in task_tools]
    schema = TaskAction.model_json_schema()
    task_schema_valid = (
        schema.get('required') == ['prompt']
        and schema['properties']['prompt'].get('type') == 'string'
        and action.prompt == 'Offline schema validation only'
        and action.subagent_type == 'offline_demo_worker'
    )
    assert child_configuration_valid, 'Child must be a tool-free Agent with the configured model'
    assert tool_names == ['task'], f'Unexpected task tool names: {tool_names!r}'
    assert task_tools[0].action_type is TaskAction, 'Task tool has the wrong action schema'
    assert task_schema_valid, 'TaskAction schema or validated values differ from expectations'

    # Negative control: missing the mandatory prompt must be rejected.
    missing_prompt_rejected = False
    try:
        TaskAction.model_validate({'subagent_type': 'offline_demo_worker'})
    except ValidationError as exc:
        missing_prompt_rejected = any(
            error['type'] == 'missing' and error['loc'] == ('prompt',)
            for error in exc.errors()
        )
    assert missing_prompt_rejected, 'TaskAction unexpectedly accepted a missing prompt'
    result = {
        'status': 'passed',
        'sdk_version': version('openhands-sdk'),
        'tools_version': version('openhands-tools'),
        'conversation_created': True,
        'registered_child_configuration_created': child_configuration_valid,
        'tool_names': tool_names,
        'task_schema_validation': task_schema_valid,
        'negative_missing_prompt_rejected': missing_prompt_rejected,
        'network_attempts': network_attempts,
        'network_guard_events': sorted(blocked_network_events | {'socket.__new__:AF_INET/AF_INET6'}),
        'runtime_offline_settings': runtime_offline_settings,
        'inference_calls': 0,
        'real_subagent_run': False,
        'mcp_server_installed': False,
    }
    for tool in task_tools:
        tool.executor.close()
finally:
    conv.close()
assert not network_attempts, network_attempts
(root / 'checks' / 'offline-receipt.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result, indent=2))
