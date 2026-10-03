from app.services.outreach_service import OutreachService
class OutreachAgent:
    def __init__(self,service=None): self.service=service or OutreachService()
    def run(self,research,dm,needs,score,icp,demo=False): return self.service.generate(research,dm,needs,score,icp,demo=demo)
