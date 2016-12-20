import time
import os
import glob
import boto3
import subprocess
import picamera
import sys
from select import select

BASE_DIR = '.'
MP3_DIR = 'mp3'


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

def return_object_name(image):
    client = boto3.client('rekognition')
    res = client.detect_labels(
            MinConfidence=.8,
            Image=image
            )
    labels = {d['Name']: d['Confidence'] for d in res['Labels']}
    with open('excluded_labels.txt', 'r') as f:
        excluded_labels = [line.rstrip('\n') for line in f]
    
    for k in excluded_labels:
        labels.pop(k, None)
    
    if labels:
        top_label = max(labels, key=labels.get)
        top_label = top_label.replace(' ', '')
    else:
        top_label = ''
    return top_label

def get_phrase(phrase_key, phrase):
    phrase = '<speak><break time="900ms" />' + phrase + '</speak>'
    needed_mp3 = '%s.mp3' % phrase_key
    existing_mp3s = [f for f in os.listdir(MP3_DIR) if os.path.isfile(os.path.join(MP3_DIR, f))]
    needed_mp3_path = os.path.join(MP3_DIR, needed_mp3)
    if needed_mp3 not in existing_mp3s:
        client = boto3.client('polly')
        res = client.synthesize_speech(OutputFormat='mp3', Text=phrase, VoiceId='Joanna', TextType='ssml')

        f = open(needed_mp3_path, 'wb')
        f.write(res['AudioStream'].read())
        f.close()

def play_phrase(phrase_key):
    needed_mp3 = '%s.mp3' % phrase_key
    needed_mp3_path = os.path.join(MP3_DIR, needed_mp3)
    subprocess.Popen("mpg123 -q %s" % needed_mp3_path, shell=True)

def say_and_annotate(phrase_key, phrase, camera):
    get_phrase(phrase_key, phrase) 
    camera.annotate_text = phrase.upper()
    play_phrase(phrase_key)
    time.sleep(2)
    camera.annotate_text = ''

def main():
    with picamera.PiCamera() as camera:
        camera.resolution = (640, 480)
        camera.framerate = 24
        camera.annotate_text_size = 80
        camera.start_preview()
        while True:
            raw_input('')
            image_path =  os.path.join(BASE_DIR, 'latest_capture.jpg')
            camera.capture(image_path)
            image = {}
            image['Bytes'] = open(image_path).read()

            worked = False
            try:
                name = return_face_name(image)
                object_name = return_object_name(image)
                worked = True
            except:
                worked = False

            if worked:
                phrase = "Hey %s" % (name)
                say_and_annotate(name, phrase, camera)
                say_and_annotate("LookingNice", "Looking nice today.", camera)

                if object_name != '':
                    object_phrase = ' Sweet %s!' % (object_name)
                    say_and_annotate(object_name, object_phrase, camera)
            else:
                say_and_annotate("Exception", "Do I know you?", camera)

if __name__ == '__main__':
    main()
