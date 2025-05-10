import os
import sys
from alembic.config import Config
from alembic import command
import traceback


def run():

    # Construct the path to alembic.ini in the scripts directory
    alembic_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'alembic.ini')

    # Check if the alembic.ini file exists
    if not os.path.exists(alembic_path):
        print(f'Error: The file {alembic_path} does not exist.')
    else:
        alembic_config = Config(alembic_path)

        try:
            print('Running Migrations ...')
            command.upgrade(alembic_config, "head")
            print("Migrations completed !!")
        except Exception as e:
            print(f'Error: {str(e)}')
        # traceback.print_exc() 
