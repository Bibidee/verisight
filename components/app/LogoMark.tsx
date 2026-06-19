export function LogoMark({ size = 30 }: { size?: number }) {
  return (
    <svg viewBox="0 0 32 32" width={size} height={size} aria-hidden>
      <defs>
        <linearGradient id="vsg-mark" x1="0" x2="1" y1="0" y2="1">
          <stop offset="0" stopColor="#2563EB" />
          <stop offset="1" stopColor="#7C3AED" />
        </linearGradient>
      </defs>
      <rect x="1" y="1" width="30" height="30" rx="7" fill="#FFFFFF" stroke="url(#vsg-mark)" strokeWidth="1.4" />
      <g stroke="#94A3B8" strokeWidth="0.9">
        <line x1="6" y1="10" x2="26" y2="10" />
        <line x1="6" y1="14" x2="26" y2="14" />
        <line x1="6" y1="18" x2="26" y2="18" />
        <line x1="6" y1="22" x2="26" y2="22" />
      </g>
      <path d="M10 18 L14 22 L23 11" stroke="#7C3AED" strokeWidth="2.1" fill="none" strokeLinecap="round" strokeLinejoin="round" />
      <circle cx="23" cy="11" r="1.8" fill="#7C3AED" />
    </svg>
  );
}
