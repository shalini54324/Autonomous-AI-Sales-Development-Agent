from app.services.scoring_service import ScoringService
class LeadScoringAgent:
    def __init__(self,service=None): self.service=service or ScoringService()
    def run(self,research,dm,needs,icp,thresholds=None): return self.service.calculate(research,dm,needs,icp,thresholds=thresholds)
