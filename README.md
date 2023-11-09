# FlaskApp_CyMovies
# For this project, I have decided to create a flask web application that would be seen as a social media site for users to find movie recommendations, create movie list, and share / discuss movies and list with other users. This site will have 5 main processes: recommend, search, login, register, discuss. When first accessing the site, the user will have the option to register for an account or to use the site as a guest. Guest users will have the ability to search for all available movies on our site & movie recommendations from our database by genre, rating, and release year. If the user would like to create a movie list, share their list, or discuss with other users, they will be required to register for an account. When registering for an account, the user will be prompted to create a username and a password for the newly created account (passwords will also be hashed “****” using the passlib.hash library and the sha256_crypt function). After creation of account, they will be required to login using the credentials they just created. They will then have full access to our site’s capabilities. Our site will profit through paid advertisements including banners and movie promotion.![image](https://github.com/jackbenshoof/FlaskApp_CyMovies/assets/121009793/0d873296-d3d1-4def-9770-3b24786d391f)


#Required Libraries – [flask, flask_sqlalchemy, flask_migrate, flask_login, pandas, re, passlib.hash, sqlite3]!

#Required Data: imdb_top_1000.csv – Free Kaggle database. Shows top 1000 IMDB movies by ratings
[https://www.kaggle.com/datasets/harshitshankhdhar/imdb-dataset-of-top-1000-movies-and-tv-shows/data]
![image](https://github.com/jackbenshoof/FlaskApp_CyMovies/assets/121009793/ab953976-1ec7-45ac-8e00-813e7a9c6dcd)

# To run this application, first ensure that all libraries are installed shown above. 

##Within your terminal, locate the directory in which you have stored the required files, and use the following command
# - python app.py runserver
##Or
# - python3 app.py runserver

# Within your terminal, you will then be given an address you can insert into any given browser ( http://127.0.0.1:5000/ )

# *NOTE that there are still errors, so functionality may not be available during development. As of November 2nd, this site is functional
