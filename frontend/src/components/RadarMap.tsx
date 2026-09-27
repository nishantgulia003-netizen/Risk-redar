export function RadarMap({ route }: { route?: number[][] }) {
  const points = route?.length
    ? route
        .map(
          (_, i) =>
            `${38 + i * (280 / Math.max(1, route.length - 1))},${
              228 - i * (154 / Math.max(1, route.length - 1))
            }`
        )
        .join(" ")
    : "42,222 115,190 158,143 238,96 318,55";

  return (
    <div className="glass-surface-elevated reveal relative h-72 overflow-hidden rounded-glass border-white/10 p-0 shadow-glass">
      <svg viewBox="0 0 360 288" className="h-full w-full">
        <defs>
          <pattern id="radar-grid" width="26" height="26" patternUnits="userSpaceOnUse">
            <path d="M26 0H0V26" fill="none" stroke="#251E22" strokeWidth="0.75" />
          </pattern>
          <linearGradient id="radar-sweep" x1="0" x2="1">
            <stop stopColor="#EF2E4B" stopOpacity="0.25" />
            <stop offset="1" stopColor="#EF2E4B" stopOpacity="0" />
          </linearGradient>
          <filter id="radar-glow">
            <feGaussianBlur stdDeviation="3" result="blur" />
            <feMerge>
              <feMergeNode in="blur" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>
        </defs>

        <rect width="360" height="288" fill="url(#radar-grid)" />
        <circle cx="180" cy="144" r="46" fill="none" stroke="#3D2930" strokeDasharray="3 3" />
        <circle cx="180" cy="144" r="94" fill="none" stroke="#3D2930" strokeDasharray="4 4" />
        <circle cx="180" cy="144" r="130" fill="none" stroke="#2B1D22" />

        {/* Sweeping Radar Beam */}
        <g style={{ transformOrigin: "180px 144px", animation: "radar-sweep 6s linear infinite" }}>
          <path d="M180 144 L318 66 A158 158 0 0 0 180 -14Z" fill="url(#radar-sweep)" />
        </g>

        <line x1="180" x2="180" y1="18" y2="270" stroke="#3D2930" strokeDasharray="2 5" />
        <line x1="24" x2="336" y1="144" y2="144" stroke="#3D2930" strokeDasharray="2 5" />

        {/* Route Vectors in Dark Red / Bright Red theme */}
        <polyline
          points={points}
          fill="none"
          stroke="#EF2E4B"
          strokeWidth="3.5"
          strokeLinecap="round"
          filter="url(#radar-glow)"
        />
        <polyline
          points={points}
          fill="none"
          stroke="#FFFFFF"
          strokeWidth="1"
          strokeDasharray="3 6"
          opacity="0.8"
        />

        <circle cx="42" cy="222" r="5" fill="#EF2E4B" />
        <circle
          cx="318"
          cy="55"
          r="9"
          fill="none"
          stroke="#FF4964"
          style={{ animation: "beacon 1.6s ease-in-out infinite" }}
        />
        <circle cx="318" cy="55" r="4" fill="#FF4964" />
      </svg>

      <div className="absolute left-4 top-4 rounded-full bg-black/60 px-3 py-1 font-hud text-[10px] uppercase tracking-wider text-bright-red backdrop-blur-md border border-primary-red/30">
        ◉ Tactical Vector Active
      </div>
      <div className="absolute bottom-4 left-4 text-white">
        <p className="hud-label text-muted-text">Live prediction</p>
        <b className="text-sm font-bold tracking-tight">Safe corridor established</b>
      </div>
    </div>
  );
}
