from datetime import datetime
from typing import List
from pydbantic import Database
from models.comment import Comment

class CommentRepository:
       
    async def create_comment(self,comment: Comment):
        new_comment = Comment.create(
            project_name= comment.project_name,
            feature_url= comment.feature_url,
            user_id= comment.user_id,
            timestamp= datetime.now(),
            rating=comment.rating,
            comment=comment.comment,
        )

        new_comment.save()
        return comment

    async def read_comments(self) -> List[Comment]:
        comments = await Comment.all()
        return comments