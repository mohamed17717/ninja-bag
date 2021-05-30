from toolsframe.models import Tool
import json

with open('toolsframe/endpoints-docs.json', 'r') as f:
  tools = json.loads(f.read())

for tool_id, tool_info in tools.items():
  print(tool_id)
  # flags
  skip = tool_info.get('skip')
  flush = tool_info.get('flush')

  tool = not skip and Tool.objects.filter(tool_id=tool_id).first()
  if not tool: continue

  endpoints = tool_info.get('endpoints', [])
  if flush: endpoints = []

  tool.endpoints = endpoints
  tool.save()


## to run ##
# 1 # python manage.py shell
# 2 # exec(open('set-endpoints-to-db.py').read())
