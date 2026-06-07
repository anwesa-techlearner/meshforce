'use client';
import { useEffect, useCallback } from 'react';

const QUEUE_KEY = 'meshforce_offline_queue';

interface QueuedItem {
  id: string;
  url: string;
  method: string;
  body: unknown;
  timestamp: number;
}

function getQueue(): QueuedItem[] {
  if (typeof window === 'undefined') return [];
  try {
    return JSON.parse(localStorage.getItem(QUEUE_KEY) || '[]');
  } catch {
    return [];
  }
}

function saveQueue(queue: QueuedItem[]): void {
  localStorage.setItem(QUEUE_KEY, JSON.stringify(queue));
}

export function useOfflineQueue() {
  const enqueue = useCallback((url: string, method: string, body: unknown) => {
    const queue = getQueue();
    queue.push({ id: `${Date.now()}-${Math.random()}`, url, method, body, timestamp: Date.now() });
    saveQueue(queue);
  }, []);

  const flushQueue = useCallback(async () => {
    const queue = getQueue();
    if (queue.length === 0) return;
    const remaining: QueuedItem[] = [];
    for (const item of queue) {
      try {
        const res = await fetch(item.url, {
          method: item.method,
          headers: { 'Content-Type': 'application/json' },
          body: item.body ? JSON.stringify(item.body) : undefined,
        });
        if (!res.ok) remaining.push(item);
      } catch {
        remaining.push(item);
      }
    }
    saveQueue(remaining);
  }, []);

  useEffect(() => {
    const handleOnline = () => flushQueue();
    window.addEventListener('online', handleOnline);
    if (navigator.onLine) flushQueue();
    return () => window.removeEventListener('online', handleOnline);
  }, [flushQueue]);

  return { enqueue, flushQueue };
}
