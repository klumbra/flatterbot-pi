import time
import os
import glob
import boto3
import subprocess
import pprint

BASE_DIR = '/media/sf_vm_share/flatterbot'

def process_snapshot():
    image_paths = [file for file in glob.glob(os.path.join(BASE_DIR, '*.jpg'))]
    image_paths.sort(key=os.path.getmtime)
    latest_image_path = image_paths[-1]

    image = {}
    image['Bytes'] = open(latest_image_path).read()

    client = boto3.client('rekognition')
    res = client.detect_labels(MinConfidence=.8, Image=image)
    pprint.pprint(res)

def main():
    before = dict ([(f, None) for f in os.listdir (BASE_DIR)])
    while 1:
      time.sleep (3)
      after = dict ([(f, None) for f in os.listdir (BASE_DIR)])
      added = [f for f in after if not f in before]
      if added:
          process_snapshot()
      before = after

if __name__ == '__main__':
    main()

