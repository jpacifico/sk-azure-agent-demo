"""
researcher_agent.py  –  Crée un agent Azure AI (Researcher) avec l’outil DuckDuckGo
Dépendances :
  pip install --upgrade --pre azure-ai-projects azure-identity python-dotenv pyyaml jsonref
"""

import os, json, yaml, jsonref
from pathlib import Path
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import OpenApiTool, OpenApiAnonymousAuthDetails

# -------------------------------------------------------------------- #
# 1) Chargement des variables .env
root = Path(__file__).resolve().parent
load_dotenv()

CONN_STR = os.getenv("PROJECT_CONNECTION_STRING")          # host;sub;rg;workspace
MODEL    = os.getenv("MODEL_DEPLOYMENT_NAME", "gpt-4o-mini")
if not CONN_STR:
    raise RuntimeError("PROJECT_CONNECTION_STRING manquant dans .env")

# -------------------------------------------------------------------- #
# 2) Client du projet Azure AI
client = AIProjectClient.from_connection_string(
    credential=DefaultAzureCredential(),
    conn_str=CONN_STR,
)

# -------------------------------------------------------------------- #
# 3) Lecture de la spécification OpenAPI DuckDuckGo
spec_path = root / "tools" / "duckduckgo.yaml"   # veille à avoir ce fichier
with open(spec_path, "r", encoding="utf-8") as f:
    spec_dict = yaml.safe_load(f)
spec = jsonref.loads(json.dumps(spec_dict))      # résout les $ref éventuels

# -------------------------------------------------------------------- #
# 4) Création de l’outil OpenAPI
duck_tool = OpenApiTool(
    name="duckduckgo_search",
    description="Recherche Web via DuckDuckGo",
    spec=spec,
    auth=OpenApiAnonymousAuthDetails()
)

# -------------------------------------------------------------------- #
# 5) Création de l’agent avec tool.definitions + tool.resources
agent = client.agents.create_agent(
    name="Researcher agent",
    model=MODEL,
    instructions=(
        """Tu es un agent de recherche.  
        **Tu n’as le droit de faire qu’une seule invocation** de l’outil DuckDuckGo pour un même sujet.  
        Après avoir obtenu la réponse, compose un résumé et transmets‑le.  
        N’effectue pas d’autres appels DuckDuckGo.
        """
    ),
    tools=duck_tool.definitions,       # le SDK s’occupe du format JSON
    tool_resources=duck_tool.resources # idem
)

print(f"\n Agent created !   ID : {agent.id}")
