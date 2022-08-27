from toolsframe.models import ToolDatabaseClass
from utils.automate_db.constants import TOOLS_DB_CLASSES_NAMES


def set_tools_db_classes_to_table():
  print('## set tool_db_classes ##')
  for name in TOOLS_DB_CLASSES_NAMES:
    print(name)
    if not ToolDatabaseClass.objects.filter(name=name).first():
      ToolDatabaseClass.objects.create(name=name)


set_tools_db_classes_to_table()


## to run ##
# 1 # python manage.py shell
# 2 # exec(open('utils/automate_db/main.py').read())
