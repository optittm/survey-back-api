from datetime import datetime
from typing import List

from models.comment import Comment, CommentPostBody
from models.project import Project

class SQLiteRepository:
    
    async def create_comment(self, commentcookie: CommentPostBody, user_id, timestamp, project_name: str):
        
        timestamp = datetime.strptime(timestamp, '%Y-%m-%dT%H:%M:%S').isoformat()

        projects = await Project.filter(name=project_name)

        if len(projects) == 0:
            #ajouter une partie qui permet de gérer la clé 
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