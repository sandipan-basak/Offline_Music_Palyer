import os
import difflib
from datetime import datetime
from urllib.parse import urlencode
from django.shortcuts import render, redirect, get_object_or_404
from googleapiclient.discovery import build
from pytube import YouTube
import requests

from django.views.generic import DetailView
from OfflinePlaylist.models import Track, Album, Artist, Playlists, Song, Category#, DownloadedSongs

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATIC_DIR = os.path.join(BASE_DIR,'static')

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

playlist_list = []

def test(request):
    
    playlist = Playlists.objects.all()
    songs = Song.objects.all()


    return render(request, 'test.html', context={'playlists':playlist,
                                                 'songs':songs})

def get_songs_from_playlist_id(playlist_id):
    endpoint = "https://api.spotify.com/v1/playlists"
    data = urlencode({"playlist_id":playlist_id,"limit":100})
    lookup_url = f"{endpoint+'/'+playlist_id+'/'+'tracks'}?{data}"
    search = requests.get(lookup_url, headers=headers).json()
    song_list = []
    while True:
        for item in search['items']:
            song_list.append({'id':item['track']['id'],'name':item['track']['name'],'artist':item['track']['artists'][0]['name'],'album':item['track']['album']['name']})
        if(search["next"] is None):
            break
        search = requests.get(search["next"], headers=headers)
        search = search.json()
    return song_list

def get_playlists_from_user_id(user_id):
    endpoint = "https://api.spotify.com/v1/users"
    data = urlencode({"limit":50})
    lookup_url = f"{endpoint+'/'+user_id+'/'+'playlists'}?{data}"
    search = requests.get(lookup_url, headers=headers).json()
    global playlist_list
    playlist_list.clear()
    while True:
        for item in search['items']:
            playlist_list.append({'name':item['name'],'id':item['id']})
        if(search["next"] is None):
            break
        search = requests.get(search["next"], headers=headers)
        search = search.json()
    return playlist_list

def get_playlist_name(playlist_id):
    endpoint = "https://api.spotify.com/v1/playlists/"+playlist_id
    data = urlencode({"playlist_id":playlist_id})
    lookup_url = f"{endpoint}?{data}"
    playlist_name = requests.get(lookup_url, headers=headers).json()['name']
    return playlist_name

def get_playlist(request):

    song_list = []
    global playlist_list
    playlist_item = ''
    if request.method == "POST":
        if "CurrentUser" in request.POST or "SelectUser" in request.POST:
            user_id = request.POST.get('UserId') if "SelectUser" in request.POST else "21dmvu3cxeudjedn7ry3vn3da"
            playlist_list = get_playlists_from_user_id(user_id)
            song_list = get_songs_from_playlist_id(playlist_list[0]['id'])
            playlist_item = {'id':playlist_list[0]['id'],'name':playlist_list[0]['name']}
        
        elif "ViewPlaylist" in request.POST or "SelectPlaylist" in request.POST:
            
            playlist_id = request.POST.get('ViewPlaylist') if "ViewPlaylist" in request.POST else request.POST.get('PlaylistId')
            song_list = get_songs_from_playlist_id(playlist_id)
            
            for playlist in playlist_list:
                if playlist['id'] == playlist_id:
                    playlist_item = {'id':playlist['id'],'name':playlist['name']}
                    # playlist_name = playlist['name']
                    break
            if "SelectPlaylist" in request.POST:
                playlist_list.clear()
                playlist_list.append({'id':playlist_id, 'name':get_playlist_name(playlist_id)})
                playlist_item = {'id':playlist_list[0]['id'],'name':playlist_list[0]['name']}

        elif "AddPlaylist" in request.POST:
            playlist_id = request.POST.get("ID")
            playlist_name = request.POST.get("PlaylistName")
            song_ids = request.POST.getlist('checkedSongs')
            # print("playlist_name: ", playlist_name)
            # print("playlist_id: ", playlist_id)
            if playlist_id is not None:
                if not Playlists.objects.filter(name=playlist_name).exists():
                    Playlists.objects.create(name=playlist_name, created=datetime.now())
            playlist_item = Playlists.objects.get(name=playlist_name)
            song_list = get_songs_from_playlist_id(playlist_id)
            # print("song_list", song_list)
            # print("song_ids", song_ids)
            # print("playlist_item", playlist_item)
            for song in song_list:
                if(song['id'] in song_ids):
                    song_item = Song.objects.filter(track_name=song['name']).filter(playlist__id=playlist_item.id)
                    if song_item.exists():
                        continue
                    Song.objects.create(track_name=song['name'], 
                                        artist_name=song['artist'],
                                        album_name=song['album'],
                                        playlist=playlist_item)

    return render(request, 'GetPlaylists.html', context={'playlists':playlist_list, 
                                                         'songs':song_list,
                                                         'playlistItem':playlist_item})

