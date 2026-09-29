import { useChat } from "./hooks/useChat";
import { Header } from "./components/Layout/Header";
import { ChatWindow } from "./components/Chat/ChatWindow";
import { InputBar } from "./components/Chat/InputBar";
import { SteeringPanel } from "./components/Steering/SteeringPanel";

export default function App() {
  const { messages, loading, error, sessionId, sendMessage, clearChat } = useChat();

  return (
    <div className="flex flex-col h-screen bg-zinc-950 text-zinc-100">
      <Header sessionId={sessionId} onClear={clearChat} />

      <div className="flex flex-1 overflow-hidden">
        {/* Main chat area */}
        <div className="flex flex-col flex-1">
          <ChatWindow messages={messages} loading={loading} />

          {error && (
            <div className="px-4 py-2 bg-red-900/30 border-t border-red-800 text-red-400 text-xs text-center">
              {error} — Is the API server running? (uvicorn api.server:app --port 8000)
            </div>
          )}

          <InputBar onSend={sendMessage} disabled={loading} />
        </div>

        {/* Right sidebar — steering controls */}
        <div className="hidden lg:block w-80 border-l border-zinc-700 p-4 overflow-y-auto bg-zinc-950">
          <SteeringPanel />

          <div className="mt-6 text-xs text-zinc-600 space-y-2">
            <p className="font-semibold text-zinc-500">Quick Guide</p>
            <p>Select a preset to change Ines's behavior in real-time using activation steering.</p>
            <p><strong>Concise</strong> — shorter, direct answers</p>
            <p><strong>Detailed</strong> — thorough explanations</p>
            <p><strong>Creative</strong> — more imaginative responses</p>
            <p><strong>Cautious</strong> — safety-first, careful answers</p>
          </div>
        </div>
      </div>
    </div>
  );
}
