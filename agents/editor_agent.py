import os
import yaml
from dotenv import load_dotenv
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from azure.ai.projects.models import OpenApiTool, OpenApiAnonymousAuthDetails

load_dotenv()

project_client = AIProjectClient.from_connection_string(
    credential=DefaultAzureCredential(),
    conn_str=os.environ["PROJECT_CONNECTION_STRING"],
)

# Update the agent with the latest OpenAPI tool
agent = project_client.agents.create_agent(
    model="gpt-4o-mini",
    name="Editor agent",
    instructions="""You are the final reviewer of the report.
If the report is clear, informative, and provides relevant insights on the topic, then you should approve it.
Otherwise, do not approve it, and explain briefly what is missing, unclear, or insufficient."""
)