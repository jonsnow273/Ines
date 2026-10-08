import { useRef, useEffect } from "react";
import type { Message } from "../../types/chat";
import { MessageBubble } from "./MessageBubble";
import { TypingIndicator } from "./TypingIndicator";

interface Props {
  messages: Message[];
  loading: boolean;
}

export function ChatWindow({ messages, loading }: Props) {
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  return (
    <div className="flex-1 overflow-y-auto px-4 py-6">
      <div className="max-w-4xl mx-auto">
        {messages.length === 0 && (
          <div className="text-center text-zinc-500 mt-20">
            <h2 className="text-2xl font-bold text-zinc-300 mb-2">Megan</h2>
            <p className="text-sm">The first local AI assistant with controllable behavior.</p>
            <p className="text-xs mt-4 text-zinc-600">Type a message to start chatting.</p>
          </div>
        )}
        {messages.map((msg) => (
          <MessageBubble key={msg.id} message={msg} />
        ))}
        {loading && <TypingIndicator />}
        <div ref={bottomRef} />
      </div>
    </div>
  );
}
