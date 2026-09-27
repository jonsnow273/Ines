import { useState, useCallback, useEffect } from "react";
import type { SteeringStatus, CompareResult } from "../types/steering";

const API = "http://localhost:8000";

export function useSteering() {
  const [status, setStatus] = useState<SteeringStatus>({
    active: false,
    preset: null,
    alpha: null,
    layer: null,
    vector_norm: null,
  });
  const [loading, setLoading] = useState(false);

  const fetchStatus = useCallback(async () => {
    try {
      const res = await fetch(`${API}/api/steering/status`);
      if (res.ok) {
        const data = await res.json();
        setStatus(data);
      }
    } catch {}
  }, []);

  const setPreset = useCallback(async (preset: string, alpha: number = 1.5) => {
    setLoading(true);
    try {
      const res = await fetch(`${API}/api/steering/set`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ preset, alpha }),
      });
      if (res.ok) await fetchStatus();
    } finally {
      setLoading(false);
    }
  }, [fetchStatus]);

  const reset = useCallback(async () => {
    try {
      await fetch(`${API}/api/steering/reset`, { method: "POST" });
      await fetchStatus();
    } catch {}
  }, [fetchStatus]);

  const compare = useCallback(async (message: string, preset: string, alpha: number): Promise<CompareResult | null> => {
    setLoading(true);
    try {
      const res = await fetch(`${API}/api/steering/compare`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message, preset, alpha }),
      });
      if (res.ok) return await res.json();
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchStatus();
  }, [fetchStatus]);

  return { status, loading, setPreset, reset, compare, fetchStatus };
}
