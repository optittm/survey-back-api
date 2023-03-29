from datetime import datetime
from typing import List

from models.comment import Comment
from models.commentcookie import CommentCookie
from models.project import Project

class SQLiteRepository:
    
    async def create_comment(self,commentcookie: CommentCookie,user_id, timestamp, project_name: str):
        
        timestamp = datetime.strptime(timestamp, '%m/%d/%y %H:%M:%S')

        projects = await Project.filter(Project.name==project_name)

        if len(projects)==0:
            await self.create_project(Project(project_name))

        new_comment = await Comment.create(
            project_id= projects[0].id,
            feature_url= commentcookie.feature_url,
            user_id= user_id,
            timestamp= timestamp,
            rating=commentcookie.rating,
            comment=commentcookie.comment,
        )

        await new_comment.insert()
        await new_comment.save()
        return new_comment

    async def read_comments(self) -> List[Comment]:
        comments = await Comment.all()
        return comments
    
    async def create_project(self, project: Project):
        new_project = await Project.create(
            name=project.name,
        )
        await new_project.insert()
        await new_project.save()
        return new_project