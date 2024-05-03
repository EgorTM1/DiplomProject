import requests
import time
from progress.bar import IncrementalBar
from datetime import datetime
import json
import os

VK_ID = int(input('Укажите свой VK ID: '))
VK_TOKEN = input('Укажите свойVK TOKEN: ')
Yandex_TOKEN = input('Укажите свой Yandex TOKEN: ')

class VK:
  def __init__(self, id, token):
    self.id = id
    self.token = token

  def get_photos(self):
    base_url = 'https://api.vk.com/method/photos.get'
    params = {
      'access_token': self.token,
      'owner_id': self.id,
      'album_id': 'profile',
      'extended': 1,
      'v': 5.199,
      'feed_type': 'photo',
    }

    print('Загрузка фотографий...')

    global response

    response = requests.get(base_url, params=params)
    bar = IncrementalBar('Downloading...', max = response.json()['response']['count'])

    for i in range(response.json()['response']['count']):
        bar.next()
        time.sleep(0.3)

    bar.finish()
    time.sleep(0.2)
    print('Загрузка завершена!')

  def writeInFile(self):
    dictUrls = {}
    allUrls = {}
    listUrls = []

    if not os.path.exists('Images'):
      os.mkdir('Images')

    for number in range(response.json()['response']['count']):
      for width in response.json()['response']['items'][number]['sizes']:

        allUrls[width['width']] =  width['url']

      dictUrls[number] = allUrls
      allUrls = {}  

    for key, value in dictUrls.items():
      for i in value:
        if i == sorted(value.keys(), reverse=True)[0]:
          listUrls.append(value[i])
    
    for index, url in enumerate(listUrls):
      response2 = requests.get(url)

      likes = response.json()['response']['items'][index]['likes']['count']
      time = str(datetime.fromtimestamp(int(response.json()['response']['items'][index]['date']))).split(' ')
      time1 = time[0].replace('-', '_')
      time2 = time[1].replace(':', '_')

      with open(f'Images\{likes} likes {time1} {time2[:-3]}.jpg', 'wb') as file:
        file.write(response2.content)

      with open('result.json', 'a') as file:
        timeInJson = datetime.fromtimestamp(int(response.json()['response']['items'][index]['date']))
        data = [{
          'file_name': f'{timeInJson}.jpg',
          'likes': likes,
          'time': time
        }]
        json.dump(data, file)
        file.write('\n')


class YandexDisk:
  def __init__(self, token):
    self.token = token

  def post_photos(self):
    url = 'https://cloud-api.yandex.net/v1/disk/resources'
    headers = {'Authorization': f'OAuth {self.token}'}
   
    params = {'path': f'/Images', 'overwrite': 'true'}
    response = requests.put(url, headers=headers, params=params)

    print('Загрузка фотографий на Yandex...')
    bar = IncrementalBar('Downloading...', max = len(os.listdir('Images')))

    for file in os.listdir('Images'):
      file_path = os.path.join('Images', file)
      base_url = 'https://cloud-api.yandex.net/v1/disk/resources/upload'

      params = {
        'path': f'/Images/{file}',
        'overwrite': 'true',
      }

      bar.next()

      time.sleep(0.3)

      response2 = requests.get(base_url, headers=headers, params=params)
      href = response2.json()['href']

      requests.put(href, data=open(file_path, 'rb'), headers=headers)

    bar.finish()
    print('Загрузка завершена!')


vk = VK(VK_ID, VK_TOKEN)
vk.get_photos()
vk.writeInFile()

yandex = YandexDisk(Yandex_TOKEN)
yandex.post_photos()