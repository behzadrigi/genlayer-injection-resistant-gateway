# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }

import json
import re

from genlayer import *
from dataclasses import dataclass


def extract_domain(url: str):
    try:
        without_protocol = re.sub(r'^https?://', '', url)
        domain = without_protocol.split('/')[0]
        return re.sub(r'^www\.', '', domain)
    except Exception:
        return ""


@allow_storage
@dataclass
class CorroborationRecord:
    corroboration_id: u256
    agent: str
    claim: str
    claim_id_a: u256
    claim_id_b: u256
    domain_a: str
    domain_b: str
    status: str  # CORROBORATED, NOT_CORROBORATED


class CrossSourceCorroboration(gl.Contract):
    corroborations: TreeMap[u256, CorroborationRecord]
    pair_used: TreeMap[str, bool]
    next_id: u256
    review_contract: str

    def __init__(self, review_address: str):
        self.next_id = u256(0)
        self.review_contract = review_address

    @gl.public.write
    def corroborate(self, claim_id_a: u256, claim_id_b: u256) -> u256:
        assert claim_id_a != claim_id_b, "Must provide two distinct claim ids"

        ia, ib = int(claim_id_a), int(claim_id_b)
        pair_key = f"{min(ia, ib)}:{max(ia, ib)}"
        assert pair_key not in self.pair_used, "This pair has already been corroborated"

        raw_a = gl.get_contract_at(
            Address(self.review_contract)
        ).view().get_claim_data(claim_id_a)
        assert raw_a != "NOT_FOUND", "Claim A not found"

        raw_b = gl.get_contract_at(
            Address(self.review_contract)
        ).view().get_claim_data(claim_id_b)
        assert raw_b != "NOT_FOUND", "Claim B not found"

        try:
            data_a = json.loads(raw_a)
            data_b = json.loads(raw_b)
        except:
            raise gl.vm.UserError("Invalid data from review contract")

        assert data_a.get("status", "") == "REVIEWED", "Claim A has not been reviewed yet"
        assert data_b.get("status", "") == "REVIEWED", "Claim B has not been reviewed yet"
        assert data_a.get("claim", "") == data_b.get("claim", ""), \
            "Both claims must be the exact same statement to corroborate each other"

        domain_a = extract_domain(data_a.get("source_url", ""))
        domain_b = extract_domain(data_b.get("source_url", ""))
        assert domain_a != "" and domain_b != "", "Could not determine source domains"
        assert domain_a != domain_b, "Sources must come from independent domains"

        both_supported = (
            data_a.get("verdict", "") == "SUPPORTED"
            and data_b.get("verdict", "") == "SUPPORTED"
        )
        status = "CORROBORATED" if both_supported else "NOT_CORROBORATED"

        cid = self.next_id
        self.next_id += u256(1)
        self.corroborations[cid] = CorroborationRecord(
            corroboration_id=cid,
            agent=data_a.get("agent", ""),
            claim=data_a.get("claim", ""),
            claim_id_a=claim_id_a,
            claim_id_b=claim_id_b,
            domain_a=domain_a,
            domain_b=domain_b,
            status=status,
        )
        self.pair_used[pair_key] = True
        return cid

    @gl.public.view
    def get_corroboration_data(self, corroboration_id: u256) -> str:
        if corroboration_id not in self.corroborations:
            return "NOT_FOUND"
        c = self.corroborations[corroboration_id]
        return json.dumps({
            "corroboration_id": int(c.corroboration_id),
            "agent": c.agent,
            "claim": c.claim,
            "claim_id_a": int(c.claim_id_a),
            "claim_id_b": int(c.claim_id_b),
            "domain_a": c.domain_a,
            "domain_b": c.domain_b,
            "status": c.status,
        })

    @gl.public.view
    def list_corroborations(self) -> str:
        items = []
        for key in self.corroborations:
            c = self.corroborations[key]
            items.append(f"{int(c.corroboration_id)}:{c.status}")
        return ",".join(items)
