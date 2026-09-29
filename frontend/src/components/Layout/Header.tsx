interface Props {
  sessionId: string | null;
  onClear: () => void;
}

export function Header({ sessionId, onClear }: Props) {
  return (
    <header className="border-b border-zinc-700 bg-zinc-900 px-6 py-3 flex items-center justify-between">
      <div className="flex items-center gap-3">
        <h1 className="text-lg font-bold text-white">🧠 Ines</h1>
        <span className="text-xs text-zinc-500 hidden sm:inline">
          Local AI Assistant with Controllable Behavior
        </span>
      </div>
      <div className="flex items-center gap-4">
        {sessionId && (
          <span className="text-xs text-zinc-600 font-mono">
            {sessionId.slice(0, 15)}...
          </span>
        )}
        <button
          onClick={onClear}
          className="text-xs text-zinc-500 hover:text-zinc-300 transition-colors"
        >
          New Chat
        </button>
      </div>
    </header>
  );
}
