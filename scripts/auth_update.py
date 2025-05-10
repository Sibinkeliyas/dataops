import asyncio
import os
import sys
from pathlib import Path

# Add project root to Python path
project_root = str(Path(__file__).parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from azure.identity.aio import AzureDeveloperCliCredential
from msgraph import GraphServiceClient
from msgraph.generated.models.application import Application
from msgraph.generated.models.public_client_application import PublicClientApplication
from msgraph.generated.models.spa_application import SpaApplication
from msgraph.generated.models.web_application import WebApplication
import db_migrations
# from app.backend.db.service.sql.sql_client import 
from azure.identity import DefaultAzureCredential, ClientSecretCredential
from azure.cosmos import CosmosClient
from app.backend.db.service.cosmos.cosmos_client import CosmosConversationClient
from auth_common import get_application, test_authentication_enabled
from msgraph.generated.models.group import Group


prompt = '''
Assistant helps the <group_name> employees with their queries and questions. Be brief in your answers.
Answer ONLY with the facts listed in the list of sources below. If there isn't enough information below, say you don't know. But then ask if the user if they are interested in searching for the AI model's general knowledge database or that they can upload documents to the chat by using the menu located on the top right corner of the screen.
Annotate/reference these answers as coming from "LLM Model Knowledge" source document for content generated from the LLM Model's knowledge.
If asking a clarifying question to the user would help, ask the question.
User might also ask questions related to the conversation. You'll be provided the chat history from which you can refer and answer the question.
For tabular information return it as an html table. Do not return markdown format. If the question is not in English, answer in the language used in the question.
Each source has a name followed by colon and the actual information, always include the source name for each fact you use in the response. Use square brackets to reference the source, for example [info1.txt]. Don't combine sources, list each source separately, for example [info1.txt][info2.pdf]. If there are no sources, mention it's coming from your LLM Model Knowledge as the source.

Additional instructions:
-----------------------------------
<additional_instructions>
-----------------------------------
'''

async def init_and_update_cosmos():
    credentials = DefaultAzureCredential(exclude_shared_token_cache_credential=True)
    DB_CONNECTION = {
        'container_name' : os.environ['AZURE_COSMOSDB_CONVERSATIONS_CONTAINER'],
        'database_name' : os.environ['AZURE_COSMOSDB_DATABASE'],
        'credential' : credentials,
        'cosmosdb_endpoint' : os.environ['AZURE_COSMOSDB_ENDPOINT']
    }

    try:
        db_client  = CosmosConversationClient(**DB_CONNECTION)
        if db_client:
            groups = await db_client.get_groups()
            admin_groups = [group for group in groups if group['groupType'] == 'admin']
            if not admin_groups or len(admin_groups) < 1:
                print("No admin group found, creating admin group")
                credentials = ClientSecretCredential(tenant_id=os.getenv('AZURE_TENANT_ID'),
                                                    client_id=os.getenv('AZURE_SERVER_APP_ID'),
                                                    client_secret=os.getenv('AZURE_SERVER_APP_SECRET'))


                scopes = [
                    'https://graph.microsoft.com/.default'
                ]

                graph_client = GraphServiceClient(credentials=credentials, scopes=scopes)
                
                group_request = Group(
                    description='Sample description for admin group',
                    display_name='Allnex admin group',
                    mail_enabled=False,
                    security_enabled=True,
                    mail_nickname='NotSet',
                    group_types=[]

                )
                # result = await graph_client.groups.post(group_request)
                result = await graph_client.directory.administrative_units.by_administrative_unit_id(os.getenv('AZURE_ADMINISTRATIVE_UNIT','')).members.post(group_request);

                db_response = await db_client.create_group(group_id=result.id,
                                            group_display_name='Allnex AI chat admin group',
                                            group_description='Sample description for admin group',
                                            group_type='admin',
                                            user_id='00000000-0000-0000-0000-000000000000',
                                            max_storage_size=5,
                                        max_file_size=1
                                        )
        else:
            print("Admin group already exists, skipping creation")
        
        prompts = await db_client.get_prompts(id='default')
        if not prompts or len(prompts) < 1:
            print("No prompts found, creating default prompts")
            await db_client.create_prompt(id='default',user_id='000000',
                                        prompt_text=prompt)
        elif prompts and len(prompts) > 0:
            print("Default prompts already exist, updating them...")
            await db_client.update_prompt(prompt_id='default', prompt_text=prompt)

    except Exception as e:
        print("Error", e)
    finally:
        await db_client.close()

async def main():
    if not test_authentication_enabled():
        print("Not updating authentication.")
        exit(0)

    auth_tenant = os.getenv("AZURE_AUTH_TENANT_ID", os.environ["AZURE_TENANT_ID"])
    credential = AzureDeveloperCliCredential(tenant_id=auth_tenant)

    scopes = ["https://graph.microsoft.com/.default"]
    graph_client = GraphServiceClient(credentials=credential, scopes=scopes)

    uri = os.getenv("BACKEND_URI")
    client_app_id = os.getenv("AZURE_CLIENT_APP_ID", None)
    if client_app_id:
        client_object_id = await get_application(graph_client, client_app_id)
        if client_object_id:
            print(f"Updating redirect URIs for client app ID {client_app_id}...")
            # Redirect URIs need to be relative to the deployed application
            app = Application(
                public_client=PublicClientApplication(redirect_uris=[]),
                spa=SpaApplication(
                    redirect_uris=[
                        "http://localhost:50505/redirect",
                        "http://localhost:5173/redirect",
                        f"{uri}/redirect",
                    ]
                ),
                web=WebApplication(
                    redirect_uris=[
                        f"{uri}/.auth/login/aad/callback",
                    ]
                ),
            )
            await graph_client.applications.by_application_id(client_object_id).patch(app)
            print(f"Application update for client app id {client_app_id} complete.")
    
    # # DB Migrations
    # if os.getenv('DB_TYPE','SQL') == 'SQL':
    #     db_migrations.run()

    db_type = os.getenv('DB_TYPE','COSMOS')
    if db_type == 'COSMOS':
        await init_and_update_cosmos()

if __name__ == "__main__":
    asyncio.run(main())
