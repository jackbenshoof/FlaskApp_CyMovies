# The purpose of this program is to run a task application that creates a site
# that users can search for movies, find movie recommendations through our filters,
# create an account, share and create movie list, discuss in our chat room

from flask import Flask, render_template, request, redirect, url_for, flash, current_app
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import pandas as pd
import re
from passlib.hash import sha256_crypt
app = Flask(__name__)
# movie data
data = pd.read_csv('imdb_top_1000.csv')

# flask configuration
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tester.db'

# Initialize SQLAlchemy
db = SQLAlchemy(app)
migrate = Migrate(app, db)
#------------------------------Classes----------------------------------------------
# User model for login
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    watched_movies = db.relationship('WatchedMovie', backref='user', lazy=True)

#Hold each user's own Watched Movies
class WatchedMovie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    movie_title = db.Column(db.String(255), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
#---------------------------------Login, Logout, & Register--------------------------------------------------------------
# Configure the LoginManager
login_manager = LoginManager(app)
login_manager.login_view = 'register'

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Retrieve the user from the database based on the username
        user = User.query.filter_by(username=username).first()

        if user and check_password(password, user.password):
            # Login the user
            login_user(user)

            # Redirect to a protected page (e.g., a user dashboard)
            return redirect(url_for('user_dashboard'))
        else:
            flash('Invalid username or password. Please try again.', 'error')

    return render_template('login.html')

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/user_dashboard')
@login_required
def user_dashboard():
   # return 'Welcome to the User Dashboard, ' + current_user.username + '!'
    return redirect(url_for('home'))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Password hashing, makes characters when entering password into "****"
def hash_password(password):
    return sha256_crypt.encrypt(password)

def check_password(entered_password, stored_password):
    return sha256_crypt.verify(entered_password, stored_password)

# Registration page route
# this allows users to register for an account if not logged in
# if username and password fits criteria, they will be added to db
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Check if the username is already in use
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            return 'Username already exists'

        new_user = User(username=username, password=hash_password(password))
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))

    return render_template('register.html')
#------------------------------------------------------------------------------------------------------------
#Pull the release year for our recommendations page
def extract_year(released_year):
    match = re.search(r'\d{4}', released_year)
    if match:
        return int(match.group())
    else:
       return 0  # Replace non-numeric values with 0

#Apply the extract_year function to the 'Released_Year' column
data['Released_Year'] = data['Released_Year'].apply(extract_year)

# Pulling all movies from imdb_top_1000.csv
available_movies = data['Series_Title'].tolist()
#Creating empty list for each user to store watched movies
watched_movies = []

# Home page
@app.route('/')
def home():
    return render_template('index.html', watched_movies=watched_movies)

# Recommendation page
# This will take the user's prefrence of movie and return
# movies best fitted for their chosen options from genre, min rating, and release year
@app.route('/recommendations', methods=['GET', 'POST'])
def recommendations():
    if request.method == 'POST':
        genre = request.form['genre']
        min_rating = float(request.form['min_rating'])
        release_year = int(request.form['release_year'])

        # Filter the dataset
        filtered_data = data[(data['Genre'].str.lower().str.contains(genre.lower())) &
                            (data['IMDB_Rating'] >= min_rating) &
                            (data['Released_Year'] >= release_year)]

        # Sort the filtered dataset by IMDb rating in descending order
        sorted_data = filtered_data.sort_values(by='IMDB_Rating', ascending=False)

        # Display the results
        if not sorted_data.empty:
            movies = []
            for index, row in sorted_data.iterrows():
                movies.append(f"{row['Series_Title']} ({row['Released_Year']}) - IMDb Rating: {row['IMDB_Rating']:.1f}")
            return render_template('recommendations.html', movies=movies)
        else:
            return render_template('recommendations.html', movies=['No movies match your preferences.'])

    # This part is for the initial load of the page or when a GET request is made
    return render_template('recommendations.html')

    # Display the results
    if not sorted_data.empty:
        movies = []
        for index, row in sorted_data.iterrows():
            movies.append(f"{row['Series_Title']} ({row['Released_Year']}) - IMDb Rating: {row['IMDB_Rating']:.1f}")
        return render_template('results.html', movies=movies)
    else:
        return render_template('results.html', movies=['No movies match your preferences.'])

