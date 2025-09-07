from datetime import datetime

class DomainIntel:
    def __init__(self, domain, ip=None, registrar=None, risk_score=0.0):
        self.domain = domain
        self.ip = ip
        self.registrar = registrar
        self.discovered_at = datetime.utcnow()
        self.risk_score = risk_score

    def to_dict(self):
        return {
            "domain": self.domain,
            "ip": self.ip,
            "registrar": self.registrar,
            "risk_score": self.risk_score,
            "discovered_at": self.discovered_at.isoformat()
        }
