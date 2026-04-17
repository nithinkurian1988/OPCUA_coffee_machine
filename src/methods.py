from asyncua import ua
import logging


async def bind_methods(server, service) -> None:
    _logger = logging.getLogger(__name__)
    ns = service.namespace_index

    start_node = server.get_node(f"ns={ns};s=CoffeeMachineA.Start")
    stop_node = server.get_node(f"ns={ns};s=CoffeeMachineA.Stop")
    fill_water_tank_node = server.get_node(f"ns={ns};s=CoffeeMachineA.FillWaterTank")
    fill_milk_tank_node = server.get_node(f"ns={ns};s=CoffeeMachineA.FillMilkTank")
    fill_coffee_bean_node = server.get_node(f"ns={ns};s=CoffeeMachineA.FillCoffeeBean")
    make_coffee_node = server.get_node(f"ns={ns};s=CoffeeMachineA.MakeCoffee")

    async def start_cb(parent):
        await service.start()
        return []

    async def stop_cb(parent):
        await service.stop()
        return []

    async def fill_water_tank_cb(parent, level: float):
        await service.fill_water_tank(level)
        return []

    async def fill_milk_tank_cb(parent, level: float):
        await service.fill_milk_tank(level)
        return []

    async def fill_coffee_bean_cb(parent, level: float):
        await service.fill_coffee_bean(level)
        return []

    async def make_coffee_cb(parent, recipe_name):
        success, error = await service.make_coffee(recipe_name.Value)
        return [
            ua.Variant(success, ua.VariantType.String),
            ua.Variant(error, ua.VariantType.String),
        ]

    # Optional debug check
    for name, node in {
        "Start": start_node,
        "Stop": stop_node,
        "FillWaterTank": fill_water_tank_node,
        "FillMilkTank": fill_milk_tank_node,
        "FillCoffeeBean": fill_coffee_bean_node,
        "MakeCoffee": make_coffee_node,
    }.items():
        bn = await node.read_browse_name()
        _logger.debug(f"{name} node found:", bn, node.nodeid)

    server.link_method(start_node, start_cb)
    server.link_method(stop_node, stop_cb)
    server.link_method(fill_water_tank_node, fill_water_tank_cb)
    server.link_method(fill_milk_tank_node, fill_milk_tank_cb)
    server.link_method(fill_coffee_bean_node, fill_coffee_bean_cb)
    server.link_method(make_coffee_node, make_coffee_cb)