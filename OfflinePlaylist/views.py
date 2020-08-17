import os
from datetime import datetime
from urllib.parse import urlencode
from django.shortcuts import render, redirect
from googleapiclient.discovery import build
from pytube import YouTube
import requests
from OfflinePlaylist.models import Track, Album, Artist, Playlists, Song, Category, DownloadedSongs

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MEDIA_DIR = os.path.join(BASE_DIR,'media')

flags = [False, False, False]
restart = [False]

API_ENDPOINT = "https://accounts.spotify.com/api/token"

client_data = {'scope':'user-library-read playlist-read-private playlist-modify-private playlist-modify-public playlist-read-collaborative',
               'client_id':'2e872b10213743bfb2e15254bbfd36f7', 
               'client_secret':'409874318f474150a77c015c565e3747', 
               'grant_type':'client_credentials' }
r = requests.post(url = API_ENDPOINT, data = client_data) 
headers = {
    "Authorization": f"Bearer {r.json()['access_token']}"
}

def test(request):
    
    playlist = Playlists.objects.all()
    songs = Song.objects.all()

    return render(request, 'test.html', context={'playlists':playlist,
                                                 'songs':songs})

def get_playlist(request):

    playlist_list = list()
    song_list = list
    if request.method == "POST":
        if "GetUserId" in request.POST:
            user_id = request.POST.get('UserId')
            endpoint = "https://api.spotify.com/v1/users"
            data = urlencode({"limit":50})
            lookup_url = f"{endpoint+'/'+user_id+'/'+'playlists'}?{data}"
            search = requests.get(lookup_url, headers=headers).json()
            for item in search['items']:
                playlist_list.append({'name':item['name'],'id':item['id']})

        if "GetCurrent" in request.POST:
            endpoint = "https://api.spotify.com/v1/users/21dmvu3cxeudjedn7ry3vn3da/playlists"
            data = urlencode({"limit":50})
            lookup_url = f"{endpoint}?{data}"
            search = requests.get(lookup_url, headers=headers).json()
            playlist_list = list()
            for item in search['items']:
                playlist_list.append({'name':item['name'],'id':item['id']})
        
        if "ViewPlaylist" in request.POST:
            playlist_id = request.POST.get('ViewPlaylist')
            endpoint = "https://api.spotify.com/v1/playlists"
            data = urlencode({"playlist_id":playlist_id,"limit":50})
            lookup_url = f"{endpoint+'/'+playlist_id+'/'+'tracks'}?{data}"
            search = requests.get(lookup_url, headers=headers).json()
            song_list = list()
            for item in search['items']:
                song_list.append({'id':item['track']['id'],'name':item['track']['name'],'artist':item['track']['artists'][0]['name'],'album':item['track']['album']['name']})
            
        if "AddPlaylist" in request.POST:
            playlist_name = request.POST.get("PlaylistName")
            track_ids = request.POST.getlist('cehckedTracks')
            if playlist_name is not None:
                if not Playlists.objects.filter(name=playlist_name).exists():
                    Playlists.objects.create(name=playlist_name, created=datetime.now())
            playlist_item = Playlists.objects.get(name=playlist_name)
            for song in song_list:
                if(song['id'] in track_ids):
                    song_item = Song.objects.filter(track_name=song['name']).filter(playlist__id=playlist_item.id)
                    if song_item.exists():
                        continue
                    Song.objects.create(track_name=song['name'], 
                                        artist_name=song['artist'],
                                        album_name=song['album'],
                                        playlist=playlist_item)

    return render(request, 'GetPlaylists.html', context={'playlists':playlist_list, 'songs':song_list})

def playlists(request):

    api_key = 'AIzaSyCrFKxRUCg3-IVk8XX-NN4cQwTfxsZz_j8'
    youtube = build('youtube','v3',developerKey=api_key)

    playlist = Playlists.objects.all()
    song_list = ''
    youtube = build('youtube','v3',developerKey=api_key)
    
    playlist_name = Playlists.objects.first().name
    if request.method == "POST":
     
        if "ViewPlaylist" in request.POST:
            playlist_name = request.POST.get('ViewPlaylist')
            song_list = Playlists.objects.get(name=playlist_name).song_set.all()

        if "deleteSong" in request.POST:
            song_id = request.POST.get('deleteSong')
            song_item = Song.objects.get(id=song_id)
            playlist_name = song_item.playlist.name
            Song.objects.get(id=song_id).delete()
            song_list = Playlists.objects.get(name=playlist_name).song_set.all()

        if "downloadSong" in request.POST:
            song_id = request.POST.get('downloadSong')
            song_item = Song.objects.get(id=song_id)
            ds = DownloadedSongs.objects.all()
            song_item.downloaded = True
            playlist_name = song_item.playlist.name
            song_list = Playlists.objects.get(name=playlist_name).song_set.all()
            if not ds.filter(song_name=song_item.track_name).filter(artist_name=song_item.artist_name).exists():
                DownloadedSongs.objects.create(song_name=song_item.track_name, artist_name=song_item.artist_name)
                search_query = song_item.track_name+'|'+song_item.artist_name
                youtube = build('youtube','v3',developerKey=api_key)
                # pylint: disable=maybe-no-member
                video_item = youtube.search().list(q=search_query,part='snippet',type='video',maxResults=1).execute()
                video_link = 'https://www.youtube.com/watch?v='+video_item['items'][0]['id']['videoId']
                stream_item = YouTube(video_link).streams.get_audio_only()
                abs_path = MEDIA_DIR + '\\downloaded_songs\\'
                stream_item.download(abs_path)

    return render(request, 'playlists.html', context={'playlists':playlist,
                                                      'songs':song_list,
                                                      'playlistName':playlist_name })

