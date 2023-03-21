import unittest
from fastapi.testclient import TestClient
import sqlite3
from models.comment import Comment
from main import app
from models.comment import Comment
from repository.DBrepository import CommentRepository

class TestComments(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        self.conn = sqlite3.connect('data/survey.sqlite3')
        self.cur = self.conn.cursor()
        self.cur.execute("CREATE TABLE IF NOT EXISTS Comment (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, email TEXT, rating INTEGER, comment TEXT, project_name TEXT, feature_url TEXT, user_id INTEGER, timestamp TEXT)")
        

    def tearDown(self):
        self.cur.execute("DELETE FROM Comment")
        self.conn.commit()
        self.conn.close()



    async def test_create_comment(self):
        comment_repo = CommentRepository()
        comment = Comment(
            id=1,
            project_name="Project X",
            feature_url="http://example.com/feature",
            user_id=123,
            timestamp=1234567890,
            rating=4,
            comment="This is a test comment"
        )
        created_comment = await comment_repo.create_comment(comment)
        assert created_comment.id == comment.id
        assert created_comment.project_name == comment.project_name
        assert created_comment.feature_url == comment.feature_url
        assert created_comment.user_id == comment.user_id
        assert created_comment.timestamp == comment.timestamp
        assert created_comment.rating == comment.rating
        assert created_comment.comment == comment.comment
        print("Test 'test_create_comment' passed successfully")

    async def test_read_comments(self):
        comment_repo = CommentRepository()
        comments = comment_repo.read_comments()
        assert isinstance(comments, list)
        assert all(isinstance(comment, Comment) for comment in comments)
        print("Test 'test_read_comments' passed successfully")
        
    def test_create_comment_requete(self):
        data = {
            "id":"1",
            "project_name": "Project1",
            "feature_url": "http://project1.com",
            "user_id": "123",
            "timestamp": "2022-03-17T10:00:00Z",
            "rating": 4,
            "comment": "Great product!"
        }
        response = self.client.post("/comments", json=data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json(), {"message": "comment created successfully"})

    def test_get_all_Comment(self):
        response = self.client.get("/comments")
        self.assertEqual(response.status_code, 200)
        Comment = response.json()
        self.assertIsInstance(Comment, list)
        for comment in Comment:
            self.assertIsInstance(comment, Comment)

    def test_database_connection(self):
        conn = sqlite3.connect('data/survey.sqlite3')
        cur = conn.cursor()
        cur.execute("SELECT * FROM Comment")
        rows = cur.fetchall()
        conn.close()
        self.assertIsInstance(rows, list)

if __name__ == '__main__':
    unittest.main()
