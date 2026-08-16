"""Mock ServiceNow integration.

POC stand-in for the ServiceNow instance where incidents / service requests
are logged and tracked. In production this uses the ServiceNow REST Table API
(incident / sc_req_item tables) with an OAuth or basic-auth integration user.
"""
from __future__ import annotations

import itertools
from dataclasses import dataclass, field
from datetime import datetime

_ticket_counter = itertools.count(10001)


@dataclass
class Ticket:
    number: str
    record_type: str
    short_description: str
    category: str
    impact: str
    urgency: str
    priority: str
    state: str = "New"
    created: str = field(default_factory=lambda: datetime.now().isoformat(timespec="seconds"))
    contact_channel: str = "chat"
    caller: str = ""
    description: str = ""
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "number": self.number,
            "record_type": self.record_type,
            "short_description": self.short_description,
            "category": self.category,
            "impact": self.impact,
            "urgency": self.urgency,
            "priority": self.priority,
            "state": self.state,
            "created": self.created,
            "contact_channel": self.contact_channel,
            "caller": self.caller,
            "description": self.description,
            "notes": list(self.notes),
        }


class ServiceNowMock:
    """In-memory ticket store simulating a ServiceNow instance."""

    def __init__(self) -> None:
        self._tickets: dict[str, Ticket] = {}

    def create_incident(self, **kwargs) -> Ticket:
        ticket = Ticket(
            number=f"INC{next(_ticket_counter):06d}",
            record_type="Incident",
            **kwargs,
        )
        self._tickets[ticket.number] = ticket
        return ticket

    def create_request(self, **kwargs) -> Ticket:
        ticket = Ticket(
            number=f"REQ{next(_ticket_counter):06d}",
            record_type="Service Request",
            **kwargs,
        )
        self._tickets[ticket.number] = ticket
        return ticket

    def add_note(self, number: str, note: str) -> None:
        if number in self._tickets:
            self._tickets[number].notes.append(note)

    def get(self, number: str) -> Ticket | None:
        return self._tickets.get(number)

    def list(self) -> list[dict]:
        return [t.to_dict() for t in self._tickets.values()]


_servicenow = ServiceNowMock()


def get_servicenow() -> ServiceNowMock:
    return _servicenow
