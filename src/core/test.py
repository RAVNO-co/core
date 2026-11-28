import asyncio

from core.application.common.agent import AgentI, HumanRequest
from core.di import container
from core.domain.models import Receipt
from core.domain.services import CreateRealUser, CreateReceipt

user = CreateRealUser()("Матвей")
receipt = CreateReceipt()(user, "Пивнуха реднек")
request = HumanRequest(
    user.id, "Привет, что ты умеешь?", (), (), receipt, [user]
)


async def run():
    agent = await container.get(AgentI)
    res = await agent.invoke(request)
    print(res)


asyncio.run(run())
