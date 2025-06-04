import os
from dotenv import load_dotenv

load_dotenv()

project = os.getenv('PROJECT')
author = os.getenv('AUTHOR')
#   util for helping managing resources tagging

#  my common tags are here but should be somewhere else
common_tags_list=[
    {
        'Key': 'project',
        'Value': project
    },
    {
        'Key': 'author',
        'Value': author
    }
]

# breaks down all values from a dict into smaller 
# dicts in aws tag format and returns a list of them
def tag_formatter(tags:dict)->list:
    new_list = []
    for key,value in tags.items():
        new_list.append(
            {
                'Key': key,
                'Value': value
            }
        )
    return new_list

# merges a common set of tags with the callers requested tags
def tagit(spec_tags:list)->list:
    return common_tags_list + spec_tags
