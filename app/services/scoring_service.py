from __future__ import annotations
from app.schemas.icp import ICPInput
from app.schemas.lead import ResearchResult, DecisionMaker, NeedItem, ScoreResult

DEFAULT_THRESHOLDS={"HOT":85,"HIGH PRIORITY":70,"WARM":50,"LOW":0}

def classify_score(score:int, thresholds:dict[str,int]|None=None)->str:
    t=thresholds or DEFAULT_THRESHOLDS
    if score>=t["HOT"]: return "HOT"
    if score>=t["HIGH PRIORITY"]: return "HIGH PRIORITY"
    if score>=t["WARM"]: return "WARM"
    return "LOW"

class ScoringService:
    def calculate(self,r:ResearchResult,dm:DecisionMaker,needs:list[NeedItem],icp:ICPInput,thresholds:dict[str,int]|None=None)->ScoreResult:
        rat=[]
        industry=20 if icp.target_industry.lower() in (r.industry or "").lower() or (r.industry or "").lower() in icp.target_industry.lower() else (8 if r.industry!="Unknown" else 3)
        rat.append(f"Industry fit: {industry}/20")
        if r.company_size is None: size=7
        elif icp.min_employees<=r.company_size<=icp.max_employees: size=15
        else: size=4
        rat.append(f"Company-size fit: {size}/15")
        loc=10 if icp.target_location.lower() in {"global","worldwide","any"} or icp.target_location.lower() in (r.location or "").lower() else (3 if r.location!="Unknown" else 1)
        role=15 if any(x.lower() in dm.role.lower() for x in icp.target_roles) else (7 if dm.role!="Unknown" else 2)
        need_strength=min(25, 8*len(needs)+ (5 if any(n.relevance.lower()=="high" for n in needs) else 0))
        tech=5 if not icp.technology_requirements else min(8,2*sum(any(req.lower() in s.lower() for s in r.technology_signals) for req in icp.technology_requirements)+2)
        signals=min(7, len(r.growth_signals)*2+len(r.recent_signals))
        confidence=5 if r.research_status in {"complete","demo"} else 2
        breakdown={"Industry Fit":industry,"Size Fit":size,"Location Fit":loc,"Decision Maker":role,"Need Fit":need_strength,"Technology Fit":tech,"Signals":signals,"Research Confidence":confidence}
        total=min(100,sum(breakdown.values()))
        rat += [f"Need fit: {need_strength}/25",f"Decision-maker relevance: {role}/15",f"Research confidence: {confidence}/5"]
        return ScoreResult(total=total,classification=classify_score(total,thresholds),breakdown=breakdown,rationale=rat)
