from sqlalchemy.orm import Session
from model.model import Evaluation, EvaluationStatus
from typing import Optional
import uuid

class EvaluationRepository:
    def __init__(self, session: Session):
        self.session = session
    
    def close(self):
        if self.session:
            self.session.close()

    def create(self, evaluation: Evaluation) -> Evaluation:
        try:
            self.session.add(evaluation)
            self.session.commit()
            self.session.refresh(evaluation)
            return evaluation
        except Exception as e:
            self.session.rollback()
            raise e


    def get_by_id(self, evaluation_id: str) -> Optional[Evaluation]:
        try:
            return self.session.query(Evaluation).filter(Evaluation.id == evaluation_id).first()
        except Exception as e:
            self.session.rollback()
            raise e

    def update_status(self, evaluation_id: str, status: EvaluationStatus) -> Optional[Evaluation]:
        try:
            evaluation = self.session.query(Evaluation).filter(Evaluation.id == evaluation_id).first()
            if evaluation:
                evaluation.status = status
                self.session.commit()
                self.session.refresh(evaluation)
            return evaluation
        except Exception as e:
            self.session.rollback()
            raise e

    def fill_results(self, evaluation_id: str, cv_match_rate: float, cv_feedback: str, project_score: float, overall_summary: str) -> Optional[Evaluation]:
        try:
            evaluation = self.session.query(Evaluation).filter(Evaluation.id == evaluation_id).first()
            if evaluation:
                evaluation.cv_match_rate = cv_match_rate
                evaluation.cv_feedback = cv_feedback
                evaluation.project_score = project_score
                evaluation.overall_summary = overall_summary
                evaluation.status = EvaluationStatus.completed
                self.session.commit()
                self.session.refresh(evaluation)
            return evaluation
        except Exception as e:
            self.session.rollback()
            raise e