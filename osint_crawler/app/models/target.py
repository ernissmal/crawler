import json
import os
from typing import List, Dict
from dotenv import load_dotenv

class GoogleGeekingModel:
    def __init__(self, seed: str, seed_type: str = "name"):
        """
        :param seed: The initial data point (name, email, username, phone, company)
        :param seed_type: Type of seed ("name", "email", "username", "phone", "company")
        """
        self.seed = seed
        self.seed_type = seed_type
        self.queries = self._generate_queries()

    def _generate_queries(self) -> Dict[str, List[str]]:
        """Generate Google dork queries based on the seed type."""
        q = {}

        # General
        q["general"] = [
            f"\"{self.seed}\"",
            f"\"{self.seed}\" site:linkedin.com",
            f"\"{self.seed}\" site:facebook.com",
            f"\"{self.seed}\" site:twitter.com",
            f"\"{self.seed}\" site:instagram.com",
        ]

        # Name-based searches
        if self.seed_type == "name":
            q["documents"] = [
                f"intitle:resume \"{self.seed}\"",
                f"filetype:pdf \"{self.seed}\"",
                f"filetype:doc \"{self.seed}\"",
                f"\"{self.seed}\" site:github.com",
            ]
        
        # Email-based searches
        if self.seed_type == "email":
            q["email"] = [
                f"\"{self.seed}\"",
                f"\"{self.seed}\" site:pastebin.com",
                f"\"{self.seed}\" site:github.com",
                f"\"{self.seed}\" filetype:txt",
            ]

        # Username searches
        if self.seed_type == "username":
            q["username"] = [
                f"\"{self.seed}\" site:reddit.com",
                f"\"{self.seed}\" site:github.com",
                f"\"{self.seed}\" site:stackoverflow.com",
                f"\"{self.seed}\" site:medium.com",
            ]

        # Phone searches
        if self.seed_type == "phone":
            q["phone"] = [
                f"\"{self.seed}\"",
                f"\"{self.seed}\" site:facebook.com",
                f"\"{self.seed}\" site:instagram.com",
                f"\"{self.seed}\" site:twitter.com",
            ]

        # Company searches
        if self.seed_type == "company":
            q["company"] = [
                f"\"{self.seed}\" site:linkedin.com",
                f"\"{self.seed}\" site:crunchbase.com",
                f"\"{self.seed}\" site:glassdoor.com",
                f"\"{self.seed}\" filetype:pdf",
            ]

        return q