from toolsframe.models import ToolViewsFunctions, ToolDatabaseClass
from utils.automate_db.constants import TOOLS_VIEWS_NAMES, TOOLS_DB_CLASSES_NAMES


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


set_tools_views_to_table()
set_tools_db_classes_to_table()


## to run ##
# 1 # python manage.py shell
# 2 # exec(open('utils/automate_db/main.py').read())
