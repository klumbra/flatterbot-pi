import time
import os
import glob
import boto3

DIR = '/media/sf_vm_share/flatterbot'

def process_snapshot():
    image_paths = [file for file in glob.glob(os.path.join(DIR, '*.jpg'))]
    image_paths.sort(key=os.path.getmtime)
    latest_image_path = image_paths[-1]

    image = {}
    image['Bytes'] = open(latest_image_path).read()

    client = boto3.client('rekognition')
    try:
        res = client.search_faces_by_image(CollectionId='flatterees', MaxFaces=1, FaceMatchThreshold=.7, Image=image)
        flatteree = res['FaceMatches'][0]['Face']['ExternalImageId']
        print 'Hey %s, looking nice today!' % (flatteree)
        #say_name(flatteree)
    except:
        print 'Is someone there? Do I know you?'

def say_name(name):
    client = boto3.client('polly')
    res = client.synthesize_speech(OutputFormat='pcm', Text=name, VoiceId='Mads')

def main():
    before = dict ([(f, None) for f in os.listdir (DIR)])
    while 1:
      time.sleep (3)
      after = dict ([(f, None) for f in os.listdir (DIR)])
      added = [f for f in after if not f in before]
      if added:
          process_snapshot()
      before = after

if __name__ == '__main__':
    main()

