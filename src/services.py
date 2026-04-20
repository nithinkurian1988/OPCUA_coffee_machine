
from datetime import datetime, timezone
import uuid

class MachineService:
    def __init__(self, server, namespace_index: int) -> None:
        self.server = server
        self.namespace_index = namespace_index
        self.nodes = {}
        # Default recipe and its requirement
        self.recipes = {
            "Latte": {
                "grounds_water": 100.0,
                "milk_amount": 50.0,
                "grounds_amount": 18.0,
            },
            "Cappuccino": {
                "grounds_water": 30.0,
                "milk_amount": 100.0,
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
            "latte_grounds_amount": f"ns={ns};s=CoffeeMachineA.Recipes.Latte.GroundsAmount",
            "latte_grounds_water": f"ns={ns};s=CoffeeMachineA.Recipes.Latte.GroundsWater",
            "latte_milk_amount": f"ns={ns};s=CoffeeMachineA.Recipes.Latte.MilkAmount",
            "capp_grounds_amount": f"ns={ns};s=CoffeeMachineA.Recipes.Cappuccino.GroundsAmount",
            "capp_grounds_water": f"ns={ns};s=CoffeeMachineA.Recipes.Cappuccino.GroundsWater",
            "capp_milk_amount": f"ns={ns};s=CoffeeMachineA.Recipes.Cappuccino.MilkAmount",
            "manufacturer": f"ns={ns};s=CoffeeMachineA.Identification.Manufacturer",
            "model": f"ns={ns};s=CoffeeMachineA.Identification.Model",
            "device_health": f"ns={ns};s=CoffeeMachineA.DeviceHealth",
            "milk_alarm_state": f"ns={ns};s=CoffeeMachineA.ErrorConditions.MilkTankLevelAlarm.LimitState.CurrentState",
            "milk_low_limit": f"ns={ns};s=CoffeeMachineA.ErrorConditions.MilkTankLevelAlarm.LowLimit",
            "milk_low_low_limit": f"ns={ns};s=CoffeeMachineA.ErrorConditions.MilkTankLevelAlarm.LowLowLimit",
            "pump_alarm_active_state": f"ns={ns};s=CoffeeMachineA.DeviceHealthAlarms.PumpFailureAlarm.ActiveState",
            "pump_alarm_enabled_state": f"ns={ns};s=CoffeeMachineA.DeviceHealthAlarms.PumpFailureAlarm.EnabledState",
            "pump_alarm_acked_state": f"ns={ns};s=CoffeeMachineA.DeviceHealthAlarms.PumpFailureAlarm.AckedState",
            "pump_alarm_confirmed_state": f"ns={ns};s=CoffeeMachineA.DeviceHealthAlarms.PumpFailureAlarm.ConfirmedState",
            "pump_alarm_severity": f"ns={ns};s=CoffeeMachineA.DeviceHealthAlarms.PumpFailureAlarm.Severity",
            "pump_alarm_message": f"ns={ns};s=CoffeeMachineA.DeviceHealthAlarms.PumpFailureAlarm.Message",
            "pump_alarm_event_id": f"ns={ns};s=CoffeeMachineA.DeviceHealthAlarms.PumpFailureAlarm.EventId",
            "pump_alarm_time": f"ns={ns};s=CoffeeMachineA.DeviceHealthAlarms.PumpFailureAlarm.Time",
            "pump_alarm_receive_time": f"ns={ns};s=CoffeeMachineA.DeviceHealthAlarms.PumpFailureAlarm.ReceiveTime",
            "pump_alarm_comment": f"ns={ns};s=CoffeeMachineA.DeviceHealthAlarms.PumpFailureAlarm.Comment",
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

        # Initialize the milk alarm states and the limits
        await self.write("device_health", "NORMAL")
        await self.write("milk_alarm_state", "Normal")
        await self.write("milk_low_limit", 200.0)
        await self.write("milk_low_low_limit", 50.0)

        # Initialize the pump failure alarm
        await self.write("pump_alarm_active_state", "False")
        await self.write("pump_alarm_enabled_state", "True")
        await self.write("pump_alarm_acked_state", "False")
        await self.write("pump_alarm_confirmed_state", "False")
        await self.write("pump_alarm_severity", "0")
        await self.write("pump_alarm_message", "")
        await self.write("pump_alarm_event_id", "")
        await self.write("pump_alarm_comment", "")

        # Identification variables
        await self.write("manufacturer", "Philips")
        await self.write("model", "CM-100")

        # Batch information variables
        await self.write("batch_id", "BATCH-001")
        await self.write("order_id", "ORDER-101")

        # Initialize the recipe nodes
        latte = self.recipes["Latte"]
        await self.write("latte_grounds_amount", latte["grounds_amount"])
        await self.write("latte_grounds_water", latte["grounds_water"])
        await self.write("latte_milk_amount", latte["milk_amount"])
        capp = self.recipes["Cappuccino"]
        await self.write("capp_grounds_amount", capp["grounds_amount"])
        await self.write("capp_grounds_water", capp["grounds_water"])
        await self.write("capp_milk_amount", capp["milk_amount"])

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

    # Update the alarm based on the milk level
    async def evaluate_milk_alarm(self):
        milk = float(await self.read("milk_tank_level") or 0)
        milk_low_limit = float(await self.read("milk_low_limit") or 0)
        milk_low_low_limit = float(await self.read("milk_low_low_limit") or 0)

        if milk < milk_low_low_limit:
            await self.write("milk_alarm_state", "Low-Low")
            await self.write("device_health", "ERROR")
        elif milk < milk_low_limit:
            await self.write("milk_alarm_state", "Low")
            await self.write("device_health", "WARNING")
        else:
            await self.write("milk_alarm_state", "Normal")
            await self.write("device_health", "NORMAL")

    # Activate the pump failure alarm
    async def activate_pump_failure_alarm(self):
        enabled = str(await self.read("pump_alarm_enabled_state") or "True")

        if enabled != "True":
            return
        event_id = str(uuid.uuid4())
        now = self.now_iso()
        await self.write("pump_alarm_active_state", "True")
        await self.write("pump_alarm_confirmed_state", "False")
        await self.write("pump_alarm_severity", "900")
        await self.write("pump_alarm_message", "Pump failure detected")
        await self.write("pump_alarm_event_id", event_id)
        await self.write("pump_alarm_time", now)
        await self.write("pump_alarm_receive_time", now)
        await self.write("device_health", "ERROR")

    async def clear_pump_failure_alarm(self):
        await self.write("pump_alarm_active_state", "False")
        await self.write("pump_alarm_acked_state", "False")
        await self.write("pump_alarm_severity", "0")
        await self.write("pump_alarm_message", "")
        await self.write("pump_alarm_event_id", "")

    async def evaluate_pump_failure(self) -> bool:
        enabled = str(await self.read("pump_alarm_enabled_state") or "True")

        if enabled != "True":
            await self.write("pump_alarm_active_state", "False")
            return
        pump_status = str(await self.read("pump_status") or "").upper()
        if pump_status == "ERROR":
            await self.activate_pump_failure_alarm()
            return True
        return False
    
    async def acknowledge_pump_failure(self, comment: str = ""):
        await self.write("pump_alarm_acked_state", "True")
        if comment:
            await self.write("pump_alarm_comment", comment)

    async def confirm_pump_failure(self, comment: str = ""):
        await self.write("pump_alarm_confirmed_state", "True")
        if comment:
            await self.write("pump_alarm_comment", comment)
        await self.write("pump_status", "OFF")
        await self.clear_pump_failure_alarm()
        await self.write("device_health", "NORMAL")
    
    async def enable_pump_failure_alarm(self):
        await self.write("pump_alarm_enabled_state", "True")

    async def disable_pump_failure_alarm(self):
        await self.write("pump_alarm_enabled_state", "False")
        await self.write("pump_alarm_active_state", "False")
        await self.write("pump_alarm_message", "")
        await self.write("pump_alarm_severity", "0")
        await self.write("pump_alarm_event_id", "")

    # Fill the milk tank
    async def fill_milk_tank(self, level: float) -> None:
        current_milk = await self.read("milk_tank_level")
        await self.write("milk_tank_level", float(current_milk) + level.Value)
        # Update the milk alarm state
        await self.evaluate_milk_alarm()

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

        pump_status = await self.evaluate_pump_failure()
        if pump_status:
            return "False", "Pump failure detected"

        water = float(await self.read("water_tank_level") or 0)
        milk = float(await self.read("milk_tank_level") or 0)
        beans = float(await self.read("coffee_bean_level") or 0)

        if water < recipe["grounds_water"]:
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
        await self.write("water_tank_level", water - recipe["grounds_water"])
        await self.write("milk_tank_level", milk - recipe["milk_amount"])
        await self.write("coffee_bean_level", beans - recipe["grounds_amount"] / 3)

        # Update the milk alarm state
        await self.evaluate_milk_alarm()

        # total coffee served after the start
        served = int(await self.read("served_coffee_count") or 0)
        await self.write("served_coffee_count", served + 1)
    
        # Stop process
        await self.write("pump_status", "OFF")
        await self.write("grinder_status", "OFF")
        await self.write("valve_status", "CLOSED")
        await self.write("current_state", "Idle")

        return "True", ""