"""Server for movie ratings app."""

from flask import Flask
from flask import (Flask, render_template, request, flash, session,
                   redirect)
from model import connect_to_db, db
import crud
from jinja2 import StrictUndefined

app = Flask(__name__)
app.secret_key = "dev"
app.jinja_env.undefined = StrictUndefined

@app.route('/')
def homepage():
    return render_template('homepage.html')


@app.route('/movies')
def movies():
    movies = crud.return_movies()

    return render_template('all_movies.html', movies=movies)


@app.route('/movies/<movie_id>')
def movie_detail(movie_id):

    movie = crud.get_movie_by_id(movie_id)

    return render_template('movie_details.html', movie=movie)


@app.route('/users')
def users():
    users = crud.return_users()

    return render_template('all_users.html', users=users)


@app.route('/users/<user_id>')
def user_details(user_id):

    user = crud.get_user(user_id)

    return render_template('user_details.html', user=user)

@app.route('/users', methods = ['POST'])
def create_user():

    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

    does_email_exist = crud.get_user_by_email(request.form['email'])

    if does_email_exist == None:
        # user = crud.create_user(email, password)
        user = crud.create_user(email, password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created successfully, and you may now log in.')
    else:
        flash('An account cannot be created with that email. Please try again.')

    return redirect ('/')

@app.route("/login", methods=["POST"])
def login():
    email = request.form.get('email')
    password = request.form.get('password')
    user = crud.get_user_by_email(email)
        
    if user and user.password==password:
        session["user"] = user.user_id
        session["email"] = user.email
        flash(f'You are logged in! {session["user"]}')
    else:
        flash('Login unsuccessful. Please try again.')
    
    return redirect('/')

@app.route("/movies/<movie_id>/ratings", methods=["POST"])
def ratings(movie_id):
    logged_in_email = session.get('email')
    score = request.form.get('rating')

    if logged_in_email:
        
        movie = crud.get_movie_by_id(movie_id)
        user = crud.get_user_by_email(logged_in_email)

        rating = crud.create_rating(user, movie, score)
        db.session.add(rating)
        db.session.commit()

        flash('Your rating has been saved.')

    else:
        flash('You must be logged in to rate a movie.')

    return redirect(f"/movies/{movie_id}")
    

if __name__ == "__main__":
    connect_to_db(app)
    app.run(host="0.0.0.0", debug=True)
