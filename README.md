# Offline Music Playlist

Steps to start the app locally:

1. Clone the repo:

`https://github.com/sandipan-basak/Offline_Music_Palyer.git`

2. Create a virtual environment and activate it: 

`python -m virtualenv musicland`

3. Download all required packages for the app to run

`pip install -r requiement.txt`

4. Make all the database migrations necessary for the app to properly initailize:

`python manage.py makemigrations`
`python manage.py migrate`

5. Create the 3 categories 'Album', 'Track', 'Artist'

`python manage.py add_category`

6. Run the webserver:

`python manage.py runserver`

Download and enjoy the songs locally..!!

