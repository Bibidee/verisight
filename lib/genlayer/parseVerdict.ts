export type VeriSightConsensusVerdict = {
  verdict: string;
  support_level: string;
  confidence_label: string;
  selected_interpretation: string;
  reasoning_summary: string;
  unsupported_assumptions: string[];
  business_risk: string;
};

export function parseGenLayerReturn(raw: unknown): VeriSightConsensusVerdict | null {
  if (!raw) return null;

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  let value: any = raw;

  if (typeof value === "object" && value !== null && "Return" in value) {
    value = (value as Record<string, unknown>).Return;
  }
  if (typeof value === "object" && value !== null && "return" in value) {
    value = (value as Record<string, unknown>).return;
  }

  for (let i = 0; i < 2; i++) {
    if (typeof value === "string") {
      try {
        value = JSON.parse(value);
      } catch {
        break;
      }
    }
  }

  if (!value || typeof value !== "object") return null;

  const obj = value as Record<string, unknown>;

  if (!obj.verdict) return null;

  let assumptions: string[] = [];
  const rawAssumptions = obj.unsupported_assumptions;
  if (typeof rawAssumptions === "string") {
    try {
      const parsed = JSON.parse(rawAssumptions);
      if (Array.isArray(parsed)) {
        assumptions = parsed.map(String);
      }
    } catch {
      assumptions = [rawAssumptions];
    }
  } else if (Array.isArray(rawAssumptions)) {
    assumptions = rawAssumptions.map(String);
  }

  return {
    verdict: String(obj.verdict || ""),
    support_level: String(obj.support_level || ""),
    confidence_label: String(obj.confidence_label || ""),
    selected_interpretation: String(obj.selected_interpretation || ""),
    reasoning_summary: String(obj.reasoning_summary || ""),
    unsupported_assumptions: assumptions,
    business_risk: String(obj.business_risk || ""),
  };
}
