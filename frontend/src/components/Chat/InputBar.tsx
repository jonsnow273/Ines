import { useState, useRef, useEffect } from "react";

interface Props {
  onSend: (message: string) => void;
  disabled: boolean;
}

export function InputBar({ onSend, disabled }: Props) {
  const [text, setText] = useState("");
  const inputRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    if (!disabled) inputRef.current?.focus();
  }, [disabled]);

  const handleSend = () => {
    const trimmed = text.trim();
    if (!trimmed || disabled) return;
    onSend(trimmed);
    setText("");
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="border-t border-zinc-700 p-4 bg-zinc-900">
      <div className="flex gap-3 items-end max-w-4xl mx-auto">
        <textarea
          ref={inputRef}
          value={text}
          onChange={(e) => setText(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={disabled ? "Megan is thinking..." : "Type a message..."}
          disabled={disabled}
          rows={1}
          className="flex-1 bg-zinc-800 text-zinc-100 border border-zinc-600 rounded-xl px-4 py-3 resize-none focus:outline-none focus:border-indigo-500 disabled:opacity-50 placeholder-zinc-500"
        />
        <button
          onClick={handleSend}
          disabled={disabled || !text.trim()}
          className="bg-indigo-600 hover:bg-indigo-500 disabled:bg-zinc-700 disabled:text-zinc-500 text-white px-5 py-3 rounded-xl font-medium transition-colors"
        >
          Send
        </button>
      </div>
    </div>
  );
}
