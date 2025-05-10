from abc import ABC, abstractmethod
from typing import List, Dict, Any

class BaseClient(ABC):

    def __init__(self,async_mode : bool):
        self.async_mode = async_mode

    @abstractmethod
    def ensure(self):
        pass

    @abstractmethod
    def create_conversation(self):
        pass

    @abstractmethod
    def delete_conversation(self):
        pass

    @abstractmethod
    def create_message(self):
        pass

    @abstractmethod
    def delete_messages(self):
        pass

    @abstractmethod
    def get_messages(self):
        pass

    @abstractmethod
    def create_group(self):
        pass

    @abstractmethod
    def get_groups(self):
        pass

    @abstractmethod
    def delete_group(self):
        pass

    async def deactivate_all_workspace_prompts(self, group_id: str, except_prompt_id: str = None) -> None:
        """
        Set all workspace prompts for a group to inactive, except for the specified prompt.
        
        :param group_id: The ID of the group
        :param except_prompt_id: The ID of the prompt to exclude from deactivation (optional)
        """
        raise NotImplementedError("This method must be implemented by subclasses")

    async def get_active_workspace_prompts(self, group_id: str) -> List[Dict[str, Any]]:
        """
        Get all active workspace prompts for a group.
        
        :param group_id: The ID of the group
        :return: A list of active workspace prompts
        """
        raise NotImplementedError("This method must be implemented by subclasses")

    async def get_workspace_prompt(self, workspace_prompt_id: str) -> Dict[str, Any]:
        """
        Get a specific workspace prompt by its ID.
        
        :param workspace_prompt_id: The ID of the workspace prompt
        :return: The workspace prompt data
        """
        raise NotImplementedError("This method must be implemented by subclasses")

    async def update_workspace_prompt(self, workspace_prompt_id: str, **kwargs) -> Dict[str, Any]:
        """
        Update a workspace prompt.
        
        :param workspace_prompt_id: The ID of the workspace prompt to update
        :param kwargs: The fields to update
        :return: The updated workspace prompt data
        """
        raise NotImplementedError("This method must be implemented by subclasses")
