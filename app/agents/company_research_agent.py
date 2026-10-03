from app.services.research_service import ResearchService
class CompanyResearchAgent:
    def __init__(self,service=None): self.service=service or ResearchService()
    def run(self,company,demo=False): return self.service.demo_research(company) if demo else self.service.live_research(company)
