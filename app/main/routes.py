# python packages
from datetime import datetime
# extensions
from flask import render_template, flash, redirect, url_for, request, current_app, g
from flask_login import current_user, login_required
from werkzeug.urls import url_parse
# local modules
from app import db
from app.models import User, Post
from app.main import bp
from app.main.forms import EditProfileForm, PostForm, SearchForm

@bp.before_app_request
def before_request():
    """
    Executes before every request:
        - Updates user's last seen time to time of request.
        - Stores search form in g. g is a Flask variable that can store data during duration of a request; exposed to templates (don't need to pass in as arg to each render_template() call in each view function).
            - Problem solved: The search form should appear on every page visited by an authenticated user but it would be inefficient to, in every route, create a form object and pass it to the template. So, instead, the solution is to implement the search form in this before_request handler which exposes the search form to g and then have the base.html use g to render the search form.

        Side-effects
            Updates user's last seen time to time of request.
            Stores search form in g, enabling the base.html template to render the search form on every page.

        Returns
            None
    """
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()
        g.search_form = SearchForm()

@bp.route('/', methods=['GET', 'POST'])
@bp.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    # login form
    form = PostForm()
    if form.validate_on_submit():
        post = Post(body=form.post.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Your post is now live!')
        return redirect(url_for('main.index'))
    
    # posts and pagination
    page = request.args.get('page', 1, type=int)
    feed_posts = current_user.feed_posts(). \
        paginate(page, current_app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('main.index',
        page=feed_posts.next_num if feed_posts.has_next else None)
    prev_url = url_for('main.index',
        page=feed_posts.prev_num if feed_posts.has_prev else None)
    
    response_html = render_template('index.html', title='Home', form=form,
        posts=feed_posts.items, next_url=next_url, prev_url=prev_url)
    return response_html
        

@bp.route('/explore')
@login_required
def explore():
    # posts and pagination
    page = request.args.get('page', 1, type=int)
    feed_posts = Post.query.order_by(Post.timestamp.desc()). \
        paginate(page, current_app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('main.explore',
        page=feed_posts.next_num if feed_posts.has_next else None)
    prev_url = url_for('main.explore',
        page=feed_posts.prev_num if feed_posts.has_prev else None)
    
    response_html = render_template('index.html', 
        title='Explore', posts=feed_posts.items, next_url=next_url, prev_url=prev_url)
    return response_html


@bp.route('/user/<username>')
@login_required
def user(username):
    """
    Returns the user's profile page if the user exists in the db (else returns 404 page).
    """
    user = User.query.filter_by(username=username).first_or_404()
    
    # posts and pagination
    page = request.args.get('page', 1, type=int)
    feed_posts = user.posts.order_by(Post.timestamp.desc()). \
        paginate(page, current_app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('main.user', username=username, 
        page=feed_posts.next_num if feed_posts.has_next else None)
    prev_url = url_for('main.user', username=username, 
        page=feed_posts.prev_num if feed_posts.has_prev else None)
    
    response_html = render_template('user.html', user=user,
        posts=feed_posts.items, next_url=next_url, prev_url=prev_url)
    return response_html


@bp.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Your changes have been saved!')
        return redirect(url_for('main.edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    
    response_html = render_template('edit_profile.html', title='Edit Profile',
        form=form)
    return response_html


# route for follow
@bp.route('/follow/<username>')
@login_required
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash(f'User {username} not found.')
        return redirect(url_for('main.user', username=username))
    if user == current_user:
        flash(f"You can't follow yourself!")
        return redirect(url_for('user', username=username))
    current_user.follow(user)
    db.session.commit()
    flash(f"You're following {username}!")
    
    response_html = redirect(url_for('main.user', username=username))
    return response_html
    

# route for unfollow
@bp.route('/unfollow/<username>')
@login_required
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash(f"User {username} not found.")
        return redirect(url_for('main.user', username=username))
    if user == current_user:
        flash(f"You can't unfollow yourself!")
        return redirect(url_for('main.user', username=username))
    current_user.unfollow(user)
    db.session.commit()
    flash(f"You've unfollowed {username}")
    
    response_html = redirect(url_for('main.user', username=username))
    return response_html


@bp.route('/search')
@login_required
def search():
    """
    Returns search form.

        Params
            None
        
        Side-Effects
            None

        Returns
            response_html (html)
                Rendered search form html
        Notes
            validate() method used rather than validate_on_submit() method.
                validate_on_submit() can't be used because it's only valid on POST requests; this is a GET request
                validate() only validates field values; here, that the field is non-empty.
    """
    # if empty search form ==> return to explore page
    if not g.search_form.validate(): 
        response_html = redirect(url_for('main.explore')) 
        return response_html
    
    # else (search form is valid)
    page = request.args.get('page', 1, type=int)
    # get page arg from request (e.g., /search?q=search_query_here&page=2)
    # if no page arg passed, default to 1
    posts, total = Post.search(g.search_form.q.data, page,
        current_app.config['POSTS_PER_PAGE'])
    # perform elasticsearch given the search form stored in g, the page to be returned, and the posts_per_page configuration
    next_url = url_for('main.search', q=g.search_form.q.data, page=page + 1) \
        if total > page * current_app.config['POSTS_PER_PAGE'] else None
    prev_url = url_for('main.search', q=g.search_form.q.data, page=page - 1) \
        if page > 1 else None
    
    response_html = render_template('search.html', title='Search',
        posts=posts, next_url=next_url, prev_url=prev_url)
    return response_html