def playlists(request):

    api_key = 'AIzaSyB8yOuNdpcUpjV3ilOJbrdZtrey9BHNStA'
    youtube = build('youtube','v3',developerKey=api_key)

    playlist = Playlists.objects.all()
    song_list = ''
    youtube = build('youtube','v3',developerKey=api_key)

    
    playlist_name = Playlists.objects.first().name
    if request.method == "POST":
     
        if "ViewPlaylist" in request.POST:
            playlist_name = request.POST.get('ViewPlaylist')
            song_list = Playlists.objects.get(name=playlist_name).song_set.all()
            print(song_list)

        elif "deleteSong" in request.POST:
            song_id = request.POST.get('deleteSong')
            song_item = Song.objects.get(id=song_id)
            playlist_name = song_item.playlist.name
            Song.objects.get(id=song_id).delete()
            song_list = Playlists.objects.get(name=playlist_name).song_set.all()
            path = STATIC_DIR + '/downloaded_songs/'
            mp4 = path + song_item.video_file
            if Song.objects.filter(track_name=song_item.track_name).count() == 0:
                if  os.path.exists(mp4):
                    os.remove(mp4)
            print(os.path.exists(mp4)) 

        elif "downloadSong" in request.POST:
            song_id = request.POST.get('downloadSong')
            song_item = Song.objects.get(id=song_id)
            # ds = DownloadedSongs.objects.all()
            # song_item.downloaded = True
            song_item.save()
            playlist_name = song_item.playlist.name
            song_list = Playlists.objects.get(name=playlist_name).song_set.all()
            if not song_item.downloaded:
                # DownloadedSongs.objects.create(song_name=song_item.track_name, artist_name=song_item.artist_name)
                search_query = song_item.track_name+'|'+song_item.artist_name
                youtube = build('youtube','v3',developerKey=api_key)
                # pylint: disable=maybe-no-member
                video_item = youtube.search().list(q=search_query,part='snippet',type='video',maxResults=1).execute()
                video_link = 'https://www.youtube.com/watch?v='+video_item['items'][0]['id']['videoId']
                # print(video_item)
                abs_path = STATIC_DIR + '/downloaded_songs/'
                video_title = YouTube(video_link).title
                stream_item = YouTube(video_link).streams.get_audio_only()
                stream_item.download(abs_path)
                files = os.listdir(abs_path)
                file_present = difflib.get_close_matches(video_title+".mp4", files, 1)
                
                for song in Song.objects.filter(track_name=song_item.track_name):
                    song.video_file = file_present[0]
                    song.downloaded = True
                    song.save()

        elif "ViewS" in request.POST:
            song = request.POST.get('ViewS')
            return redirect('OfflinePlaylist:curr_song', song)

    return render(request, 'playlists.html', context={'playlists':playlist,
                                                      'songs':song_list,
                                                      'playlistName':playlist_name})

def index(request):
    # global playlist_list
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

def song_view(request, pk):
    
    song = get_object_or_404(Song, pk=pk)
    template_name = 'song_view.html'
    print(song.id)

    return render(request, template_name, {'song_link':'downloaded_songs/'+song.video_file})
