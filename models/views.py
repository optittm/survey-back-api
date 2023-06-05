from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class FeatureRatingAvg(Base):
    __tablename__ = 'feature_rating_avg'
    project_id = Column(Integer, primary_key=True)
    feature_url = Column(String, primary_key=True)
    average_rating = Column(Float)

class ProjectRatingAvg(Base):
    __tablename__ = 'project_rating_avg'
    project_id = Column(Integer, primary_key=True)
    average_rating = Column(Float)

class NumberCommentByProject(Base):
    __tablename__ = 'number_comment_by_project'
    project_id = Column(Integer, primary_key=True)
    number_comment = Column(Integer)

class NumberDisplayByProject(Base):
    __tablename__ = 'number_display_by_project'
    project_id = Column(Integer, primary_key=True)
    number_display = Column(Integer)