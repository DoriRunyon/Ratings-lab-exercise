"""Movie Ratings."""

from jinja2 import StrictUndefined

from flask import Flask, render_template, redirect, request, flash, session, url_for
from flask_debugtoolbar import DebugToolbarExtension

from model import connect_to_db, db, User, Rating, Movie


app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "ABC"

# Normally, if you use an undefined variable in Jinja2, it fails silently.
# This is horrible. Fix this so that, instead, it raises an error.
app.jinja_env.undefined = StrictUndefined


@app.route('/')
def index():
    """Homepage."""

    if 'user' in session:
        print session['user'], "LOOK HERE"
     


    return render_template("homepage.html")

@app.route('/sign-in-form')
def sign_in_form():
    """Shows the user a form to put in info."""

    return render_template("sign_in.html")

@app.route('/sign-up', methods=["POST"])
def sign_in():
    """Have the user signed in."""
    
    email = request.form.get("email")
    print email
    password = request.form.get("password")
    print password

    user = User.query.filter(User.email == email).first()

    if user == None: 
        user = User(email=email, password=password)
        db.session.add(user)
        db.session.commit()


    return redirect('/login')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/logged-in', methods=["POST"])
def logged_in():
    """Users with an account can login."""

    email = request.form.get("email")
    password = request.form.get("password")


    user = User.query.filter(User.email == email).first()
    

    if user.password == password:
        user_id = user.user_id
        session['user'] = user_id
        flash(("Hello %s, you are now logged in.") % email)
        return redirect(('/users/%d') %user_id) 

    else: 
        return "Incorrect password. <a href='/login'>Try again.</a>"    

@app.route('/log-out')
def logout():

    del session['user']
    flash("Goodbye, you are now logged out.")
    return redirect('/')


@app.route('/users')
def user_list():
    """Show list of users."""

    users = User.query.all()
    return render_template("user_list.html", users=users)

@app.route('/movies')
def movie_list():
    """Show list of movies."""

    #movies = Movie.query.all().order_by(title)
    #movies = Movie.query.all().order_by(title)
    movies = db.session.query(Movie).order_by(Movie.title).all()
    return render_template("movie_list.html", movies=movies)

@app.route('/users/<int:user_id>')    
def user_page(user_id): 
    """Show details for individual user."""

    user = User.query.get(user_id)
    age = user.age
    zipcode = user.zipcode
    ratings = user.ratings

    movie_titles = []
    scores = []
    for rating in ratings: 
        movie_title = Movie.query.get(rating.movie_id).title
        movie_titles.append(movie_title)
        movie_rating = rating.score
        scores.append(movie_rating)

    movie_scores = zip(movie_titles, scores)


    return render_template("user_details.html", 
                            age=age, 
                            zipcode=zipcode,
                            ratings=ratings,
                            movie_scores=movie_scores)


@app.route('/movies/<int:movie_id>')    
def movie_details(movie_id): 
    """Show details for individual movie."""

    movie = Movie.query.get(movie_id)
    title = movie.title
    released_at = movie.released_at
    imdb_url = movie.imdb_url
    ratings = movie.ratings

    scores = []
    for rating in ratings:
        score = rating.score 
        scores.append(score)



    return render_template("movie_details.html", 
                            title=title,
                            released_at=released_at,
                            imdb_url=imdb_url, 
                            scores=scores) 

@app.route('/new_rating', methods=['POST'])
def make_new_rating():

    # title = request.form.get("title")
    score = int(request.form.get("rating"))
    title = request.form.get("title")
    #print score
    #print title 

    movie = Movie.query.filter(Movie.title == title).first()
    #print movie
    movie_id = movie.movie_id
    user_id = session['user']

    rating = Rating.query.filter((Rating.user_id == user_id) & (Rating.movie_id == movie_id)).first()
    #print rating 

    if rating != None:
        rating.score = score
    else:
        new_rating = Rating(user_id=user_id, 
                            movie_id=movie_id, 
                            score=score)

        db.session.add(new_rating)
        
    db.session.commit()

    
    return "SUCCESS! You gave %s a rating of %s." % (title, score)
                            

if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the point
    # that we invoke the DebugToolbarExtension
    app.debug = True

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run()
