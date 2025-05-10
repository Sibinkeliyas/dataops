import uuid
from datetime import datetime
from azure.cosmos.aio import CosmosClient
from azure.cosmos import exceptions
from ..db_client import BaseClient as Client
from typing import List, Dict, Any
import asyncio
# from azure.cosmos import CosmosClient


class CosmosConversationClient(Client):
    
    def __init__(self, cosmosdb_endpoint: str, credential: any, database_name: str, container_name: str, enable_message_feedback: bool = False):
        self.cosmosdb_endpoint = cosmosdb_endpoint
        self.credential = credential
        self.database_name = database_name
        self.container_name = container_name
        self.enable_message_feedback = enable_message_feedback
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
            self.container_client = self.database_client.get_container_client(container_name)
        except exceptions.CosmosResourceNotFoundError:
            raise ValueError("Invalid CosmosDB container name") 
        

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

    async def create_conversation(self, user_id, title = '', group_id = None, datetime=None):
        conversation = {
            'id': str(uuid.uuid4()),  
            'type': 'conversation',
            'createdAt': datetime.utcnow().isoformat() if not datetime else datetime,  
            'updatedAt': datetime.utcnow().isoformat() if not datetime else datetime,  
            'userId': user_id,
            'groupId' : group_id if group_id != '' and group_id else 'none',
            'title': title
        }
        ## TODO: add some error handling based on the output of the upsert_item call
        resp = await self.container_client.upsert_item(conversation)  
        if resp:
            return resp
        else:
            return False
    
    async def upsert_conversation(self, conversation):
        resp = await self.container_client.upsert_item(conversation)
        if resp:
            return resp
        else:
            return False

    async def delete_conversation(self, user_id, conversation_id):
        conversation = await self.container_client.read_item(item=conversation_id, partition_key=user_id)        
        if conversation:
            resp = await self.container_client.delete_item(item=conversation_id, partition_key=user_id)
            return resp
        else:
            return True
        
    async def delete_conversations(self, user_id, group_id):
        conversations,_ = await self.get_conversations(user_id, 100, 'DESC', group_id=group_id)
        # tasks = []
    
        # # Iterate through conversations
        # for conversation in conversations:
        #     # Collect tasks to delete messages associated with the conversation
        #     messages = await self.get_messages(user_id, conversation['id'])
        #     self.container_client.delete_all_items_by_partition_key(match_condition=)
        #     for message in messages:
        #         tasks.append(self.container_client.delete_item(item=message['id'], partition_key=user_id))
            
        #     # Collect task to delete the conversation itself
        #     tasks.append(self.container_client.delete_item(item=conversation['id'], partition_key=user_id))
        
        # # Run all delete tasks concurrently using asyncio.gather()
        # await asyncio.gather(*tasks)
        for conversation in conversations:
            async for item in self.container_client.query_items(query=f"SELECT * FROM c WHERE c.conversationId = '{conversation['id']}' AND c.type='message' AND c.userId = '{user_id}'"):
                await self.container_client.delete_item(item,partition_key=user_id)
            await self.container_client.delete_item(item=conversation['id'], partition_key=user_id)
        return True


        
    async def delete_messages(self, conversation_id, user_id):
        ## get a list of all the messages in the conversation
        messages = await self.get_messages(user_id, conversation_id)
        response_list = []
        if messages:
            for message in messages:
                resp = await self.container_client.delete_item(item=message['id'], partition_key=user_id)
                response_list.append(resp)
            return response_list


    async def get_conversations(self, user_id, limit, sort_order = 'DESC', offset = 0,group_id=None,continuation_token=None):
        parameters = [
            {
                'name': '@userId',
                'value': user_id
            },
            {
                'name' : '@groupId',
                'value' : group_id if group_id != '' and group_id else 'none'
            }
        ]
        query = f"SELECT * FROM c where c.userId = @userId and c.groupId = @groupId and c.type='conversation' order by c.createdAt {sort_order}"
        # if limit is not None and continuation_token is None:
        #     query += f" offset {offset} limit {limit}" 
        

        # conversations = self.container_client.query_items(query=query, parameters=parameters,continuation_token=continuation_token)
        # if not continuation_token:

        #     conversations = []
        #     async for item in self.container_client.query_items(query=query, parameters=parameters):
        #         conversations.append(item)
        
        #     return conversations,None
        # else:
        resp = self.container_client.query_items(query=query, parameters=parameters,max_item_count=limit)
        pager = resp.by_page(continuation_token=continuation_token)
        try:
            page = await pager.__anext__()
            continuation_token = pager.continuation_token 
            items = []
            async for item in page:
                items.append(item)
        except StopAsyncIteration:
            items = []
            continuation_token = None
        return items, continuation_token

    async def get_conversation(self, user_id, conversation_id):
        parameters = [
            {
                'name': '@conversationId',
                'value': conversation_id
            },
            {
                'name': '@userId',
                'value': user_id
            }
        ]
        query = f"SELECT * FROM c where c.id = @conversationId and c.type='conversation' and c.userId = @userId"
        conversations = []
        async for item in self.container_client.query_items(query=query, parameters=parameters):
            conversations.append(item)

        ## if no conversations are found, return None
        if len(conversations) == 0:
            return None
        else:
            return conversations[0]
        

    async def update_conversation(self, conversation_id, user_id, title):
        conversation = await self.get_conversation(user_id, conversation_id)
        if conversation:
            conversation['title'] = title
            conversation['updatedAt'] = datetime.utcnow().isoformat()
            await self.upsert_conversation(conversation)
            return True
        else:
            return False
 
    async def create_message(self, uuid, conversation_id, user_id, input_message: dict, datetime=None, context=None):
        message = {
            'id': uuid,
            'type': 'message',
            'userId' : user_id,
            'createdAt': datetime.utcnow().isoformat() if not datetime else datetime,
            'updatedAt': datetime.utcnow().isoformat() if not datetime else datetime,
            'conversationId' : conversation_id,
            'role': input_message['role'],
            'content': input_message['content'],
            'feedback': {'positive_feedback' : None},
            'context': context
        }

        if self.enable_message_feedback:
            message['feedback'] = ''
        
        resp = await self.container_client.upsert_item(message)  
        if resp:
            ## update the parent conversations's updatedAt field with the current message's createdAt datetime value
            conversation = await self.get_conversation(user_id, conversation_id)
            if not conversation:
                return "Conversation not found"
            conversation['updatedAt'] = message['createdAt']
            await self.upsert_conversation(conversation)
            return resp
        else:
            return False
    
    async def create_question(self,user_id,group_id,question):
        question = {
            'id' : str(uuid.uuid4()),
            'type' : 'question',
            'userId' : '12334567890123',
            'createdAt': datetime.utcnow().isoformat(),
            'updatedAt': datetime.utcnow().isoformat(),
            'groupId' : group_id,
            'question' : question
        }
        response = await self.container_client.upsert_item(question)
        return response

    async def update_question(self,question_id,user_id,group_id,question):
        question_item = await self.container_client.read_item(item=question_id, partition_key='12334567890123')
        if question_item:
            question_item['updatedAt'] = datetime.utcnow().isoformat()
            question_item['question'] = question
            response = await self.container_client.upsert_item(question_item)
            return response
        else:
            return False
    
    async def delete_question(self,question_id,user_id):
        question_item = await self.container_client.read_item(item=question_id, partition_key='12334567890123')
        if question_item:
            response = await self.container_client.delete_item(item=question_id, partition_key='12334567890123')
            return response
        else:
            return False

    async def get_questions(self,group_id):
        parameters = [
            {
                'name': '@groupId',
                'value': group_id
            }
        ]
        query = f"SELECT * FROM c WHERE c.groupId = @groupId and c.type='question'"
        questions = []
        async for item in self.container_client.query_items(query=query, parameters=parameters):
            questions.append(item)
        return questions

    async def create_group(self,group_id, group_display_name,group_description, user_id,group_type,max_storage_size,max_file_size):
        # NotImplemented
        group = {
            'id' : str(uuid.uuid4()),
            'entraGroupId' : group_id,
            'groupName' : group_display_name,
            'type' : 'group',
            'groupDescription' : group_description,
            'groupType' : group_type,
            'createdAt': datetime.utcnow().isoformat(),
            'updatedAt': datetime.utcnow().isoformat(),
            'userId' : '123987654321',
            'maxStorageSize' : max_storage_size,
            'maxFileSize' : max_file_size,
            'groupLogoUrl' : None,
            'settings' : {}
            # 'group_' 
        }
        response = await self.container_client.upsert_item(group)
        return response

    def group_model(self):
        return {'id',
            'entraGroupId',
            'groupName',
            'type',
            'groupDescription',
            'groupType',
            'createdAt',
            'updatedAt',
            'userId',
            'maxStorageSize',
            'maxFileSize',
            'groupLogoUrl',
            'settings'
            }
    
    async def delete_group(self,group_id,user_id):
        group = await self.get_groups(group_id=group_id)
        if len(group) > 0:
            item_id = group[0]['id']
            partition_key = '123987654321'  # Use the correct partition key
            await self.container_client.delete_item(item=item_id, partition_key=partition_key)

    
    async def update_group(self,**group_args):  
        group_id = group_args.get('group_id')
        groups = await self.get_groups(group_id=group_id)
        if len(groups) > 0:
            group_item = groups[0]
            group_item['updatedAt'] = datetime.utcnow().isoformat()
            group_model = self.group_model()
            #only update the fields that are passed in the kwargs
            for key, value in group_args.items():
                if key in group_model:
                    group_item[key] = value
            await self.container_client.upsert_item(group_item)
            return True
        else:
            return False

        

    
    async def get_groups(self,id=None,group_id=None,group_type=None):
        filters = []
        parameters = []

        if id:
            filters.append("c.id = @id")
            parameters.append({'name': '@id', 'value': id})

        if group_id:
            filters.append("c.entraGroupId = @groupId")
            parameters.append({'name': '@groupId', 'value': group_id})

        if group_type:
            filters.append("c.groupType = @groupType")
            parameters.append({'name': '@groupType', 'value': group_type})

        # Base query
        query = "SELECT * FROM c WHERE c.type = 'group'"
        
        # Append dynamic filters if they exist
        if filters:
            query += " AND " + " AND ".join(filters)

        groups = []
        async for item in self.container_client.query_items(query=query, parameters=parameters):
            groups.append(item)
        
        if len(groups) == 0:
            return []
        else:
            return groups

    
    async def update_message_feedback(self, user_id, message_id, feedback):
        message = await self.container_client.read_item(item=message_id, partition_key=user_id)
        if message:
            message['feedback']['positive_feedback'] = feedback
            resp = await self.container_client.upsert_item(message)
            return resp
        else:
            return False

    async def get_messages(self, user_id, conversation_id):
        parameters = [
            {
                'name': '@conversationId',
                'value': conversation_id
            },
            {
                'name': '@userId',
                'value': user_id
            }
        ]
        query = f"SELECT * FROM c WHERE c.conversationId = @conversationId AND c.type='message' AND c.userId = @userId ORDER BY c.timestamp ASC"
        messages = []
        async for item in self.container_client.query_items(query=query, parameters=parameters):
            messages.append(item)

        return messages
    

    
    async def close(self):
        await self.cosmosdb_client.close()

    async def create_prompt(self, user_id: str, prompt_text: str,status: str = 'active',id: str = None):
        prompt = {
            'id': id if id else str(uuid.uuid4()),
            'type': 'prompt',
            'userId': '123987654321',
            'status' : status,
            'ts': datetime.utcnow().isoformat(),
            'text': prompt_text
        }
        response = await self.container_client.upsert_item(prompt)
        return response

    async def update_prompt(self, prompt_id: str, prompt_text: str,status: str = 'active'):
        prompt_item = await self.container_client.read_item(item=prompt_id, partition_key='123987654321')
        if prompt_item:
            prompt_item['ts'] = datetime.utcnow().isoformat()
            prompt_item['text'] = prompt_text
            prompt_item['status'] = status
            response = await self.container_client.upsert_item(prompt_item)
            return response
        else:
            return False

    async def delete_prompt(self, prompt_id: str, user_id: str):
        try:
            await self.container_client.delete_item(item=prompt_id, partition_key='123987654321')
            return True
        except exceptions.CosmosResourceNotFoundError:
            return False

    async def get_prompts(self, id=None,status: str = None):
        filters = []
        parameters = []
        if id:
            filters.append("c.id = @id")
            parameters.append({'name': '@id', 'value': id})
        
        query = "SELECT * FROM c WHERE c.type = 'prompt'"
        if status:
            filters.append("c.status = @status")
            parameters.append({'name': '@status', 'value': status})
        if filters:
            query += " AND " + " AND ".join(filters)
        prompts = []
        async for item in self.container_client.query_items(query=query, parameters=parameters):
            prompts.append(item)
        return prompts


    async def create_workspace_prompt(self, base_prompt_id: str, variables: dict[str, any], text: str, group_id: str,active: bool = False):
        workspace_prompt = {
            'id': str(uuid.uuid4()),
            'type': 'workspace-prompt',
            'userId': '123987654321',
            'basePromptId': base_prompt_id,
            'variables': variables,
            'text': text,
            'ts': datetime.utcnow().isoformat(),
            'active': active,
            'groupId': group_id
        }
        response = await self.container_client.upsert_item(workspace_prompt)
        return response

    async def update_workspace_prompt(self, workspace_prompt_id: str, variables: dict[str, any], text: str):
        workspace_prompt_item = await self.container_client.read_item(item=workspace_prompt_id, partition_key='123987654321')
        if workspace_prompt_item:
            workspace_prompt_item['ts'] = datetime.utcnow().isoformat()
            workspace_prompt_item['variables'] = variables
            workspace_prompt_item['text'] = text
            response = await self.container_client.upsert_item(workspace_prompt_item)
            return response
        else:
            return False

    async def delete_workspace_prompt(self, workspace_prompt_id: str):
        try:
            await self.container_client.delete_item(item=workspace_prompt_id, partition_key='123987654321')
            return True
        except exceptions.CosmosResourceNotFoundError:
            return False

    async def list_workspace_prompts(self, **prompt_args):
        filters = ["c.type = 'workspace-prompt'"]
        parameters = []
        
        for key, value in prompt_args.items():
            filters.append(f"c.{key} = @{key}")
            parameters.append({"name": f"@{key}", "value": value})
        
        query = "SELECT * FROM c WHERE " + " AND ".join(filters)
        workspace_prompts = []
        async for item in self.container_client.query_items(query=query, parameters=parameters):
            workspace_prompts.append(item)
        return workspace_prompts

    async def deactivate_all_workspace_prompts(self, group_id: str, except_prompt_id: str = None) -> None:
        query = f"SELECT * FROM c WHERE c.type = 'workspace-prompt' AND c.groupId = '{group_id}' and c.active = true"
        
        
        async for prompt in self.container_client.query_items(query=query):
            if prompt['id'] != except_prompt_id and prompt.get('active', False):
                prompt['active'] = False
                await self.container_client.upsert_item(prompt)

    async def get_active_workspace_prompts(self, group_id: str) -> List[Dict[str, Any]]:
        query = f"SELECT * FROM c WHERE c.type = 'workspace-prompt' AND c.groupId = '{group_id}' AND c.active = true"
        prompts = []
        async for prompt in self.container_client.query_items(query=query):
            prompts.append(prompt)
        return prompts

    async def get_workspace_prompt(self, workspace_prompt_id: str) -> Dict[str, Any]:
        query = f"SELECT * FROM c WHERE c.id = '{workspace_prompt_id}' AND c.type = 'workspace-prompt'"
        results = []
        async for prompt in self.container_client.query_items(query=query):
            results.append(prompt)
        return results[0] if results else []

    async def update_workspace_prompt(self, workspace_prompt_id: str, **kwargs) -> Dict[str, Any]:
        prompt = await self.get_workspace_prompt(workspace_prompt_id)
        if not prompt:
            raise ValueError(f"Workspace prompt with id {workspace_prompt_id} not found")
        
        for key, value in kwargs.items():
            prompt[key] = value
        
        updated_prompt = await self.container_client.upsert_item(prompt)
        return updated_prompt
    





    # Policy Section

    async def create_policy(self, policy_text: str, status: str = 'active'):
        policy = {
            'id': str(uuid.uuid4()),
            'type': 'policy',
            'text': policy_text,
            'userId': '1239876543211',
            'createdAt': datetime.utcnow().isoformat(),
            'updatedAt': datetime.utcnow().isoformat()
        }
        response = await self.container_client.upsert_item(policy)
        return response

    async def update_policy(self, policy_id: str , policy_text: str):

        policy_item = await self.container_client.read_item(item=policy_id, partition_key='1239876543211')
        if policy_item:
            policy_item['updatedAt'] = datetime.utcnow().isoformat()
            policy_item['text'] = policy_text
            response = await self.container_client.upsert_item(policy_item)
            return response
        else:
            return None


    async def delete_policy(self, policy_id: str):
        try:
            await self.container_client.delete_item(item=policy_id, partition_key='1239876543211')
            return True
        except exceptions.CosmosResourceNotFoundError:
            return False
    
    async def list_policies(self, **policy_args):
        filters = ["c.type = 'policy'"]
        parameters = []
        
        for key, value in policy_args.items():
            filters.append(f"c.{key} = @{key}")
            parameters.append({"name": f"@{key}", "value": value})
        
        query = "SELECT * FROM c WHERE " + " AND ".join(filters)
        policies = []
        async for item in self.container_client.query_items(query=query, parameters=parameters):
            policies.append(item)
        return policies


    # End of Policy Section


    # Prompt Request Section
    async def create_request_prompt(self, user_id: str, prompt_text: str, group_id: str):
        """Create a new prompt request with pending status"""
        prompt = {
            'id': str(uuid.uuid4()),
            'type': 'prompt-request',
            'userId': '123987654321',
            'status': 'pending',
            'ts': datetime.utcnow().isoformat(),
            'text': prompt_text,
            # 'requestedBy': user_id,
            'groupId': group_id
        }
        response = await self.container_client.upsert_item(prompt)
        return response

    async def update_request_prompt(self, prompt_id: str, prompt_text: str = None, status: str = None):
        """Update a prompt request's text and/or status"""
        prompt_item = await self.container_client.read_item(item=prompt_id, partition_key='123987654321')
        if prompt_item:
            prompt_item['ts'] = datetime.utcnow().isoformat()
            if prompt_text is not None:
                prompt_item['text'] = prompt_text
            if status is not None:
                prompt_item['status'] = status
            response = await self.container_client.upsert_item(prompt_item)
            return response
        else:
            return False

    async def delete_request_prompt(self, prompt_id: str):
        """Delete a prompt request"""
        try:
            await self.container_client.delete_item(item=prompt_id, partition_key='123987654321')
            return True
        except exceptions.CosmosResourceNotFoundError:
            return False

    async def list_request_prompts(self, status: str = None, group_id: str = None, prompt_id: str = None):
        """List all prompt requests, optionally filtered by status, group_id, and prompt_id"""
        filters = ["c.type = 'prompt-request'"]
        parameters = []
        
        if status:
            filters.append("c.status = @status")
            parameters.append({'name': '@status', 'value': status})
        
        if group_id:
            filters.append("c.groupId = @groupId")
            parameters.append({'name': '@groupId', 'value': group_id})
        
        if prompt_id:
            filters.append("c.id = @promptId")
            parameters.append({'name': '@promptId', 'value': prompt_id})
        
        query = "SELECT * FROM c WHERE " + " AND ".join(filters)
        prompts = []
        async for item in self.container_client.query_items(query=query, parameters=parameters):
            prompts.append(item)
        return prompts
    
    # End of Prompt Request Section


    # User Prompt Section

    async def create_user_prompt(self, user_id: str, title : str,prompt_text: str):
        user_prompt = {
            'id': str(uuid.uuid4()),
            'type': 'user-prompt',
            'userId': '12398765432111',
            'title': title,
            'text': prompt_text,
            'createdAt': datetime.utcnow().isoformat(),
            'updatedAt': datetime.utcnow().isoformat()
        }
        response = await self.container_client.upsert_item(user_prompt)
        return response
    

    async def update_user_prompt(self, user_prompt_id: str, title: str, prompt_text: str):
        user_prompt_item = await self.container_client.read_item(item=user_prompt_id, partition_key='12398765432111')
        if user_prompt_item:
            user_prompt_item['updatedAt'] = datetime.utcnow().isoformat()
            user_prompt_item['title'] = title
            user_prompt_item['text'] = prompt_text
            response = await self.container_client.upsert_item(user_prompt_item)
            return response
        else:
            return False

    async def update_user_prompt_kwargs(self, user_prompt_id: str, **kwargs) -> Dict[str, Any]:
        """
        Alternative version of update_user_prompt that accepts dynamic fields
        """
        query = f"SELECT * FROM c WHERE c.id = '{user_prompt_id}' AND c.type = 'user-prompt'"
        results = []
        async for prompt in self.container_client.query_items(query=query):
            results.append(prompt)
            
        if not results:
            raise ValueError(f"User prompt with id {user_prompt_id} not found")
            
        prompt = results[0]
        prompt['updatedAt'] = datetime.utcnow().isoformat()
        
        for key, value in kwargs.items():
            prompt[key] = value
            
        updated_prompt = await self.container_client.upsert_item(prompt)
        return updated_prompt
    
    async def delete_user_prompt(self, user_prompt_id: str):
        try:
            await self.container_client.delete_item(item=user_prompt_id, partition_key='12398765432111')
            return True
        except exceptions.CosmosResourceNotFoundError:
            return False
    
    async def list_user_prompts(self,id=None, title: str = None,active: bool = None):
        filters = ["c.type = 'user-prompt'"]
        parameters = []
        if id or title or active is not None:
            if id:
                filters.append("c.id = @id")
                parameters.append({'name': '@id', 'value': id})
            if title:
                filters.append("c.title = @title")
                parameters.append({'name': '@title', 'value': title})
            if active is not None:
                filters.append("c.active = @active")
                parameters.append({'name': '@active', 'value': active})
        query = "SELECT * FROM c WHERE " + " AND ".join(filters)
        user_prompts = []
        async for item in self.container_client.query_items(query=query, parameters=parameters):
            user_prompts.append(item)
        return user_prompts
    
    async def deactivate_all_user_prompts(self):
        query = "SELECT * FROM c WHERE c.type = 'user-prompt' AND c.active = true"
        
        async for prompt in self.container_client.query_items(query=query):
            if prompt.get('active', False):
                prompt['active'] = False
                await self.container_client.upsert_item(prompt)
        return True
    
        

