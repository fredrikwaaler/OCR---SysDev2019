
"""from google.cloud import vision
from google.oauth2 import service_account

key = "3b6baaea984e1382d7528456c19633bbdd949e31"
credentials = service_account.Credentials.from_service_account_file("key.json")

scoped_credentials = credentials.with_scopes(['https://www.googleapis.com/auth/cloud-platform'])

client = vision.ImageAnnotatorClient(credentials=credentials)
response = client.annotate_image({"image": {"source": {"image_uri": 'https://i.stack.imgur.com/vrkIj.png'}}, "features":
    [{'type': vision.enums.Feature.Type.TEXT_DETECTION}]})

print(response)
"""

a = "12300"
b = list(a)
c = "".join(b[:len(b)-2]) + ".00"
print(c)