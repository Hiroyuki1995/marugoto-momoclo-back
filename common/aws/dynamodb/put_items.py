import boto3

def put_items(table_name, items, resource=None):
  if not resource:
    resource = boto3.resource('dynamodb')
  table = resource.Table(table_name)
  for item in items:
    dict = table.put_item(Item=item)
    print(dict)

if __name__ == '__main__':
    put_items()