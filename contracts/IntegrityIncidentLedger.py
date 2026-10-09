# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }

import json

from genlayer import *
from dataclasses import dataclass


@allow_storage
@dataclass
class IncidentRecord:
    incident_id: u256
    source_url: str
    scan_requester: str
    reported_by: str
    status: str  # LOGGED


class IntegrityIncidentLedger(gl.Contract):
    incidents: TreeMap[u256, IncidentRecord]
    logged_urls: TreeMap[str, bool]
    next_id: u256
    scanner_contract: str

    def __init__(self, scanner_address: str):
        self.next_id = u256(0)
        self.scanner_contract = scanner_address

    @gl.public.write
    def record_incident(self, source_url: str) -> u256:
        raw = gl.get_contract_at(
            Address(self.scanner_contract)
        ).view().get_scan_data(source_url)
        assert raw != "NOT_FOUND", "Source has not been scanned yet"

        try:
            data = json.loads(raw)
        except:
            raise gl.vm.UserError("Invalid data from scanner")

        assert data.get("verdict", "") == "SUSPICIOUS", "Only SUSPICIOUS sources can be logged as incidents"

        url = data.get("source_url", "")
        assert url != "", "Source url missing in scan record"
        assert url not in self.logged_urls, "Already logged"

        iid = self.next_id
        self.next_id += u256(1)
        self.incidents[iid] = IncidentRecord(
            incident_id=iid,
            source_url=url,
            scan_requester=data.get("requester", ""),
            reported_by=str(gl.message.sender_address),
            status="LOGGED",
        )
        self.logged_urls[url] = True
        return iid

    @gl.public.view
    def get_incident_data(self, incident_id: u256) -> str:
        if incident_id not in self.incidents:
            return "NOT_FOUND"
        i = self.incidents[incident_id]
        return json.dumps({
            "incident_id": int(i.incident_id),
            "source_url": i.source_url,
            "scan_requester": i.scan_requester,
            "reported_by": i.reported_by,
            "status": i.status,
        })

    @gl.public.view
    def list_incidents(self) -> str:
        items = []
        for key in self.incidents:
            i = self.incidents[key]
            items.append(f"{int(i.incident_id)}:{i.source_url}")
        return ",".join(items)
