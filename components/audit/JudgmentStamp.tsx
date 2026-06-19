export function JudgmentStamp({ label = "Validated · GenLayer Consensus" }: { label?: string }) {
  return <span className="stamp">{label}</span>;
}
