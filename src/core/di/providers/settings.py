from dishka import Provider, Scope, provide

from core.settings import AgentSettings, BaseSettings


class SettingsProvider(Provider):
    scope = Scope.APP

    @provide
    @staticmethod
    def get_agent_settings() -> AgentSettings:
        return AgentSettings()

    @provide
    @staticmethod
    def get_base_settings() -> BaseSettings:
        return BaseSettings()
