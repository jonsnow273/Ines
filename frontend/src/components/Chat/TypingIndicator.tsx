export function TypingIndicator() {
  return (
    <div className="flex justify-start mb-3">
      <div className="bg-zinc-800 border border-zinc-700 rounded-2xl rounded-bl-md px-4 py-3">
        <div className="flex gap-1 items-center">
          <div className="text-xs text-indigo-400 font-semibold mr-2">Sephora</div>
          <span className="w-2 h-2 bg-zinc-500 rounded-full animate-bounce" style={{ animationDelay: "0ms" }} />
          <span className="w-2 h-2 bg-zinc-500 rounded-full animate-bounce" style={{ animationDelay: "150ms" }} />
          <span className="w-2 h-2 bg-zinc-500 rounded-full animate-bounce" style={{ animationDelay: "300ms" }} />
        </div>
      </div>
    </div>
  );
}
