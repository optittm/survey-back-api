from math import ceil
import unittest
from datetime import datetime
from unittest.mock import AsyncMock, Mock

from models.comment import Comment, CommentGetBody
from models.pagination import Pagination
from models.project import Project
from repository.sqlite_repository import SQLiteRepository
from utils.formatter import comment_to_comment_get_body, paginate_results
from utils.nlp import NlpPreprocess


class TestUtils(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.sqliterepo = AsyncMock(spec=SQLiteRepository)
        self.comment = Comment(
            id=1,
            project_id=1,
            user_id=123,
            timestamp=datetime.now().isoformat(),
            feature_url="http://test.com",
            rating=5,
            comment="This is a test comment",
            language="en",
        )

    async def test_comment_to_comment_get_body(self):
        self.sqliterepo.get_project_by_id = AsyncMock(
            return_value=Project(id=1, name="test_project")
        )
        nlp = Mock(spec=NlpPreprocess)
        nlp.text_preprocess.return_value = None
        
        result = await comment_to_comment_get_body(
            self.comment, sqliterepo=self.sqliterepo, nlp_preprocess=nlp
        )
        self.assertEqual(
            result,
            CommentGetBody(
                id=1,
                project_name="test_project",
                user_id=123,
                timestamp=self.comment.timestamp,
                feature_url="http://test.com",
                rating=5,
                comment="This is a test comment",
                language="en",
            ),
        )
        self.sqliterepo.get_project_by_id.assert_called_once_with(1)
    
    def test_pagination(self):
        items = ["1", "2", "3", "4", "5"]

        resource_url = "http://localhost/api/v1/numbers"
        page_size = 2
        expected_total_pages = ceil(len(items) / page_size)

        # Test first page
        request_filters = {"key": "value", "number": 7}
        page = 1
        expected_pagination = Pagination(
            results=items[:page_size],
            total_pages=expected_total_pages,
            page=page,
            page_size=page_size,
            total=len(items),
            next_page=f"{resource_url}?page={page + 1}&page_size={page_size}&key=value&number=7",
            previous_page=None,
        )
        result = paginate_results(
            items,
            page_size,
            page,
            resource_url,
            request_filters
        )
        self.assertEqual(result, expected_pagination)

        # Test second page
        request_filters = {"key": "value"}
        page = 2
        expected_pagination = Pagination(
            results=items[page_size : page_size * 2],
            total_pages=expected_total_pages,
            page=page,
            page_size=page_size,
            total=len(items),
            next_page=f"{resource_url}?page={page + 1}&page_size={page_size}&key=value",
            previous_page=f"{resource_url}?page={page - 1}&page_size={page_size}&key=value",
        )
        result = paginate_results(
            items,
            page_size,
            page,
            resource_url,
            request_filters
        )
        self.assertEqual(result, expected_pagination)

        # Test last page
        request_filters = None
        page = 3
        expected_pagination = Pagination(
            results=items[page_size * 2 :],
            total_pages=expected_total_pages,
            page=page,
            page_size=page_size,
            total=len(items),
            next_page=None,
            previous_page=f"{resource_url}?page={page - 1}&page_size={page_size}",
        )
        result = paginate_results(
            items,
            page_size,
            page,
            resource_url,
            request_filters
        )
        self.assertEqual(result, expected_pagination)

    def test_pagination_invalid_page_nb(self):
        with self.assertRaises(ValueError) as cm:
            paginate_results(
                [],
                2,
                0,
                "/test",
                None
            )
    
    def test_pagination_invalid_page_size(self):
         with self.assertRaises(ValueError) as cm:
            paginate_results(
                [],
                0,
                1,
                "/test",
                None
            )