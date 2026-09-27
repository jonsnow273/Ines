// Voice hook placeholder — will be implemented with WebSocket audio streaming
export function useVoice() {
  return {
    isListening: false,
    isAvailable: false,
    startListening: () => {},
    stopListening: () => {},
  };
}
