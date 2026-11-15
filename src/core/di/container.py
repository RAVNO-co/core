from dishka import make_async_container

from .providers import AgentProvider, ServicesProvider, SettingsProvider

container = make_async_container(
    AgentProvider(), ServicesProvider(), SettingsProvider()
)
