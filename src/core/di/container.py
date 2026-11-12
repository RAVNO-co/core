from dishka import make_async_container

from .providers import AgentProvider

container = make_async_container(AgentProvider())
