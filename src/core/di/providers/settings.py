from dishka import Provider, Scope, provide

from core.settings import AgentSettings, OpenRouterSettings


class SettingsProvider(Provider):
    scope = Scope.APP

    @provide
    @staticmethod
    def get_agent_settings() -> AgentSettings:
        return AgentSettings()

    @provide
    @staticmethod
    def get_open_router_settings() -> OpenRouterSettings:
        return OpenRouterSettings()
