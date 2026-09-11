import type { RepositoryItem } from "../data/polaris";

const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000").replace(/\/$/, "");

type RepositoryResponse = {
  items: Array<Partial<RepositoryItem> & { id: string; title: string; type: string }>;
  total: number;
};

export type AssistantSource = {
  id: string;
  title: string;
  type: string;
};

export type AssistantResponse = {
  detailedAnswer: string;
  simplifiedAnswer: string;
  usedSourceIds: string[];
  sources: AssistantSource[];
};

function normalizeRepositoryItem(item: RepositoryResponse["items"][number]): RepositoryItem {
  return {
    id: item.id,
    type: item.type as RepositoryItem["type"],
    title: item.title,
    summary: item.summary ?? "",
    year: item.year ?? 0,
    region: item.region as RepositoryItem["region"],
    topics: item.topics ?? [],
    meta: item.meta ?? "Source record",
    accent: item.accent ?? "from-cyan-300/30 via-sky-500/10 to-transparent",
    icon: item.icon ?? "▱",
  };
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...init,
    headers: { "Content-Type": "application/json", ...init?.headers },
  });

  if (!response.ok) {
    throw new Error(`API request failed (${response.status})`);
  }

  return response.json() as Promise<T>;
}

export async function getRepository(filters: {
  query?: string;
  type?: string;
  region?: string;
  year?: string;
  topic?: string;
  sort?: string;
}): Promise<{ items: RepositoryItem[]; total: number }> {
  const params = new URLSearchParams();
  if (filters.query) params.set("q", filters.query);
  if (filters.type && filters.type !== "All types") params.set("type", filters.type);
  if (filters.region && filters.region !== "All regions") params.set("region", filters.region);
  if (filters.year && filters.year !== "All years") params.set("year", filters.year);
  if (filters.topic && filters.topic !== "All topics") params.set("topics", filters.topic);
  if (filters.sort) params.set("sort", filters.sort);

  const query = params.toString();
  const result = await request<RepositoryResponse>(`/api/repository${query ? `?${query}` : ""}`);
  return { items: result.items.map(normalizeRepositoryItem), total: result.total };
}

export function queryAssistant(question: string, simplified: boolean) {
  return request<AssistantResponse>("/api/assistant/query", {
    method: "POST",
    body: JSON.stringify({ question, simplified }),
  });
}