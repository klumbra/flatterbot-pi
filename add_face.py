import boto3
import pprint
import os
import glob

DIR = '/media/sf_vm_share/flatterbot'

image_paths = [file for file in glob.glob(os.path.join(DIR, '*.jpg'))]
image_paths.sort(key=os.path.getmtime)
latest_image_path = image_paths[-1]
image = {}
image['Bytes'] = open(latest_image_path).read()

face_name = sys.argv[2]
client = boto3.client('rekognition')
res = client.index_faces(CollectionId='flatterees', ExternalImageId=face_name, Image=image)
pprint.pprint(res)
