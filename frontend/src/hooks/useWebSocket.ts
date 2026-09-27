// WebSocket hook placeholder — will be used for streaming responses
export function useWebSocket() {
  return {
    connected: false,
    send: (_msg: string) => {},
  };
}
