import time
import os
import glob
import boto3
import subprocess

BASE_DIR = '/media/sf_vm_share/flatterbot'
MP3_DIR = 'mp3'

def process_snapshot():
    image_paths = [file for file in glob.glob(os.path.join(BASE_DIR, '*.jpg'))]
    image_paths.sort(key=os.path.getmtime)
    latest_image_path = image_paths[-1]

    image = {}
    image['Bytes'] = open(latest_image_path).read()

    try:
        name = return_face_name(image)
        phrase = 'Hey %s, looking nice today!' % (name)
        subjects = name
        print phrase
    except:
        print 'Is someone there? Do I know you?'
    say_name(subjects, phrase)

def return_face_name(image):
    client = boto3.client('rekognition')
    res = client.search_faces_by_image(
            CollectionId='flatterees',
            MaxFaces=1,
            FaceMatchThreshold=.7,
            Image=image
            )
    name = res['FaceMatches'][0]['Face']['ExternalImageId']
    return name

def say_name(subjects, phrase):
    subject_mp3 = '%s.mp3' % subjects
    mp3s = [f for f in os.listdir(MP3_DIR) if os.path.isfile(os.path.join(MP3_DIR, f))]
    subject_mp3_path = os.path.join(MP3_DIR, subject_mp3)
    if subject_mp3 not in mp3s:
        client = boto3.client('polly')
        res = client.synthesize_speech(OutputFormat='mp3', Text=phrase, VoiceId='Joanna')

        f = open(subject_mp3_path, 'wb')
        f.write(res['AudioStream'].read())
        f.close()
    subprocess.Popen("mpg123 -q %s" % subject_mp3_path, shell=True)

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