# End of User Prompt Section

# Batch processing section

    async def create_batch_processing(self, group_id: str = None, userId : str = None):
        batch = {
            'id': str(uuid.uuid4()),
            'type': 'batch-processing',
            'groupId': group_id,
            'userId': userId if userId else '000000000000-0003-1000-1000-100000000000',
            'status': 'pending',
            'documents': [],
            'createdAt': datetime.utcnow().isoformat(),
            'updatedAt': datetime.utcnow().isoformat()
        }
        response = await self.container_client.upsert_item(batch)
        return response


    async def update_batch_processing(self, batch_id: str, userId : str = None, **kwargs):
        batch_item = await self.container_client.read_item(item=batch_id, partition_key=userId if userId else '000000000000-0003-1000-1000-100000000000')
        if batch_item:
            batch_item['updatedAt'] = datetime.utcnow().isoformat()
            for key, value in kwargs.items():
                batch_item[key] = value
            response = await self.container_client.upsert_item(batch_item)
            return response
        else:
            return False
        
    
    async def delete_batch_processing(self, batch_id: str, userId : str = None):
        try:
            await self.container_client.delete_item(item=batch_id, partition_key=userId if userId else '000000000000-0003-1000-1000-100000000000')
            return True
        except exceptions.CosmosResourceNotFoundError:
            return False
    
    async def list_batch_processing(self, group_id: str = None, status: str = None, batch_id: str = None, userId : str = None,order_by = 'DESC'):
        filters = ["c.type = 'batch-processing'"]
        parameters = []
        if userId:
            filters.append("c.userId = @userId")
            parameters.append({'name' : '@userId','value' : userId})
        if group_id:
            filters.append("c.groupId = @groupId")
            parameters.append({'name': '@groupId', 'value': group_id})
        if status:
            filters.append("c.status = @status")
            parameters.append({'name': '@status', 'value': status})
        if batch_id:
            filters.append("c.id = @batchId")
            parameters.append({'name': '@batchId', 'value': batch_id})
        

        query = "SELECT * FROM c WHERE " + " AND ".join(filters) + f" ORDER BY c.createdAt {order_by}"
        batch_processing = []
        async for item in self.container_client.query_items(query=query, parameters=parameters):
            batch_processing.append(item)
        return batch_processing
    

# End of Batch processing section


