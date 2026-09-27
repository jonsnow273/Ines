import type { Message } from "../../types/chat";

interface Props {
  message: Message;
}

export function MessageBubble({ message }: Props) {
  const isUser = message.role === "user";

  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"} mb-3`}>
      <div
        className={`max-w-[75%] px-4 py-3 rounded-2xl text-sm leading-relaxed ${
          isUser
            ? "bg-indigo-600 text-white rounded-br-md"
            : "bg-zinc-800 text-zinc-100 rounded-bl-md border border-zinc-700"
        }`}
      >
        {!isUser && (
          <div className="text-xs text-indigo-400 font-semibold mb-1">Sephora</div>
        )}
        <div className="whitespace-pre-wrap">{message.content}</div>
      </div>
    </div>
  );
}
