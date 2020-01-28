# python packages
from datetime import datetime
from hashlib import md5
# extensions
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
# local modules
from app import db, login
from app.search import add_to_index, remove_from_index, query_index

class SearchableMixin():
    """
    Notes
        @classmethod -- defines a method only used for class objects (and not a specific instance of a class)
        cls -- renaming of the `self` keyword to clarify that the method receives a class and not a class instance
    """
    @classmethod
    def search(cls, expression, page, per_page):
        """
        Returns search results as list of models (rather than model IDs). Does this by wrapping the app/search.query_index() function and replacing the object IDs with models.

            Params
                cls (object) -- the class object
                expression
                page
                per_page

            Notes
                To order the objects in hits_objects_list by object ID (elasticsearch orders results by importance), the SQL query needs to include a CASE WHEN statement in the ORDERY BY statement to order by the object's ID (the CASE WHEN provides this mapping)
        """
        ids, hits_count = query_index(cls.__tablename__, expression, page, per_page)
        if hits_count == 0:
            return cls.query.filter_by(id=0), 0
        when_clause = []
        for i in range(len(ids)):
            when_clause.append((ids[i], i))
        hits_objects_list = cls.query.filter(cls.id.in_(ids)). \
            order_by(db.case(when_clause, value=cls.id))
        return hits_objects_list, hits_count
            

    @classmethod
    def before_commit(cls, session):
        """
        Store session data before commit to enable using this information to update the elasticsearch index.

            Params

            Side-Effects
                session._changes (dict) -- create dicti 

            Returns
                None
        """
        session._changes = {
            'add': list(session.new),
            'update': list(session.dirty),
            'delete': list(session.deleted)
        }

    @classmethod
    def after_commit(cls, session):
        """
        Update elasticsearch index to mirror changes made to db during session.

            Params
                cls (obj)
                    Replacement for the `self` keyword. Emphasizes that this is a class method and therefore only receives a class as an argument (and not a class instance).
                session (???)
                    SQLAlchemy session object. Records changes intended to be made to the db.

            Side-Effects
                Elasticsearch object attached to app
                    Mutated to mirror changes made to the db during the session.
                session._changes
                    Set to None

            Returns
                None
        """
        for obj in session._changes['add']:
            if isinstance(obj, SearchableMixin):
                add_to_index(obj.__tablename__, obj)
        for obj in session._changes['update']:
            if isinstance(obj, SearchableMixin):
                add_to_index(obj.__tablename__, obj)
        for obj in session._changes['delete']:
            if isinstance(obj, SearchableMixin):
                remove_from_index(obj.__tablename__, obj)
        session._changes = None


    @classmethod
    def reindex(cls):
        """
        Initialize the index from all the records in the table.
            
            Params
                cls (obj)
                    Emphasizing this method receives a class object rather than an instance of a class object, the latter of which is typical and which is denoted using the `self` keyword.

            Side-effects
                cls (obj)
                    Re-initializes the index given all the records of the class in the database.

            Returns
                None
        """
        for obj in cls.query:
            add_to_index(cls.__tablename__, obj)


# Event listeners
db.event.listen(db.session, 'before_commit', SearchableMixin.before_commit)
db.event.listen(db.session, 'after_commit', SearchableMixin.after_commit)


# Association table
followers = db.Table(
    'followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id')))


# Users table
class User(UserMixin, db.Model):
    # columns
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)

    # relationships
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    followed = db.relationship(
        'User',
        secondary=followers,
        primaryjoin=(followers.c.follower_id == id), 
        # links left-side entity (follower user) to the association table
        secondaryjoin=(followers.c.followed_id == id),
        # links right-side entity (followed user) to the association table
        backref=db.backref('followers', lazy='dynamic'), 
        # defines how the relationship is exposed to the right-side entity
        # from left-side, relationship is named 'followed'; therefore, from
        # right-side, use 'followers' to represent all the left-side users
        # that are linked to the target user on the right side
        lazy='dynamic'
        )

    # print the username when User object is printed. this definition is
    # handled by the __repr__() method. 
    def __repr__(self):
        username_and_id = f"User: {self.username}; id: {self.id}"
        return username_and_id

    # set user's password
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    # check user's password
    def check_password(self, password):
        password_is_correct = check_password_hash(self.password_hash, password)
        return password_is_correct

    def get_avatar_image(self, size=70, default='identicon'):
        """
        Returns an avatar image for the user. Uses the Gravatar service which returns a unique avatar for each user by using a MD5 hash of their email address.
        """
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        gravatar_avatar_url = f"https://www.gravatar.com/avatar/{digest}?d={default}&s={size}"
        return gravatar_avatar_url

    # follow logic
    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)

    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)

    def is_following(self, user):
        # check association table ('followers') for self following user
        return self.followed.filter( # follower == self
            followers.c.followed_id == user.id # followed == user
            ).count() > 0
    
    def feed_posts(self):
        # all posts from all users who are followed
        # filter to posts where the user is followed by self
        followed_posts = Post.query. \
            join(followers, (followers.c.followed_id == Post.user_id)). \
                filter(followers.c.follower_id == self.id)
        own_posts = Post.query.filter_by(user_id=self.id)
        feed_posts = followed_posts.union(own_posts) \
            .order_by(Post.timestamp.desc())
        return feed_posts


# enable the login object to access a User record when it calls its 
# user_loader method on a stringified version of a user_id. do this
# by decorating a method on the User table.
@login.user_loader
def load_user(id):
    return User.query.get(int(id))
    

class Post(SearchableMixin, db.Model):
    __searchable__ = ['body']
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        post_user_and_body = f"user: {self.user_id}; post: {self.body}"
        return post_user_and_body

