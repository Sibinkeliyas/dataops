import uuid
from datetime import datetime
from azure.cosmos.aio import CosmosClient
from azure.cosmos import exceptions
from ..db_client import BaseClient as Client
from typing import List, Dict, Any
import logging

class CosmosDocumentClient():
    def __init__(self, cosmosdb_endpoint: str, credential: any, database_name: str):
        self.cosmosdb_endpoint = cosmosdb_endpoint
        self.credential = credential
        self.database_name = database_name
        self.container_name = 'documents'  # Static container name
        self.async_mode = True

        try:
            self.cosmosdb_client = CosmosClient(self.cosmosdb_endpoint, credential=credential)
        except exceptions.CosmosHttpResponseError as e:
            if e.status_code == 401:
                raise ValueError("Invalid credentials") from e
            else:
                raise ValueError("Invalid CosmosDB endpoint") from e

        try:
            self.database_client = self.cosmosdb_client.get_database_client(database_name)
        except exceptions.CosmosResourceNotFoundError:
            raise ValueError("Invalid CosmosDB database name")
        
        try:
            logging.info(f"Creating container {self.container_name} with partition key /type")
            # print(f"Creating container {self.container_name} with partition key /type")
            # self.database_client.create_container_if_not_exists(self.container_name, partition_key="/type")
            self.container_client = self.database_client.get_container_client(self.container_name)
        except exceptions.CosmosResourceNotFoundError:
            raise ValueError("Invalid CosmosDB container name")
        return None

    async def ensure(self):
        if not self.cosmosdb_client or not self.database_client or not self.container_client:
            return False, "CosmosDB client not initialized correctly"
        try:
            database_info = await self.database_client.read()
        except:
            return False, f"CosmosDB database {self.database_name} on account {self.cosmosdb_endpoint} not found"
        
        try:
            container_info = await self.container_client.read()
        except:
            return False, f"CosmosDB container {self.container_name} not found"
            
        return True, "CosmosDB client initialized successfully"

    async def create_task(self, starts_with: str = None, 
                          ends_with: str = None, 
                          contains: str = None, 
                          extensions: List[str] = None, 
                          task_name: str = None,
                          tags: List[str] = [],
                          status: str = 'active', 
                          metadata: Dict = {}):
        task = {
            'id': str(uuid.uuid4()),
            'type': 'task',
            'startsWith': starts_with,
            'endsWith': ends_with,
            'contains': contains,
            'extensions': extensions,
            'taskName': task_name,
            'status': status,
            'metadata': metadata or {},
            'tags': tags,
            'workspace_or_oid' : 'global',
            'createdAt': datetime.utcnow().isoformat(),
            'updatedAt': datetime.utcnow().isoformat(),
        }
        response = await self.container_client.upsert_item(task)
        return response


    async def check_file_pattern(self, file_name: str = None, extensions: List[str] = None):
        filters = ["c.type = 'task'"]  # Ensure only "task" type documents
        parameters = []

        # Ensure `file_name` contains `c.contains` (case-insensitive)
        if file_name:
            filters.append("CONTAINS(LOWER(@file_name), LOWER(c.contains))")
            parameters.append({'name': '@file_name', 'value': file_name.lower()})  # Convert input to lowercase

        # Check if any extension matches, ensuring a dot (.)
        if extensions:
            normalized_extensions = [ext if ext.startswith('.') else f".{ext}" for ext in extensions]  # Ensure '.' prefix
            filters.append("EXISTS (SELECT VALUE ext FROM ext IN c.extensions WHERE ARRAY_CONTAINS(@extensions, ext))")
            parameters.append({'name': '@extensions', 'value': normalized_extensions})  # Pass list directly (no tuple)

        # Build query
        query = "SELECT * FROM c"
        if filters:
            query += " WHERE " + " AND ".join(filters)

        query += " ORDER BY c.createdAt DESC"

        tasks = []
        print("QUERY:", query)
        print("PARAMETERS:", parameters)

        async for item in self.container_client.query_items(query=query, parameters=parameters):
            tasks.append(item)

        return tasks





    
    async def update_task(self, task_id: str, **task_args):
        task = await self.container_client.read_item(item=task_id, partition_key='global')
        if task:
            task['updatedAt'] = datetime.utcnow().isoformat()
            for key, value in task_args.items():
                task[key] = value
            response = await self.container_client.upsert_item(task)
            return response
        return None

    async def delete_task(self, task_id: str, user_id: str):
        try:
            await self.container_client.delete_item(item=task_id, partition_key='global')
            return True
        except exceptions.CosmosResourceNotFoundError:
            return False

    async def get_task(self, task_id: str):
        try:
            task = await self.container_client.read_item(item=task_id, partition_key='global')
            return task
        except exceptions.CosmosResourceNotFoundError:
            return None

    async def list_tasks(self, type: str = None, status: str = None, task_type: str = None, starts_with: str = None, ends_with: str = None, contains: str = None, extensions: list = None):
        filters = ["c.type = 'task'"]
        parameters = []

        if type:
            filters.append("c.type = @type")
            parameters.append({'name': '@type', 'value': type})
        
        if status:
            filters.append("c.status = @status")
            parameters.append({'name': '@status', 'value': status})
        
        if starts_with:
            filters.append("c.startsWith = @startsWith")
            parameters.append({'name': '@startsWith', 'value': starts_with})
        
        if ends_with:
            filters.append("c.endsWith = @endsWith")
            parameters.append({'name': '@endsWith', 'value': ends_with})
        
        if contains:
            filters.append("c.contains = @contains")
            parameters.append({'name': '@contains', 'value': contains})

        #extensions is a list of strings not use ARRAY_CONTAINS
        if extensions:
            filters.append("ARRAY_CONTAINS(c.extensions, @extensions)")
            parameters.append({'name': '@extensions', 'value': extensions})
        

        query = "SELECT * FROM c WHERE " + " AND ".join(filters) + " ORDER BY c.createdAt DESC"
        tasks = []
        async for item in self.container_client.query_items(query=query, parameters=parameters):
            tasks.append(item)
        return tasks
    
    async def create_tag(self, tag : str ):
        tag = await self.container_client.upsert_item({
            'id': str(uuid.uuid4()),
            'type': 'tag',
            'name': tag,
            'workspace_or_oid' : 'global',
            'createdAt': datetime.utcnow().isoformat(),
            'status': 'active',
        })
        return tag

    async def get_tags(self, status: str = 'active', name: str = None, id: str = None):
        filters = ["c.type = 'tag'"]
        parameters = []

        if status:
            filters.append("c.status = @status")
            parameters.append({'name': '@status', 'value': status})

        if name:
            filters.append("c.name = @name")
            parameters.append({'name': '@name', 'value': name})

        if id:
            filters.append("c.id = @id")
            parameters.append({'name': '@id', 'value': id})

        query = "SELECT * FROM c WHERE " + " AND ".join(filters) + " ORDER BY c.createdAt DESC"
        tags = []
        async for item in self.container_client.query_items(query=query, parameters=parameters):
            tags.append(item)
        return tags

    async def tag_search(self, tag_name: str):
        query = "SELECT * FROM c WHERE c.type = 'tag' AND LOWER(c.name) LIKE @name"
        parameters = [{'name': '@name', 'value': f"%{tag_name.lower()}%"}]
        
        tags = [item async for item in self.container_client.query_items(query=query, parameters=parameters)]
        return tags
    


    async def create_document(self, file_name : str, 
                              file_extension : str, 
                              workspace_or_oid : str, 
                              file_url : str, 
                              file_size : int, 
                              uploadedFrom : str,
                              tags : List[str],
                              file_metadata : Dict = {}):
        document = {
            'id': str(uuid.uuid4()),
            'type': 'document',
            'name': file_name,
            'extension': file_extension,
            'workspace_or_oid': workspace_or_oid,
            'url': file_url,
            'size': file_size,
            'metadata': file_metadata,
            'uploadedFrom' : uploadedFrom,
            'tags' : tags,
            'createdAt': datetime.utcnow().isoformat(),
            'updatedAt': datetime.utcnow().isoformat(),
        }
        response = await self.container_client.upsert_item(document)
        return response
    



    async def delete_document(self, file_url: str, workspace_or_oid: str):
        try:

            filters = ["c.type = 'document'", "c.workspace_or_oid = @workspace_or_oid", "c.url = @file_url"]
            parameters = [
                {'name': '@file_url', 'value': file_url},
                {'name': '@workspace_or_oid', 'value': workspace_or_oid}
            ]

            query = f"SELECT * FROM c WHERE {' AND '.join(filters)}"

            print("Executing Query:", query)
            print("Parameters:", parameters)

            # Fetch document
            documents = []
            async for doc in self.container_client.query_items(query=query, parameters=parameters):
                documents.append(doc)

            if not documents:
                raise ValueError("Document not found")

            # Ensure correct partition key usage
            document = documents[0]
            partition_key_value = document.get("workspace_or_oid")  # Ensure it matches stored structure

            # Delete document
            await self.container_client.delete_item(item=document['id'], partition_key=partition_key_value)
            print(f"Deleted document: {document['id']}")
            return True

        except Exception as e:
            print(f"Error deleting document: {e}")
            return False

        
    async def file_search(self, oid: str, group_id: str = None, match_all_tags: List[str] = None, match_any_tags: List[str] = None):
        filters = ["c.type = 'document'"]
        parameters = []

        # Match ALL tags (every tag in match_all_tags must exist in c.tags)
        if match_all_tags:
            for i, tag in enumerate(match_all_tags):
                param_name = f"@tag_all_{i}"
                filters.append(f"ARRAY_CONTAINS(c.tags, {param_name})")
                parameters.append({'name': param_name, 'value': tag})
        if group_id:
            filters.append("c.workspace_or_oid = @group_id")
            parameters.append({'name': '@group_id', 'value': group_id})
        else:
            filters.append("c.workspace_or_oid = @oid")
            parameters.append({'name': '@oid', 'value': oid})

        # Match ANY tag (at least one tag in match_any_tags must exist in c.tags)
        if match_any_tags:
            filters.append(f"EXISTS (SELECT VALUE t FROM t IN c.tags WHERE ARRAY_CONTAINS(@tags_any, t))")
            parameters.append({'name': '@tags_any', 'value': match_any_tags})

        # Construct the query
        query = "SELECT * FROM c"
        if filters:
            query += " WHERE " + " AND ".join(filters)  # AND for match_all, EXISTS for match_any

        query += " ORDER BY c.createdAt DESC"

        documents = []

        async for doc in self.container_client.query_items(query=query, parameters=parameters):
            documents.append(doc)

        return documents


    
    async def close(self):
        await self.cosmosdb_client.close() 