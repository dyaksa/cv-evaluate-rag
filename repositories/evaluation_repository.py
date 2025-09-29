from sqlalchemy.orm import Session
from model.model import Evaluation, EvaluationStatus
from typing import Optional

class EvaluationRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, evaluation: Evaluation) -> Evaluation:
        self.session.add(evaluation)
        self.session.commit()
        self.session.refresh(evaluation)
        return evaluation

    def get_by_id(self, evaluation_id: int) -> Optional[Evaluation]:
        return self.session.query(Evaluation).filter(Evaluation.id == evaluation_id).first()

    def update_status(self, evaluation_id: int, status: EvaluationStatus) -> Optional[Evaluation]:
        evaluation = self.get_by_id(evaluation_id)
        if evaluation:
            evaluation.status = status
            self.session.commit()
            self.session.refresh(evaluation)
        return evaluation

    def fill_results(self, evaluation_id: int, cv_match_rate: float, cv_feedback: str, project_score: float, overall_summary: str) -> Optional[Evaluation]:
        evaluation = self.get_by_id(evaluation_id)
        if evaluation:
            evaluation.cv_match_rate = cv_match_rate
            evaluation.cv_feedback = cv_feedback
            evaluation.project_score = project_score
            evaluation.overall_summary = overall_summary
            evaluation.status = EvaluationStatus.completed
            self.session.commit()
            self.session.refresh(evaluation)
        return evaluation