def index(request):

    endpoint = "https://api.spotify.com/v1/search"
    playlist = Playlists.objects.all()
    songs = Song.objects.all()
    track_list = Track.objects.all()
    artist_list = Artist.objects.all()
    album_list = Album.objects.all()
    if Category.objects.count() > 0:
        category = Category.objects.first()
    else:
        Category.objects.create(name='Track')
        category = Category.objects.first()

    if request.method == "POST":
        if 'selectCategory' in request.POST:
            category = request.POST.get('categoryOption')
            if category == "Track":
                restart[0] = True
                flags[0] = False
                flags[1] = False
                category = Category.objects.first()
                category.name = 'Track'
                category.save()             
                track_name = request.POST.get('Input')
                data = urlencode({"q":track_name, "type": "track"})
                lookup_url = f"{endpoint}?{data}"
                search = requests.get(lookup_url, headers=headers).json()
                track_list.delete()
                for item in search['tracks']['items']:
                    track_item = Track(id=item['id'], name=item['name'], album=item['album']['name'], artist=item['artists'][0]['name'])
                    track_item.save()
                return redirect('/')
            
            elif category == 'Artist':
                restart[0] = True
                flags[0] = False
                flags[1] = False
                category = Category.objects.first()
                category.name = 'Artist'
                category.save()
                artist_name = request.POST.get('Input')
                data = urlencode({"q":artist_name, "type": "artist", "limit":5})
                lookup_url = f"{endpoint}?{data}"
                search = requests.get(lookup_url, headers=headers).json()
                artist_list.delete()
                for item in search['artists']['items']:
                    artist_item = Artist(name=item['name'], id=item['id'])
                    artist_item.save()
                return redirect('/')

            else:
                restart[0] = True
                category = Category.objects.first()
                flags[0] = True
                flags[1] = False
                category.name = 'Album'
                category.save()
                album_name = request.POST.get('Input')
                data = urlencode({"q":album_name, "type": "album", "limit":10})
                lookup_url = f"{endpoint}?{data}"
                search = requests.get(lookup_url, headers=headers).json()
                album_list.delete()
                for item in search['albums']['items']:
                    album_item = Album(name=item['name'], id=item['id'], artist=item['artists'][0]['name'])
                    album_item.save()
                return redirect('/')

        elif 'getAlbums' in request.POST:
            flags[0] =  True 
            flags[1] =  False 
            endpoint = "https://api.spotify.com/v1/artists"
            artist_id = request.POST['checkedArtist']

            if artist_id is None:
                return redirect('/')

            artist = Artist.objects.get(id=artist_id)
            data = urlencode({"id":artist.id, 'include_groups':'album,single,appears_on,compilation', "limit":50})
            lookup_url = f"{endpoint+'/'+artist.id+'/'+'albums'}?{data}"
            search = requests.get(lookup_url, headers=headers).json()
            album_list.delete()
            artist_name = search['items'][0]['artists'][0]['name']
            for item in search['items']:
                album_item = Album(name=item['name'], id=item['id'], artist=artist_name)
                album_item.save()

            return redirect('/')
            
        elif 'getTracks' in request.POST:
            flags[0] =  False
            flags[1] =  True
            endpoint = "https://api.spotify.com/v1/albums"
            album_ids = request.POST.getlist('checkedAlbums')

            if len(album_ids) == 0:
                return redirect('/')

            for album_id in album_ids:
                album = Album.objects.get(id=album_id)
                data = urlencode({"id":album_id, "limit":50})
                lookup_url = f"{endpoint+'/'+album_id+'/'+'tracks'}?{data}"
                search = requests.get(lookup_url, headers=headers).json()
                track_list.delete()
                for item in search['items']:
                    track_item = Track(id=item['id'], name=item['name'], artist=item['artists'][0]['name'], album=album.name)
                    track_item.save()
                
            for album in album_list:
                if album.id not in album_ids:
                    album_list.get(id=album.id).delete()
            
            return redirect('/')

        elif 'AddSong' in request.POST:

            if not Playlists.objects.filter(name='Randoms').exists():
                Playlists.objects.create(name='Randoms', created=datetime.now())
            track_ids = request.POST.getlist('checkedTracks')
            playlist_list = request.POST.getlist('checkedPlaylists')
            new_playlist = request.POST.get('NewPlaylist')

            
            if new_playlist is not None:
                if not Playlists.objects.filter(name=new_playlist).exists():
                    Playlists.objects.create(name=new_playlist, created=datetime.now())
                if len(playlist_list) > 0:
                    playlist_list.append(new_playlist)
                else:
                    playlist_list = [new_playlist]


            if len(playlist_list) == 0:
                return redirect('/')

            for track_id in track_ids:
                track_item = Track.objects.get(id=track_id)

                for playlist in playlist_list:
                    playlist_item = Playlists.objects.get(name=playlist)
                    song_item = Song.objects.filter(track_name=track_item.name).filter(playlist__id=playlist_item.id)

                    if song_item.exists():
                        continue
                    Song.objects.create(track_name=track_item.name, 
                                        artist_name=track_item.artist,
                                        album_name=track_item.album,
                                        playlist=playlist_item)

            restart[0] = True
            
            return redirect('/')
     
    return render(request, 'index.html', context={'tracks':track_list,
                                                  'artists':artist_list,
                                                  'albums':album_list,
                                                  'category':category,
                                                  'flags':flags,
                                                  'playlists':playlist,
                                                  'songs':songs,
                                                  'restart':restart})
