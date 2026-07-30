from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True)
class Approval:

    status: str = "draft"

    approved_by: str = ""

    approved_at: str = ""

    remarks: str = ""

    def approve(self, administrator: str):

        self.status = "approved"

        self.approved_by = administrator

        self.approved_at = datetime.utcnow().isoformat()
