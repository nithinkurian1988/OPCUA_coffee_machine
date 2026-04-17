from pathlib import Path

async def load_model(server) -> None:
    model_path = (
        Path(__file__).resolve().parent.parent
        / "models"
        / "nodeset"
        / "CoffeeMachineA.NodeSet2.xml"
    )
    if not model_path.exists():
        raise FileNotFoundError(f"NodeSet file not found: {model_path}")
    await server.import_xml(str(model_path))
