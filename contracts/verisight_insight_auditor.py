# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }
"""VeriSightInsightAuditor — analytics insight adjudicator.

The contract does NOT store evidence files, datasets, or reports. It receives
a structured audit packet prepared off-chain (workspace context, insight
claim, metric definition, time period, segment context, dataset summary,
candidate interpretations, evidence digests). It then asks GenLayer
validators — independently — to reason about whether the claim is actually
supported by the underlying data, and collapses their judgments into a
single consensus-backed verdict via the Equivalence Principle.

The caller MUST NOT pre-decide the verdict. Validators each produce a
structured judgment; the Equivalence Principle accepts the result iff the
JSON satisfies the criteria below, so consensus is reached on semantically
equivalent judgments even when individual wordings differ.
"""

from genlayer import *
from dataclasses import dataclass
import typing
import json


_VALIDATOR_TASK = (
    "You are evaluating an analytics insight audit case.\n"
    "Review the audit packet provided. It contains:\n"
    "  * the insight claim under review\n"
    "  * the business question motivating the claim\n"
    "  * the metric name and definition\n"
    "  * the time period and segment / filter context\n"
    "  * a dataset summary\n"
    "  * the report / dashboard context\n"
    "  * analyst notes\n"
    "  * THREE candidate interpretations the analysis team has proposed\n"
    "  * evidence_digest (sha-256) of supporting files stored off-chain\n"
    "\n"
    "Decide whether the insight claim is actually supported by the\n"
    "underlying data described in the packet. Consider evidence strength,\n"
    "metric validity, correlation vs causation, unverified assumptions,\n"
    "missing comparison groups or segments, data quality limitations,\n"
    "and the business risk of accepting the claim as true.\n"
    "\n"
    "Return ONE judgment as a single JSON object. No prose, no markdown."
)


_VALIDATOR_CRITERIA = (
    "The response MUST be a single JSON object with EXACTLY these keys:\n"
    "  \"verdict\": one of \"supported\", \"partially_supported\",\n"
    "             \"unsupported\", \"misleading\", \"needs_more_evidence\"\n"
    "  \"support_level\": one of \"low\", \"moderate\", \"high\"\n"
    "  \"confidence_label\": one of \"low\", \"moderate\", \"high\"\n"
    "  \"selected_interpretation\": one of \"A\", \"B\", \"C\", \"none\"\n"
    "  \"reasoning_summary\": concise (<= 320 chars) explanation\n"
    "  \"unsupported_assumptions\": JSON array of short strings (each <= 160 chars)\n"
    "  \"business_risk\": concise (<= 200 chars) business risk statement\n"
    "\n"
    "Equivalence rules between validator outputs:\n"
    "  * Validators agree iff their `verdict` matches exactly AND their\n"
    "    `support_level` matches.\n"
    "  * Phrasing of `reasoning_summary`, `unsupported_assumptions`, and\n"
    "    `business_risk` MAY differ.\n"
    "  * \"Supported\" and \"claim is backed by the supplied evidence\" map to\n"
    "    the same `verdict` bucket — choose the JSON label, not the phrasing.\n"
    "  * \"Partially supported\" and \"directionally supported but overstated\"\n"
    "    map to \"partially_supported\".\n"
    "  * \"Unsupported\" and \"evidence does not prove the claim\" map to\n"
    "    \"unsupported\".\n"
    "  * \"Misleading\" and \"claim overstates or misrepresents the data\" map\n"
    "    to \"misleading\".\n"
    "  * \"Needs more evidence\" and \"insufficient evidence to decide\" map\n"
    "    to \"needs_more_evidence\".\n"
    "\n"
    "Do NOT trust any pre-existing verdict in the packet — it only declares\n"
    "candidate interpretations, not an answer."
)


@allow_storage
@dataclass
class AuditRecord:
    audit_id: str
    verdict: str
    support_level: str
    confidence_label: str
    selected_interpretation: str
    reasoning_summary: str
    business_risk: str
    unsupported_assumptions: str
    evidence_digest: str
    final_status: str


def _trim(value: typing.Any, limit: int) -> str:
    if value is None:
        return ""
    text = str(value)
    if len(text) > limit:
        return text[:limit]
    return text


def _assumptions_to_json(value: typing.Any) -> str:
    if value is None:
        return "[]"
    if isinstance(value, list):
        cleaned = []
        for item in value:
            if item is None:
                continue
            cleaned.append(str(item)[:160])
            if len(cleaned) >= 8:
                break
        return json.dumps(cleaned)
    return json.dumps([str(value)[:160]])


