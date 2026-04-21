from asyncua import Server, ua
import logging
from model_loader import load_model
from services import MachineService
from simulation import MachineSimulation
from methods import bind_methods
from asyncua.server.history_sql import HistorySQLite

async def run_server() -> None:
    _logger = logging.getLogger(__name__)
    server = Server()
    await server.init()
    server.set_endpoint("opc.tcp://127.0.0.1:4849/coffee/")
    server.set_server_name("CoffeeMachine OPC UA Server")
    # set all possible endpoint policies
    server.set_security_policy(
        [
            ua.SecurityPolicyType.NoSecurity,
            ua.SecurityPolicyType.Basic256Sha256_SignAndEncrypt,
            ua.SecurityPolicyType.Basic256Sha256_Sign,
        ]
    )

    # Import the nodeset2.xml file
    await load_model(server)

    # Get the namespace index of the namespace from nodeset2.xml file
    idx = await server.get_namespace_index("urn:openai:generated:CoffeeMachineA")

    # Service object will includes all the machine logic of the coffee machine
    service = MachineService(server, idx)
    simulation = MachineSimulation(service)

    await service.initialize()
    await enable_history(server, service)

    # Link the method nodes from the nodeset2.xml to 
    # the corresponding service methods
    await bind_methods(server, service)

    async with server:
        _logger.info("Starting server!")
        await simulation.run()

async def enable_history(server, service):
    hm = server.iserver.history_manager

    hm.set_storage(HistorySQLite("my_datavalue_history.sql"))
    await hm.init()

    await server.historize_node_data_change(service.nodes["water_tank_level"], period=None, count=100)
    await server.historize_node_data_change(service.nodes["milk_tank_level"], period=None, count=100)
    await server.historize_node_data_change(service.nodes["coffee_bean_level"], period=None, count=100)