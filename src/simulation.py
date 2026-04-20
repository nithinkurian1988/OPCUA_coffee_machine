import asyncio

class MachineSimulation:
    def __init__(self, service) -> None:
        self.service = service

    async def run(self) -> None:
        while True:
            await self.service.evaluate_pump_failure()
            await self.service.write("system_time", self.service.now_iso())
            await asyncio.sleep(2.0)
