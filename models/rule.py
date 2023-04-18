class Rule:
    """
    A class representing a rule for a particular feature.
    """

    def __init__(
        self,
        feature_url: str,
        ratio: float,
        delay_before_reanswer: int,
        delay_to_answer: int,
        is_active: bool,
    ):
        """
        Initializes a new instance of the Rule class.

        Args:
        feature_url (str): The URL of the feature associated with the rule.
        ratio (float): The ratio associated with the rule.
        delay_before_reanswer (int): The delay before re-answering associated with the rule.
        delay_to_answer (int): The delay to answer associated with the rule.
        is_active (bool): Whether or not the rule is active.
        """
        self.feature_url = feature_url
        self.ratio = ratio
        self.delay_before_reanswer = delay_before_reanswer
        self.delay_to_answer = delay_to_answer
        self.is_active = is_active
