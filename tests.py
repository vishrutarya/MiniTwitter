# python packages
from datetime import datetime, timedelta
import unittest
# local modules
from app import app_factory, db
from app.models import User, Post
from config import Config


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite://'


class UserModelCase(unittest.TestCase):
    def setUp(self):
        self.app = app_factory(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
    
    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_password_hashing(self):
        """
        Test the check_password method.
        """
        u = User(username='sally')
        u.set_password('cat')
        self.assertFalse(u.check_password('dog'))
        self.assertTrue(u.check_password('cat'))

    def test_get_avatar_image(self):
        """
        Test the get_avatar_image method
        """
        u = User(username='john', email='john@example.com')
        self.assertEqual(u.get_avatar_image(size=128),
        ('https://www.gravatar.com/avatar/d4c74594d841139328695756648b6bd6?d=identicon&s=128'))

    def test_follow(self):
        """
        Test the follow method.
        """
        u1 = User(username='john', email='john@example.com')
        u2 = User(username='sally', email='sally@example.com')
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()

        # test: u1 and u2 instantiated; no extraneous follows
        self.assertEqual(u1.followed.all(), [])
        self.assertEqual(u2.followed.all(), [])

        # test: u1 follows u2 
        u1.follow(u2)
        db.session.commit()
        self.assertTrue(u1.is_following(u2))
        self.assertEqual(u1.followed.count(), 1)
        self.assertEqual(u1.followed.first().username, 'sally')
        self.assertEqual(u2.followers.count(), 1)
        self.assertEqual(u2.followers.first().username, 'john')

        # test: u1 unfollows u2
        u1.unfollow(u2)
        db.session.commit()
        self.assertFalse(u1.is_following(u2))
        self.assertEqual(u1.followed.count(), 0)
        self.assertEqual(u2.followers.count(), 0)

    # test: feed posts
    def test_feed_posts(self):
        # make four users
        u1 = User(username='john', email='john@example.com')
        u2 = User(username='sally', email='sally@example.com')
        u3 = User(username='mary', email='mary@example.com')
        u4 = User(username='david', email='david@example.com')

        # make one post for each user
        # for robustness: make timedeltas not-perfectly-correlated
        # with sequence in post count
        now = datetime.utcnow()
        p1 = Post(body='post from john', author=u1,
            timestamp=now + timedelta(seconds=1))
        p2 = Post(body='post from sally', author=u2,
            timestamp=now + timedelta(seconds=4))
        p3 = Post(body='post from mary', author=u3,
            timestamp=now + timedelta(seconds=3))
        p4 = Post(body='post from david', author=u4,
            timestamp=now + timedelta(seconds=2))
        db.session.add_all([p1, p2, p3, p4])
        db.session.commit()

        # define followers
        u1.follow(u2) # john follows sally
        u1.follow(u4) # john follows david
        u2.follow(u3) # sally follows mary
        u3.follow(u4) # mary follows david
        db.session.commit()

        # check the followed posts of each user
        f1 = u1.feed_posts().all()
        f2 = u2.feed_posts().all()
        f3 = u3.feed_posts().all()
        f4 = u4.feed_posts().all()
        self.assertEqual(f1, [p2, p4, p1]) 
        # recall sally has biggest timedelta
        self.assertEqual(f2, [p2, p3]) 
        self.assertEqual(f3, [p3, p4]) 
        self.assertEqual(f4, [p4])
            
if __name__ == '__main__':
    unittest.main(verbosity=2)

        
    