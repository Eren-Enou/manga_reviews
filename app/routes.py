from app import app, db
from flask import Response, render_template, redirect, request, url_for, flash, Markup
# from fake_data import posts
from app.forms import SignUpForm, LoginForm, PostForm, SearchForm
from app.models import User, Post
from flask_login import login_user, logout_user, login_required, current_user

import requests
url = "https://anilist-graphql.p.rapidapi.com/"

headers = {
    "X-RapidAPI-Key": "87927f4031msh473a290f717da11p189432jsn9b635492ee37",
    "X-RapidAPI-Host": "anilist-graphql.p.rapidapi.com"
}

@app.route('/', methods=["GET", "POST"])
def index():
    form = SearchForm()
    if form.validate_on_submit():
        search_term = form.search_term.data
        # posts = Post.query.filter(Post.title.ilike(f"%{search_term}%")).all()
        # posts = db.session.execute(db.select(Post).where((Post.title.ilike(f"%{search_term}%")) | (Post.body.ilike(f"%{search_term}%")))).scalars().all()
    return render_template('index.html', form=form)


@app.route('/signup', methods=["GET", "POST"])
def signup():
    # Create an instance of the form (in the context of the current request)
    form = SignUpForm()
    # Check if the form was submitted and that all of the fields are valid
    if form.validate_on_submit():
        # If so, get the data from the form fields
        print('Hooray our form was validated!!')
        first_name = form.first_name.data
        last_name = form.last_name.data
        email = form.email.data
        username = form.username.data
        password = form.password.data
        print(first_name, last_name, email, username, password)
        # Check to see if there is already a user with either username or email
        check_user = db.session.execute(db.select(User).filter((User.username == username) | (User.email == email))).scalars().all()
        if check_user:
            # Flash a message saying that user with email/username already exists
            flash("A user with that username and/or email already exists", "warning")
            return redirect(url_for('signup'))
        # If check_user is empty, create a new record in the user table
        new_user = User(first_name=first_name, last_name=last_name, email=email, username=username, password=password)
        flash(f"Thank you {new_user.username} for signing up!", "success")
        return redirect(url_for('index'))
    return render_template('signup.html', form=form)


@app.route('/login', methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        print('Form Validated :)')
        username = form.username.data
        password = form.password.data
        print(username, password)
        # Check if there is a user with username and that password
        user = User.query.filter_by(username=username).first()
        if user is not None and user.check_password(password):
            # If the user exists and has the correct password, log them in
            login_user(user)
            flash(f'You have successfully logged in as {username}', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid username and/or password. Please try again', 'danger')
            return redirect(url_for('login'))

    return render_template('login.html', form=form)


@app.route('/logout')
def logout():
    logout_user()
    flash("You have logged out", "info")
    return redirect(url_for('index'))

@app.route("/search")
def search():
    return render_template('search.html')

@app.route('/mangalist')
def mangalist():
    # Get the user input from the request object
    page = request.args.get('page', 1)
    per_page = request.args.get('per_page', 10)
    genre = request.args.get('genre', '')

    if (genre == ''):
        query = '''
        query ($page: Int, $perPage: Int) {
        Page (page: $page, perPage: $perPage) {
            media (type: MANGA) {
            id
            title {
                romaji
                english
            }
            genres
            tags {
              name
            }
            averageScore
            description
            coverImage {
                large
            }
            }
        }
        }
        '''
    elif (genre != ''):
        query = '''
        query ($page: Int, $perPage: Int, $genre: String) {
        Page (page: $page, perPage: $perPage) {
            media (type: MANGA, genre: $genre) {
            id
            title {
                romaji
                english
            }
            genres
            tags {
              name
            }
            averageScore
            description
            coverImage {
                large
            }
            }
        }
        }
        '''

    # Define the query as a multi-line string
    

    # Define our query variables and values that will be used in the query request
    variables = {
        'page': int(page),
        'perPage': int(per_page),
        'genre': genre
    }

    

    # Make the HTTP API request
    response = requests.post(url, headers=headers, json={'query': query, 'variables': variables})

    # If the response status code is not 200, raise an exception
    if response.status_code != 200:
        raise Exception('API response: {}'.format(response.status_code))

    # Get the JSON response from the API
    data = response.json()

    # Extract media results from response
    media = data['data']['Page']['media']

    # Convert HTML strings to escaped Markup objects
    for m in media:
        m['description'] = Markup(m['description'])

    # Render reviews template with media data
    return render_template('mangalist.html', media=media)

@app.route('/mangapage', methods=["GET"])
def reviews():

    media_id = request.args.get('media_id')

    query = '''
        query ($review_id:Int, $media_id:Int, $user_id:Int) {
            Review(id:$review_id,mediaId:$media_id,userId:$user_id,mediaType:MANGA){
    			id
  				user{
                    name
                    avatar{
                        large
                    }
                }
    			mediaId
    			summary
    			score
    			body
            }
        }
    '''

    variables = {
        'media_id': media_id
    }

    response = requests.post(url, headers=headers, json={'query': query, 'variables': variables})
    
    data = response.json()
    # Extract media and reviews from response
    review = data['data']['Review']
    
    return render_template('mangapage.html', review=review)

@app.route('/test', methods=["GET"])
def test():


    media_id = request.args.get('media_id')

    query = '''
    query ($media_id:Int) {
    Page {
        media (id: $media_id, type: MANGA) {
        id
        title {
            romaji
            english
        }
        genres
        tags {
            name
        }
        averageScore
        description
        coverImage {
            large
        }
        reviews {
            id
            summary
            score
            user {
            name
            avatar {
                large
            }
            }
        }
        }
    }
    }
    '''

    variables = {
        'media_id': media_id
    }



    response = requests.post(url, headers=headers, json={'query': query, 'variables': variables})
    
    # If the response status code is not 200, raise an exception
    if response.status_code != 200:
        raise Exception('API response: {}'.format(response.status_code))
    
    data = response.json()
    media = data['data']['Page']['media']
    reviews = media['reviews']
    return render_template('test.html', media=media)