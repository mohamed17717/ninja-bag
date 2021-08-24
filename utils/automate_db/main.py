from toolsframe.models import Tool, Category, ToolViewsFunctions, ToolDatabaseClass
from utils.automate_db.constants import TOOLS_VIEWS_NAMES, TOOLS_DOCUMENTATION_FILE, TOOLS_DB_CLASSES_NAMES
from utils.helpers import FileManager

import json


class ToolDatabaseHandler:
  def __init__(self, tool):
    self.tool = tool

  def get_or_create(self, model, **kwargs):
    obj = model.objects.filter(**kwargs).first()
    if not obj:
      obj = model.objects.create(**kwargs)
    return obj

  def create(self):
    tool_fields = {
      'name': self.tool.get('name'),
      'description': self.tool.get('description'),
      'app_type': self.tool.get('type'),
      'endpoints': self.tool.get('endpoints')
    }

    tool = Tool.objects.create(**tool_fields)

    categories = self.tool.get('category')
    for name in categories:
      category = self.get_or_create(Category, name=name)
      tool.category.add(category)

    return tool

  def update(self):
    tool = Tool.objects.get(tool_id=self.tool.get('tool_id'))

    tool.name = self.tool.get('name')
    tool.description = self.tool.get('description')
    tool.app_type = self.tool.get('type')
    tool.endpoints = self.tool.get('endpoints')

    tool.save()
    tool.category.clear()

    categories = self.tool.get('category')
    for name in categories:
      category = self.get_or_create(Category, name=name)
      tool.category.add(category)
    
    return tool

  def run(self):
    is_tool_exist = self.tool.get('tool_id')
    tool_setup_method = self.update if is_tool_exist else self.create
    tool_obj = tool_setup_method()

    return tool_obj


def set_tools_docs_to_table():
  print('## set tool docs ##')

  tools = FileManager.read(TOOLS_DOCUMENTATION_FILE, to_json=True)
  updated_tools = {}

  for name, info in tools.items():
    print(name)

    if info.get('is_changed', True):
      tool_handler = ToolDatabaseHandler({ **info, 'name': name })
      tool_obj = tool_handler.run()
      info.update({ 'tool_id': tool_obj.tool_id, 'is_changed': False  })

    updated_tools.update({ name: info })

  FileManager.write(TOOLS_DOCUMENTATION_FILE, updated_tools)

def set_tools_views_to_table():
  print('## set tool_views_functions ##')
  for name in TOOLS_VIEWS_NAMES:
    print(name)
    if not ToolViewsFunctions.objects.filter(name=name).first():
      ToolViewsFunctions.objects.create(name=name)

def set_tools_db_classes_to_table():
  print('## set tool_db_classes ##')
  for name in TOOLS_DB_CLASSES_NAMES:
    print(name)
    if not ToolDatabaseClass.objects.filter(name=name).first():
      ToolDatabaseClass.objects.create(name=name)


if __name__ == '__main__':
  set_tools_docs_to_table()
  set_tools_views_to_table()
  set_tools_db_classes_to_table()


## to run ##
# 1 # python manage.py shell
# 2 # exec(open('utils/automate_db/main.py').read())
