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
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', default=10, type=int)
    genre = request.args.get('genre',default='',type=str)
    search_type = request.args.get('search_type',type=str)

    if (genre == ''):
        query = '''
        query ($page: Int, $perPage: Int, $sort:[MediaSort]) {
        Page (page: $page, perPage: $perPage) {
            media (type: MANGA, sort:$sort) {
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
            description(asHtml: true)
            coverImage {
                large
            }
            }
        }
        }
        '''
    elif (genre != ''):
        query = '''
        query ($page: Int, $perPage: Int, $genre: String, $sort:[MediaSort]) {
        Page (page: $page, perPage: $perPage) {
            media (type: MANGA, genre: $genre, sort:$sort) {
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
            description(asHtml: true)
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
        'genre': genre,
        'sort': [search_type]
    }

    

    # Make the HTTP API request
    response = requests.post(url, headers=headers, json={'query': query, 'variables': variables})

    # If the response status code is not 200, raise an exception
    if response.status_code != 200:
        raise Exception('API response: {}'.format(response.status_code))

    # Get the JSON response from the API
    data = response.json()

    # Extract media results from response
    page_data = data['data']['Page']
    media = data['data']['Page']['media']

    next_page = int(page) + 1

    # Convert HTML strings to escaped Markup objects
    for m in media:
        m['description'] = Markup(m['description'])

    # Render reviews template with media data
    return render_template('mangalist.html', media=media, page=page, per_page=per_page, genre=genre, next_page=next_page)

@app.route('/mangapage', methods=["GET"])
def mangapage():

    media_id = request.args.get('media_id')

    query = '''
        query ($media_id:Int) {
            Review(mediaId:$media_id,mediaType:MANGA){
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
    			body(asHtml:true)
            }
        }
    '''

    query2 = '''
        query ($media_id:Int) {
        Media(id:$media_id type: MANGA){
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
            description(asHtml: true)
            coverImage {
                large
            }
        }      
}
        '''
    
    query3 = '''
    query GetMediaRecommendations($mediaId: Int!, $sort: [RecommendationSort]) {
  Media(id: $mediaId) {
    recommendations(sort: $sort) {
      pageInfo {
        total
        perPage
        currentPage
        lastPage
      }
      edges {
        node {
          rating
          media {
            title {
              romaji
            }
            coverImage {
              large
            }
          }
          mediaRecommendation{
            id
            title{
              romaji
            }
            coverImage{
              large
            }
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
    variables2 = {
        'mediaId': media_id,
        "sort": "RATING_DESC"
    }
    response = requests.post(url, headers=headers, json={'query': query, 'variables': variables})
    response2 = requests.post(url, headers=headers, json={'query': query2, 'variables': variables})
    response3 = requests.post(url, headers=headers, json={'query': query3, 'variables': variables2})
    
    
    data = response.json()
    data2 = response2.json()
    data3 = response3.json()
    # Extract media and reviews from response
    review = data['data']['Review']
    media = data2['data']['Media']
    edges = data3['data']['Media']['recommendations']['edges']
    
    # Convert HTML strings to escaped Markup objects
    media['description'] = Markup(media['description'])
    
    return render_template('mangapage.html', review=review, media=media, edges=edges)

@app.route('/reviews', methods=["GET"])
def reviews():

    media_id = request.args.get('media_id')

    query = '''
        query ($media_id:Int) {
            Review(mediaId:$media_id,mediaType:MANGA){
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
    			body(asHtml:true)
            }
        }
    '''

    query2 = '''
        query ($media_id:Int) {
        Media(id:$media_id type: MANGA){
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
            description(asHtml: true)
            coverImage {
                large
            }
        }      
}
        '''
    query3 = '''
    query ($sort: [ReviewSort], $media_id:Int) {
  Page {
    reviews(sort: $sort, mediaId:$media_id) {
      id
      userId
      mediaId
      mediaType
      summary
      body(asHtml: true)
      rating
      ratingAmount
      userRating
      score
      private
      siteUrl
      createdAt
      updatedAt
      user {
        id
        name
      }
      media {
        id
        title {
          romaji
        }
      }
    }
  }
}
'''


    variables = {
        'media_id': media_id,
        
    }

    variables2 = {
        'media_id': media_id,
        'sort': ["RATING_DESC"]
    }



    response2 = requests.post(url, headers=headers, json={'query': query2, 'variables': variables})
    response3 = requests.post(url, headers=headers, json={'query': query3, 'variables': variables2})

    data2 = response2.json()
    data3 = response3.json()
    


    # Extract media and reviews from response

    media = data2['data']['Media']
    reviews = data3['data']['Page']['reviews']

    # Convert HTML strings to escaped Markup objects

    media['description'] = Markup(media['description'])
    for review in reviews:
        review['body'] = Markup(review['body'])
    

    return render_template('reviews.html', media=media, reviews=reviews)

@app.route('/create', methods=["GET","POST"])
def create():
    return render_template('create.html')

import requests

@app.route('/search_results')
def search_results():
    search_term = request.args.get('search')
    url = 'https://graphql.anilist.co'
    query = '''
        query ($search: String) {
            Media(search: $search, type: MANGA) {
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
                description(asHtml:true)
                coverImage {
                    large
                }
            }
        }
    '''
    variables = {'search': search_term}
    response = requests.post(url, json={'query': query, 'variables': variables})
    data = response.json()['data']['Media']
    return render_template('search_results.html', results=data)

