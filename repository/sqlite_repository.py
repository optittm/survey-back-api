from datetime import datetime
from typing import List

from models.comment import Comment, CommentGetBody, CommentPostBody
from models.project import Project

class SQLiteRepository:
    
    async def create_comment(self, commentcookie: CommentPostBody, user_id, timestamp, project_name: str):
        
        timestamp = datetime.strptime(timestamp, '%m/%d/%y %H:%M:%S')

        projects = await Project.filter(name=project_name)

        if len(projects) == 0:
            project = await self.create_project(Project(name=project_name))
        else:
            project = projects[0]

        new_comment = Comment(
            project_id= project.id,
            feature_url= commentcookie.feature_url,
            user_id= user_id,
            timestamp= timestamp,
            rating=commentcookie.rating,
            comment=commentcookie.comment,
        )
        id = await new_comment.insert()
        new_comment.id = id
        return new_comment

    async def read_comments(self) -> List[Comment]:
        comments = await Comment.all()
        return comments
    
    async def create_project(self, project: Project):
        id = await project.insert()
        project.id = id
        return project

    async def get_project_by_id(self, project_id : int):
        project = await Project.get(id=project_id)
        return project

