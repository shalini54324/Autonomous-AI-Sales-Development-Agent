from app.services.outreach_service import OutreachService
class FollowUpAgent:
    def __init__(self,service=None): self.service=service or OutreachService()
    def run(self,research,dm,needs,score,icp,demo=False): return self.service.followup(research,dm,needs,score,icp,demo=demo)
