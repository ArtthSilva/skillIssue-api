from dataclasses import dataclass
from typing import List, Optional

@dataclass
class Job:
    title: str
    company: str
    location: str
    desc: str
    source: str
    url: Optional[str] = None

JobList = List[Job]
