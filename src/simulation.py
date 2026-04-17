import asyncio

class MachineSimulation:
    def __init__(self, service) -> None:
        self.service = service
        # self.alarm_manager = alarm_manager

    async def run(self) -> None:
        while True:
            await self.service.write("system_time", self.service.now_iso())
            # await self.alarm_manager.evaluate_milk_alarm()
            await asyncio.sleep(2.0)
