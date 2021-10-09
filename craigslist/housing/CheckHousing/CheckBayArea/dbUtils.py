from azure.cosmosdb.table.tableservice import TableService
from azure.common import AzureConflictHttpError
import os

def insertPosts(posts):

    envVarName = "scriptsStorageConnString"
    connString = os.environ.get(envVarName)
    i = 0

    try:
        for post in posts:
        
            table_service = TableService(connection_string=connString)
            table_service.insert_entity('housingSearchResults', post)
            i+= 1

    except AzureConflictHttpError as e:
        print(f"Conflict hit after inserting {i} entries")

    print(f"Inserted {i} entries")
