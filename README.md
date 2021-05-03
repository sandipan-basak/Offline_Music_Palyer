# Offline Music Playlist

Start the app locally

Steps below:

Clone the repo:
`https://github.com/sandipan-basak/Offline_Music_Palyer.git`

Create a virtual environment and activate it: 
`python -m virtualenv musicland`

Make all the database migrations necessary for the app to properly initailize:
`python manage.py makemigrations`
`python manage.py migrate`

Create the 3 categories 'Album', 'Track', 'Artist'
`python manage.py add_category`

Run the webserver:
`python manage.py runserver`

Download and enjoy the songs locally..!!