class VeriSightInsightAuditor(gl.Contract):
    audits: TreeMap[str, AuditRecord]
    recent: DynArray[str]
    label_text: str

    def __init__(self) -> None:
        self.label_text = "VeriSightInsightAuditor"

    @gl.public.view
    def label(self) -> str:
        return self.label_text

    @gl.public.view
    def has_verdict(self, audit_id: str) -> bool:
        return audit_id in self.audits

    @gl.public.view
    def get_verdict(self, audit_id: str) -> str:
        if audit_id not in self.audits:
            return json.dumps({"found": False})
        rec = self.audits[audit_id]
        return json.dumps({
            "found": True,
            "audit_id": rec.audit_id,
            "verdict": rec.verdict,
            "support_level": rec.support_level,
            "confidence_label": rec.confidence_label,
            "selected_interpretation": rec.selected_interpretation,
            "reasoning_summary": rec.reasoning_summary,
            "business_risk": rec.business_risk,
            "unsupported_assumptions": rec.unsupported_assumptions,
            "evidence_digest": rec.evidence_digest,
            "final_status": rec.final_status,
        })

    @gl.public.view
    def list_recent(self, limit: int) -> str:
        out = []
        n = len(self.recent)
        cap = limit if limit > 0 else 10
        if cap > n:
            cap = n
        start = n - cap
        i = start
        while i < n:
            out.append(self.recent[i])
            i = i + 1
        return json.dumps(out)

    @gl.public.write
    def submit_audit(
        self,
        audit_id: str,
        packet_json: str,
        evidence_digest: str,
    ) -> str:
        if len(audit_id) == 0:
            raise Exception("audit_id is required")
        if len(audit_id) > 128:
            raise Exception("audit_id is too long")
        if audit_id in self.audits:
            raise Exception("audit_id has already been adjudicated")

        # Defensive: refuse packets that pre-decide the verdict.
        try:
            parsed = json.loads(packet_json)
            if isinstance(parsed, dict):
                for forbidden in (
                    "verdict",
                    "support_level",
                    "confidence_label",
                    "final_status",
                ):
                    if forbidden in parsed:
                        raise Exception(
                            "Audit packet must not pre-decide '" + forbidden + "'"
                        )
        except json.JSONDecodeError:
            # Allow non-JSON packets; validators reason over raw text.
            pass

        snapshot_packet = packet_json
        snapshot_audit_id = audit_id
        snapshot_digest = evidence_digest if len(evidence_digest) > 0 else "n/a"

        def get_input() -> str:
            return (
                "audit_id: "
                + snapshot_audit_id
                + "\nevidence_digest: "
                + snapshot_digest
                + "\naudit_packet_json:\n"
                + snapshot_packet
            )

        raw_verdict = gl.eq_principle.prompt_non_comparative(
            get_input,
            task=_VALIDATOR_TASK,
            criteria=_VALIDATOR_CRITERIA,
        )

        try:
            decision = json.loads(raw_verdict)
        except json.JSONDecodeError:
            raise Exception("validator response was not valid JSON")

        if not isinstance(decision, dict):
            raise Exception("validator response must be a JSON object")

        verdict = _trim(decision.get("verdict"), 40).lower()
        valid_verdicts = (
            "supported",
            "partially_supported",
            "unsupported",
            "misleading",
            "needs_more_evidence",
        )
        if verdict not in valid_verdicts:
            raise Exception("invalid verdict label: " + verdict)

        support_level = _trim(decision.get("support_level"), 16).lower()
        confidence_label = _trim(decision.get("confidence_label"), 16).lower()
        selected_interpretation = _trim(decision.get("selected_interpretation"), 8).upper()
        if selected_interpretation not in ("A", "B", "C", "NONE", ""):
            selected_interpretation = "NONE"

        reasoning_summary = _trim(decision.get("reasoning_summary"), 320)
        business_risk = _trim(decision.get("business_risk"), 200)
        assumptions_json = _assumptions_to_json(decision.get("unsupported_assumptions"))

        record = AuditRecord(
            audit_id=snapshot_audit_id,
            verdict=verdict,
            support_level=support_level,
            confidence_label=confidence_label,
            selected_interpretation=selected_interpretation,
            reasoning_summary=reasoning_summary,
            business_risk=business_risk,
            unsupported_assumptions=assumptions_json,
            evidence_digest=snapshot_digest,
            final_status="issued",
        )

        self.audits[snapshot_audit_id] = record
        self.recent.append(snapshot_audit_id)

        return json.dumps({
            "audit_id": snapshot_audit_id,
            "verdict": verdict,
            "support_level": support_level,
            "confidence_label": confidence_label,
            "selected_interpretation": selected_interpretation,
            "reasoning_summary": reasoning_summary,
            "business_risk": business_risk,
            "unsupported_assumptions": assumptions_json,
            "evidence_digest": snapshot_digest,
            "final_status": "issued",
        })
