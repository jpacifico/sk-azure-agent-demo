import os, json, yaml, jsonref
from pathlib import Path
from dotenv import load_dotenv
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from azure.ai.projects.models import OpenApiTool, OpenApiAnonymousAuthDetails

load_dotenv()
root = Path(__file__).resolve().parent

project_client = AIProjectClient.from_connection_string(
    credential=DefaultAzureCredential(),
    conn_str=os.environ["PROJECT_CONNECTION_STRING"],
)

spec_path = root / "tools" / "send_email.yaml"   # veille à avoir ce fichier
with open(spec_path, "r", encoding="utf-8") as f:
    spec_dict = yaml.safe_load(f)
openapi_spec = jsonref.loads(json.dumps(spec_dict))      # résout les $ref éventuels

# Create Auth object for the OpenApiTool (note that connection or managed identity auth setup requires additional setup in Azure)
auth = OpenApiAnonymousAuthDetails()

# Initialize agent OpenAPI tool using the read in OpenAPI spec
openapi = OpenApiTool(name="Outlook", spec=openapi_spec, description="sends and receives emails", auth=auth)

# Update the agent with the latest OpenAPI tool
agent = project_client.agents.create_agent(
    model="gpt-4o-mini",
    name="Sender agent",
    instructions="Call the SendEmail function. The body must be the report. Address it to Mads Bolaris and use HTML instead of markdown.",
    tools=openapi.definitions
)