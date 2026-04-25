export class ApiError extends Error {
  status: number;
  detail: string;

  constructor(status: number, detail: string) {
    super(detail);
    this.name = "ApiError";
    this.status = status;
    this.detail = detail;
  }
}

export type AppAuthUser = {
  id: string;
  email: string;
  display_name?: string | null;
};

export type AppSettings = {
  preferred_language?: string | null;
  response_style?: string | null;
  collaboration_preference?: string | null;
  proactive_opt_in?: boolean | null;
};

export type AppMeResponse = {
  user: AppAuthUser;
  settings: AppSettings;
};

export type AppChatHistoryEntry = {
  event_id: string;
  source: string;
  summary: string;
  event_timestamp: string;
  payload?: Record<string, unknown> | null;
};

export type AppChatHistoryResponse = {
  items: AppChatHistoryEntry[];
};

export type AppChatMessageResponse = {
  event_id: string;
  trace_id: string;
  reply: {
    message: string;
    language: string;
    tone: string;
    channel: string;
  };
  runtime?: {
    role: string;
    motivation_mode: string;
    action_status: string;
    reflection_triggered: boolean;
  } | null;
};

export type AppPersonalityOverviewResponse = Record<string, unknown>;

type JsonBody = Record<string, unknown> | undefined;

async function requestJson<T>(path: string, init: RequestInit = {}, body?: JsonBody): Promise<T> {
  const response = await fetch(path, {
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
      ...(init.headers ?? {}),
    },
    ...init,
    body: body ? JSON.stringify(body) : init.body,
  });

  if (response.status === 204) {
    return undefined as T;
  }

  const text = await response.text();
  const payload = text ? JSON.parse(text) : {};

  if (!response.ok) {
    const detail =
      typeof payload?.detail === "string"
        ? payload.detail
        : `Request failed with status ${response.status}.`;
    throw new ApiError(response.status, detail);
  }

  return payload as T;
}

export const api = {
  getMe(): Promise<AppMeResponse> {
    return requestJson<AppMeResponse>("/app/me", { method: "GET" });
  },
  register(body: {
    email: string;
    password: string;
    display_name?: string;
  }): Promise<AppMeResponse> {
    return requestJson<AppMeResponse>("/app/auth/register", { method: "POST" }, body);
  },
  login(body: { email: string; password: string }): Promise<AppMeResponse> {
    return requestJson<AppMeResponse>("/app/auth/login", { method: "POST" }, body);
  },
  logout(): Promise<{ ok: boolean }> {
    return requestJson<{ ok: boolean }>("/app/auth/logout", { method: "POST" });
  },
  patchSettings(body: {
    preferred_language?: string | null;
    response_style?: string | null;
    collaboration_preference?: string | null;
    proactive_opt_in?: boolean | null;
    display_name?: string | null;
  }): Promise<AppSettings> {
    return requestJson<AppSettings>("/app/me/settings", { method: "PATCH" }, body);
  },
  getChatHistory(): Promise<AppChatHistoryResponse> {
    return requestJson<AppChatHistoryResponse>("/app/chat/history", { method: "GET" });
  },
  sendChatMessage(text: string): Promise<AppChatMessageResponse> {
    return requestJson<AppChatMessageResponse>(
      "/app/chat/message",
      { method: "POST" },
      { text },
    );
  },
  getPersonalityOverview(): Promise<AppPersonalityOverviewResponse> {
    return requestJson<AppPersonalityOverviewResponse>(
      "/app/personality/overview",
      { method: "GET" },
    );
  },
};
