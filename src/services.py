
from datetime import datetime, timezone

class MachineService:
    def __init__(self, server, namespace_index: int) -> None:
        self.server = server
        self.namespace_index = namespace_index
        self.nodes = {}
        # Default recipe and its requirement
        self.recipes = {
            "Latte-Large": {
                "water_amount": 100.0,
                "milk_amount": 50.0,
                "grounds_amount": 18.0,
            },
            "Cappuccino": {
                "water_amount": 30.0,
                "milk_amount": 120.0,
                "grounds_amount": 12.0,
            }
    }

    async def initialize(self) -> None:
        ns = self.namespace_index

        node_ids = {
            "current_state": f"ns={ns};s=CoffeeMachineA.Parameters.CurrentState",
            "coffee_bean_level": f"ns={ns};s=CoffeeMachineA.Parameters.CoffeeBeanLevel",
            "water_tank_level": f"ns={ns};s=CoffeeMachineA.Parameters.WaterTankLevel",
            "milk_tank_level": f"ns={ns};s=CoffeeMachineA.Parameters.MilkTankLevel",
            "served_coffee_count": f"ns={ns};s=CoffeeMachineA.Parameters.ServedCoffeeCount",
            "heater_status": f"ns={ns};s=CoffeeMachineA.Parameters.HeaterStatus",
            "pump_status": f"ns={ns};s=CoffeeMachineA.Parameters.PumpStatus",
            "valve_status": f"ns={ns};s=CoffeeMachineA.Parameters.ValveStatus",
            "grinder_status": f"ns={ns};s=CoffeeMachineA.Parameters.GrinderStatus",
            "system_time": f"ns={ns};s=CoffeeMachineA.BatchInformation.SystemTime",
            "batch_id": f"ns={ns};s=CoffeeMachineA.BatchInformation.BatchId",
            "order_id": f"ns={ns};s=CoffeeMachineA.BatchInformation.OrderId",
            "message": f"ns={ns};s=CoffeeMachineA.DeviceHealthAlarms.OffSpecAlarm.Message",
            "severity": f"ns={ns};s=CoffeeMachineA.DeviceHealthAlarms.OffSpecAlarm.Severity",
            "active_state": f"ns={ns};s=CoffeeMachineA.DeviceHealthAlarms.OffSpecAlarm.ActiveState",
            "acked_state": f"ns={ns};s=CoffeeMachineA.DeviceHealthAlarms.OffSpecAlarm.AckedState",
            "confirmed_state": f"ns={ns};s=CoffeeMachineA.DeviceHealthAlarms.OffSpecAlarm.ConfirmedState",
            "enabled_state": f"ns={ns};s=CoffeeMachineA.DeviceHealthAlarms.OffSpecAlarm.EnabledState",
            "comment": f"ns={ns};s=CoffeeMachineA.DeviceHealthAlarms.OffSpecAlarm.Comment",
            "event_id": f"ns={ns};s=CoffeeMachineA.DeviceHealthAlarms.OffSpecAlarm.EventId",
            "time": f"ns={ns};s=CoffeeMachineA.DeviceHealthAlarms.OffSpecAlarm.Time",
            "receive_time": f"ns={ns};s=CoffeeMachineA.DeviceHealthAlarms.OffSpecAlarm.ReceiveTime",
            "milk_alarm_state": f"ns={ns};s=CoffeeMachineA.ErrorConditions.MilkTankLevelAlarm.LimitState.CurrentState",
            "milk_low_limit": f"ns={ns};s=CoffeeMachineA.ErrorConditions.MilkTankLevelAlarm.LowLimit",
            "milk_low_low_limit": f"ns={ns};s=CoffeeMachineA.ErrorConditions.MilkTankLevelAlarm.LowLowLimit",
        }

        # Adding the nodes from nodeset2.xml to the 
        # service with a specific key string to represent each
        for key, node_id in node_ids.items():
            try:
                node = self.server.get_node(node_id)
                self.nodes[key] = node
            except Exception as e:
                print(f"FAILED: {key} -> {node_id} -> {e}")
 
        # This will be the initial state of the machine
        await self.write("current_state", "Idle")
        await self.write("heater_status", "ON")
        await self.write("pump_status", "OFF")
        await self.write("valve_status", "CLOSED")
        await self.write("grinder_status", "OFF")
        await self.write("system_time", self.now_iso())

    def now_iso(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    async def read(self, key: str):
        return await self.nodes[key].read_value()

    async def write(self, key: str, value):
        await self.nodes[key].write_value(value)

    # Start the machine
    async def start(self) -> None:
        await self.write("current_state", "Running")
        await self.write("served_coffee_count", 0)

    # Stop the machine
    async def stop(self) -> None:
        await self.write("current_state", "Stopped")
        await self.write("heater_status", "OFF")
        await self.write("pump_status", "OFF")
        await self.write("valve_status", "CLOSED")
        await self.write("grinder_status", "OFF")
    
    # Fill the water tank
    async def fill_water_tank(self, level: float) -> None:
        current_water = await self.read("water_tank_level")
        await self.write("water_tank_level", float(current_water) + level.Value)

    # Fill the milk tank
    async def fill_milk_tank(self, level: float) -> None:
        current_milk = await self.read("milk_tank_level")
        await self.write("milk_tank_level", float(current_milk) + level.Value)

    # Fill the coffee beans
    async def fill_coffee_bean(self, level: float) -> None:
        current_beans = await self.read("coffee_bean_level")
        await self.write("coffee_bean_level", float(current_beans) + level.Value)

    # Make coffee based on the user recipe
    async def make_coffee(self, recipe_name: str):
        recipe = self.recipes.get(recipe_name)
        if recipe is None:
            return "False", f"Recipe '{recipe_name}' not found"

        current_state = await self.read("current_state")
        if current_state not in {"Idle", "Running", "Brewing"}:
            return "False", f"Machine is not running, please start it: {current_state}"

        water = float(await self.read("water_tank_level") or 0)
        milk = float(await self.read("milk_tank_level") or 0)
        beans = float(await self.read("coffee_bean_level") or 0)

        if water < recipe["water_amount"]:
            return "False", "Not enough water"
        if milk < recipe["milk_amount"]:
            return "False", "Not enough milk"
        if beans < recipe["grounds_amount"] / 3:
            return "False", "Not enough coffee beans"

        # Start process
        await self.write("current_state", "Brewing")
        await self.write("pump_status", "ON")
        await self.write("grinder_status", "ON")
        await self.write("valve_status", "OPEN")

        # Deduct resources
        await self.write("water_tank_level", water - recipe["water_amount"])
        await self.write("milk_tank_level", milk - recipe["milk_amount"])
        await self.write("coffee_bean_level", beans - recipe["grounds_amount"] / 3)

        # total coffee served after the start
        served = int(await self.read("served_coffee_count") or 0)
        await self.write("served_coffee_count", served + 1)
    
        # Stop process
        await self.write("pump_status", "OFF")
        await self.write("grinder_status", "OFF")
        await self.write("valve_status", "CLOSED")
        await self.write("current_state", "Idle")

        return "True", ""