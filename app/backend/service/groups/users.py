# from quart import current_app
# from azure.identity import ClientSecretCredential
# from msgraph.generated.models.group import Group 
# from msgraph import GraphServiceClient
# # from azure.identity import DeviceCodeCredential
# from msgraph.generated.models.o_data_errors.o_data_error import ODataError
# from msgraph.generated.groups.groups_request_builder import GroupsRequestBuilder
# from kiota_abstractions.base_request_configuration import RequestConfiguration
# from msgraph.generated.users.users_request_builder import UsersRequestBuilder
# from kiota_abstractions.base_request_configuration import RequestConfiguration
# from msgraph.generated.models.reference_create import ReferenceCreate
# import os


# async def get_group_members(group_id: str,user_type: list[str]):
#     owners = 'owners' in user_type
#     members = 'members' in user_type
#     credentials = ClientSecretCredential(tenant_id=os.getenv('AZURE_TENANT_ID'),
#                                              client_id=os.getenv('AZURE_SERVER_APP_ID'),
#                                              client_secret=os.getenv('AZURE_SERVER_APP_SECRET'))
        
#     graph_client = GraphServiceClient(credentials=credentials)
#     query_params = UsersRequestBuilder.UsersRequestBuilderGetQueryParameters(
#             count=True,
#             orderby=["displayName"],
#             select=["displayName", "id", "mail"],
#         )

#     request_configuration = RequestConfiguration(
#         query_parameters=query_params,
#     )
#     if members:
#         members = await graph_client.groups.by_group_id(group_id=group_id).members.graph_user.get(request_configuration=request_configuration)
#         members_list = []
#         for member in members.value:
#             members_list.append({
#             'id': member.id,
#             'name': member.display_name,
#             'mail': member.mail
#         })
    

