from dishka import Provider, Scope, provide

from core.domain.services import CreateLineItem


class ServicesProvider(Provider):
    scope = Scope.APP

    create_line_item = provide(CreateLineItem)
