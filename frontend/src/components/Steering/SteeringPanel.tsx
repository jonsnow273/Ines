import { useSteering } from "../../hooks/useSteering";

const PRESETS = [
  { name: "neutral", label: "Neutral", emoji: "⚖️" },
  { name: "cautious", label: "Cautious", emoji: "🛡️" },
  { name: "concise", label: "Concise", emoji: "✂️" },
  { name: "detailed", label: "Detailed", emoji: "📖" },
  { name: "creative", label: "Creative", emoji: "🎨" },
];

export function SteeringPanel() {
  const { status, loading, setPreset, reset } = useSteering();

  return (
    <div className="bg-zinc-900 border border-zinc-700 rounded-xl p-4">
      <h3 className="text-sm font-semibold text-zinc-300 mb-3">
        🎛️ Activation Steering
      </h3>

      <div className="flex flex-wrap gap-2 mb-3">
        {PRESETS.map((p) => (
          <button
            key={p.name}
            onClick={() =>
              p.name === "neutral" ? reset() : setPreset(p.name, 1.8)
            }
            disabled={loading}
            className={`px-3 py-1.5 text-xs rounded-lg border transition-colors ${
              status.preset === p.name || (p.name === "neutral" && !status.active)
                ? "bg-indigo-600 border-indigo-500 text-white"
                : "bg-zinc-800 border-zinc-600 text-zinc-400 hover:border-zinc-500"
            }`}
          >
            {p.emoji} {p.label}
          </button>
        ))}
      </div>

      <div className="text-xs text-zinc-500">
        {status.active ? (
          <span>
            Active: <span className="text-indigo-400">{status.preset}</span> |
            Layer {status.layer} | α={status.alpha}
          </span>
        ) : (
          <span>No steering active (neutral mode)</span>
        )}
      </div>
    </div>
  );
}
