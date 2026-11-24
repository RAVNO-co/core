from dishka import AsyncContainer

from core.application.common.agent import AgentI


async def test_di(container: AsyncContainer) -> None:
    """Temporary test to run DI code
    In future this should be changed to presentation layer testing
    with inner dishka usage
    """
    await container.get(AgentI)
