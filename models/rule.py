from pydantic import BaseModel


class Rule(BaseModel):
    """
    A class representing a rule for a particular feature.
    """
    feature_url: str
    ratio: float
    delay_before_reanswer: int
    delay_to_answer: int
    is_active: bool