@app.route('/recommend', methods=['POST'])
def recommend():
    genre = request.form['genre']
    min_rating = float(request.form['min_rating'])
    release_year = int(request.form['release_year'])

    # Filter the dataset
    filtered_data = data[(data['Genre'].str.lower().str.contains(genre.lower())) &
                         (data['IMDB_Rating'] >= min_rating) &
                         (data['Released_Year'] >= release_year)]

    # Sort the filtered dataset by IMDb rating in descending order
    sorted_data = filtered_data.sort_values(by='IMDB_Rating', ascending=False)

    # Display the results
    # If sorted data is not empty, display the results. If empty, show error
    if not sorted_data.empty:
        movies = []
        for index, row in sorted_data.iterrows():
            movies.append(f"{row['Series_Title']} ({row['Released_Year']}) - IMDb Rating: {row['IMDB_Rating']:.1f}")
        return render_template('results.html', movies=movies)
    else:
        return render_template('results.html', movies=['No movies match your preferences.'])

@app.route('/search', methods=['GET'])
def search_movies():
    search_query = request.args.get('search', '').strip()  # Get the search query from the URL

    # Filter the available movies based on the search query
    filtered_movies = [movie for movie in available_movies if search_query.lower() in movie['title'].lower()]

    return render_template('search_results.html', search_query=search_query, filtered_movies=filtered_movies)

# Add to Watched page
# this will allow users to store
# movies in their Watched Movies list if they are logged in
@app.route('/add_to_watched', methods=['POST'])
@login_required  # ensure that user is logged in
def add_to_watched():
    if request.method == 'POST':
        if current_user.is_authenticated:
            movie_title = request.form.get('movie')
            user_id = current_user.id

            # Used ChatGPT to help with this portion (line 209-222)
            with current_app.app_context():
                # Check if the movie is not already in the watched list for the current user
                if not WatchedMovie.query.filter_by(user_id=user_id, movie_title=movie_title).first():
                    new_watched_movie = WatchedMovie(movie_title=movie_title, user_id=user_id)
                    db.session.add(new_watched_movie)
                    db.session.commit()
                    # Remove the movie from the available list
                    if movie_title in available_movies:
                        available_movies.remove(movie_title)

            return redirect('/watched')
        else:
            flash('You must register for an account to add movies to "My Watched Movies."', 'warning')
            return redirect('/login')

# My Watched Movies page
@app.route('/watched')
@login_required
def watched():
    user_id = current_user.id
    watched_movies_query = WatchedMovie.query.filter_by(user_id=user_id)
    watched_movies = [movie.movie_title for movie in watched_movies_query]

    return render_template('watched.html', watched_movies=watched_movies)

# Remove from Watched page
# this will allow users to remove movies from their Watched Page
# with a remove button.
@app.route('/remove_watched', methods=['POST'])
def remove_watched():
    if current_user.is_authenticated:
        movie_to_remove = request.form['movie']
        user_id = current_user.id

        # Check if the movie is in the user's watched list
        watched_movie = WatchedMovie.query.filter_by(user_id=user_id, movie_title=movie_to_remove).first()

        if watched_movie:
            db.session.delete(watched_movie)
            db.session.commit()

            # Remove the movie from the watched_movies list
            if movie_to_remove in watched_movies:
                watched_movies.remove(movie_to_remove)

    return redirect('/watched')

# Route for displaying available movies
@app.route('/available_movies')
def display_available_movies():
    available_movie_details = []

    for movie_title in available_movies:
        # Find the movie details based on the title
        movie = data[data['Series_Title'] == movie_title].iloc[0]
        movie_details = {
            'title': movie['Series_Title'],
            'rating': movie['IMDB_Rating'],
            'genre': movie['Genre'],
            'runtime': movie['Runtime']
        }
        available_movie_details.append(movie_details)

    return render_template('available_movies.html', available_movies=available_movie_details)


# Route for Returning Movies to "Available Movies"
@app.route('/return_movie', methods=['POST'])
def return_movie():
    movie_to_return = request.form['movie']
    if movie_to_return in watched_movies:
        watched_movies.remove(movie_to_return)
        available_movies.append(movie_to_return)
    return redirect('/watched')

# Function to create database tables
def create_database_tables():
    with app.app_context():
        db.create_all()

if __name__ == '__main__':
    create_database_tables()
    app.run(debug=True)
