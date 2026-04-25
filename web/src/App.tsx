import { startTransition, useDeferredValue, useEffect, useMemo, useState } from "react";
import {
  ApiError,
  api,
  type AppChatHistoryEntry,
  type AppMeResponse,
  type AppPersonalityOverviewResponse,
  type AppSettings,
} from "./lib/api";

type RoutePath = "/login" | "/chat" | "/settings" | "/personality";
type AuthMode = "login" | "register";
type SessionMessage =
  | { id: string; role: "user"; text: string }
  | { id: string; role: "assistant"; text: string; meta?: string };

const BUILD_REVISION = String(import.meta.env.VITE_APP_BUILD_REVISION ?? "dev");
const ROUTES: RoutePath[] = ["/chat", "/settings", "/personality"];
const ROUTE_LABELS: Record<RoutePath, string> = {
  "/login": "Login",
  "/chat": "Chat",
  "/settings": "Settings",
  "/personality": "Personality",
};

function normalizeRoute(pathname: string): RoutePath {
  if (pathname === "/settings") {
    return "/settings";
  }
  if (pathname === "/personality") {
    return "/personality";
  }
  if (pathname === "/chat" || pathname === "/") {
    return "/chat";
  }
  return "/login";
}

function navigate(path: RoutePath) {
  if (window.location.pathname !== path) {
    window.history.pushState({}, "", path);
  }
}

function formatTimestamp(value: string | undefined) {
  if (!value) {
    return "unknown time";
  }

  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return value;
  }

  return new Intl.DateTimeFormat(undefined, {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(date);
}

function prettyJson(value: unknown) {
  return JSON.stringify(value, null, 2);
}

function stringValue(value: unknown, fallback = "not set") {
  if (typeof value === "string" && value.trim()) {
    return value;
  }
  if (typeof value === "number" || typeof value === "boolean") {
    return String(value);
  }
  return fallback;
}

function routeDescription(route: RoutePath) {
  if (route === "/chat") {
    return "Main conversation surface with recent continuity and runtime-aware replies.";
  }
  if (route === "/settings") {
    return "User-owned preferences stored by backend truth, not browser-only drafts.";
  }
  if (route === "/personality") {
    return "Structured insight into identity, learned knowledge, plans, capabilities, and continuity.";
  }
  return "Authenticate into the product shell.";
}

export default function App() {
  const [route, setRoute] = useState<RoutePath>(() => normalizeRoute(window.location.pathname));
  const [authMode, setAuthMode] = useState<AuthMode>("login");
  const [authBusy, setAuthBusy] = useState(false);
  const [initializing, setInitializing] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [toast, setToast] = useState<string | null>(null);
  const [me, setMe] = useState<AppMeResponse | null>(null);
  const [history, setHistory] = useState<AppChatHistoryEntry[]>([]);
  const [historyLoading, setHistoryLoading] = useState(false);
  const [sendingMessage, setSendingMessage] = useState(false);
  const [sessionMessages, setSessionMessages] = useState<SessionMessage[]>([]);
  const [chatText, setChatText] = useState("");
  const [overview, setOverview] = useState<AppPersonalityOverviewResponse | null>(null);
  const [overviewLoading, setOverviewLoading] = useState(false);
  const [inspectorQuery, setInspectorQuery] = useState("");
  const deferredInspectorQuery = useDeferredValue(inspectorQuery);
  const [authForm, setAuthForm] = useState({
    email: "",
    password: "",
    displayName: "",
  });
  const [settingsDraft, setSettingsDraft] = useState({
    displayName: "",
    preferredLanguage: "en",
    responseStyle: "",
    collaborationPreference: "",
    proactiveOptIn: false,
  });
  const [savingSettings, setSavingSettings] = useState(false);

  useEffect(() => {
    const onPopState = () => {
      setRoute(normalizeRoute(window.location.pathname));
    };

    window.addEventListener("popstate", onPopState);
    return () => window.removeEventListener("popstate", onPopState);
  }, []);

  useEffect(() => {
    let cancelled = false;

    async function bootstrap() {
      try {
        const snapshot = await api.getMe();
        if (cancelled) {
          return;
        }
        setMe(snapshot);
        setSettingsDraft({
          displayName: snapshot.user.display_name ?? "",
          preferredLanguage: snapshot.settings.preferred_language ?? "en",
          responseStyle: snapshot.settings.response_style ?? "",
          collaborationPreference: snapshot.settings.collaboration_preference ?? "",
          proactiveOptIn: Boolean(snapshot.settings.proactive_opt_in),
        });
        if (route === "/login") {
          startTransition(() => {
            navigate("/chat");
            setRoute("/chat");
          });
        }
      } catch (caught) {
        if (cancelled) {
          return;
        }
        if (!(caught instanceof ApiError && caught.status === 401)) {
          setError(caught instanceof Error ? caught.message : "Failed to initialize session.");
        }
        startTransition(() => {
          navigate("/login");
          setRoute("/login");
        });
      } finally {
        if (!cancelled) {
          setInitializing(false);
        }
      }
    }

    void bootstrap();
    return () => {
      cancelled = true;
    };
  }, []);

  useEffect(() => {
    if (!toast) {
      return;
    }

    const timeout = window.setTimeout(() => setToast(null), 3200);
    return () => window.clearTimeout(timeout);
  }, [toast]);

  useEffect(() => {
    if (!me || route !== "/chat") {
      return;
    }

    let cancelled = false;
    setHistoryLoading(true);
    void api
      .getChatHistory()
      .then((payload) => {
        if (!cancelled) {
          setHistory(payload.items);
        }
      })
      .catch((caught) => {
        if (!cancelled) {
          setError(caught instanceof Error ? caught.message : "Failed to load chat history.");
        }
      })
      .finally(() => {
        if (!cancelled) {
          setHistoryLoading(false);
        }
      });

    return () => {
      cancelled = true;
    };
  }, [me, route]);

  useEffect(() => {
    if (!me || route !== "/personality" || overviewLoading || overview) {
      return;
    }

    let cancelled = false;
    setOverviewLoading(true);
    void api
      .getPersonalityOverview()
      .then((payload) => {
        if (!cancelled) {
          setOverview(payload);
        }
      })
      .catch((caught) => {
        if (!cancelled) {
          setError(caught instanceof Error ? caught.message : "Failed to load personality overview.");
        }
      })
      .finally(() => {
        if (!cancelled) {
          setOverviewLoading(false);
        }
      });

    return () => {
      cancelled = true;
    };
  }, [me, route, overview, overviewLoading]);

  const overviewSections = useMemo(() => {
    if (!overview) {
      return [];
    }

    const sections = [
      {
        key: "identity_state",
        title: "Identity",
        subtitle: "Profile, learned preferences, and identity policy context.",
        payload: overview.identity_state,
      },
      {
        key: "learned_knowledge",
        title: "Learned Knowledge",
        subtitle: "Semantic conclusions, affective conclusions, relations, and reflective growth.",
        payload: overview.learned_knowledge,
      },
      {
        key: "planning_state",
        title: "Planning",
        subtitle: "Goals, tasks, milestones, pending proposals, and continuity summaries.",
        payload: overview.planning_state,
      },
      {
        key: "role_skill_state",
        title: "Role + Skills",
        subtitle: "Role-policy boundaries, skill metadata, and selection visibility.",
        payload: overview.role_skill_state,
      },
      {
        key: "capability_catalog",
        title: "Capability Catalog",
        subtitle: "Approved tool families, authorization posture, and client-safe catalog truth.",
        payload: overview.capability_catalog,
      },
      {
        key: "api_readiness",
        title: "API Readiness",
        subtitle: "Backend readiness posture for first-party surfaces and future clients.",
        payload: overview.api_readiness,
      },
    ];

    const filter = deferredInspectorQuery.trim().toLowerCase();
    if (!filter) {
      return sections;
    }

    return sections.filter((section) => {
      const blob = `${section.title}\n${section.subtitle}\n${prettyJson(section.payload)}`.toLowerCase();
      return blob.includes(filter);
    });
  }, [deferredInspectorQuery, overview]);

  const planningSummary = (overview?.planning_state as Record<string, unknown> | undefined)?.continuity_summary as
    | Record<string, unknown>
    | undefined;
  const knowledgeSummary = (overview?.learned_knowledge as Record<string, unknown> | undefined)?.knowledge_summary as
    | Record<string, unknown>
    | undefined;
  const preferenceSummary = (overview?.identity_state as Record<string, unknown> | undefined)?.preference_summary as
    | Record<string, unknown>
    | undefined;

  async function refreshMe() {
    const snapshot = await api.getMe();
    setMe(snapshot);
    return snapshot;
  }

  async function handleAuthSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setAuthBusy(true);
    setError(null);

    try {
      const snapshot =
        authMode === "login"
          ? await api.login({
              email: authForm.email,
              password: authForm.password,
            })
          : await api.register({
              email: authForm.email,
              password: authForm.password,
              display_name: authForm.displayName || undefined,
            });

      setMe(snapshot);
      setSettingsDraft({
        displayName: snapshot.user.display_name ?? "",
        preferredLanguage: snapshot.settings.preferred_language ?? "en",
        responseStyle: snapshot.settings.response_style ?? "",
        collaborationPreference: snapshot.settings.collaboration_preference ?? "",
        proactiveOptIn: Boolean(snapshot.settings.proactive_opt_in),
      });
      setAuthForm({ email: authForm.email, password: "", displayName: authForm.displayName });
      setToast(authMode === "login" ? "Session restored." : "Account created and session started.");
      startTransition(() => {
        navigate("/chat");
        setRoute("/chat");
      });
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Authentication failed.");
    } finally {
      setAuthBusy(false);
    }
  }

  async function handleLogout() {
    try {
      await api.logout();
      setMe(null);
      setOverview(null);
      setHistory([]);
      setSessionMessages([]);
      setToast("Signed out.");
      startTransition(() => {
        navigate("/login");
        setRoute("/login");
      });
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Failed to sign out.");
    }
  }

  async function handleSaveSettings(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!me) {
      return;
    }

    setSavingSettings(true);
    setError(null);

    try {
      const nextSettings: AppSettings = await api.patchSettings({
        display_name: settingsDraft.displayName || null,
        preferred_language: settingsDraft.preferredLanguage || null,
        response_style: settingsDraft.responseStyle || null,
        collaboration_preference: settingsDraft.collaborationPreference || null,
        proactive_opt_in: settingsDraft.proactiveOptIn,
      });
      const freshMe = await refreshMe();
      setSettingsDraft({
        displayName: freshMe.user.display_name ?? "",
        preferredLanguage: nextSettings.preferred_language ?? "en",
        responseStyle: nextSettings.response_style ?? "",
        collaborationPreference: nextSettings.collaboration_preference ?? "",
        proactiveOptIn: Boolean(nextSettings.proactive_opt_in),
      });
      setToast("Settings saved to backend memory.");
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Failed to save settings.");
    } finally {
      setSavingSettings(false);
    }
  }

  async function handleSendMessage(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const text = chatText.trim();
    if (!text) {
      return;
    }

    setSendingMessage(true);
    setError(null);
    setSessionMessages((messages) => [
      ...messages,
      { id: `local-user-${Date.now()}`, role: "user", text },
    ]);
    setChatText("");

    try {
      const reply = await api.sendChatMessage(text);
      setSessionMessages((messages) => [
        ...messages,
        {
          id: reply.event_id,
          role: "assistant",
          text: reply.reply.message,
          meta: [
            reply.reply.language,
            reply.runtime?.role ? `role ${reply.runtime.role}` : null,
            reply.runtime?.action_status ? `action ${reply.runtime.action_status}` : null,
          ]
            .filter(Boolean)
            .join(" | "),
        },
      ]);
      const freshHistory = await api.getChatHistory();
      setHistory(freshHistory.items);
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Message delivery failed.");
    } finally {
      setSendingMessage(false);
    }
  }

  if (initializing) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-base-100 px-6 text-base-content">
        <div className="flex max-w-md flex-col items-center gap-4 rounded-[2rem] border border-base-300 bg-base-100/90 px-8 py-10 text-center shadow-halo">
          <span className="loading loading-spinner loading-lg text-primary" />
          <h1 className="font-display text-3xl text-base-900">Preparing AION Web</h1>
          <p className="text-sm leading-7 text-base-800">
            Checking your backend-owned session and loading the first-party workspace.
          </p>
        </div>
      </div>
    );
  }

  if (!me) {
    return (
      <div className="min-h-screen bg-base-100 text-base-content">
        <div className="mx-auto flex min-h-screen max-w-7xl flex-col px-6 py-8 lg:px-10">
          <header className="mb-8 overflow-hidden rounded-[2rem] border border-base-300 bg-hero-glow shadow-halo">
            <div className="grid gap-8 px-6 py-8 lg:grid-cols-[1.2fr_0.9fr] lg:px-10">
              <div className="space-y-5">
                <span className="badge badge-lg border-none bg-base-900 px-4 py-3 font-display text-signal-gold">
                  AION Web v2
                </span>
                <div className="space-y-3">
                  <h1 className="font-display text-4xl leading-tight text-base-900 md:text-6xl">
                    Dedicated product shell for the personality.
                  </h1>
                  <p className="max-w-2xl text-base leading-7 text-base-800 md:text-lg">
                    Browser auth, user settings, conversation, and deep personality inspection now sit on top of the
                    existing Python backend instead of debug-only surfaces.
                  </p>
                </div>
                <div className="flex flex-wrap gap-3">
                  <div className="badge badge-outline badge-lg">backend / web / mobile</div>
                  <div className="badge badge-outline badge-lg">first-party auth</div>
                  <div className="badge badge-outline badge-lg">daisyUI shell</div>
                </div>
              </div>

              <div className="grid gap-4 rounded-[1.5rem] border border-base-300 bg-base-100/80 p-4 backdrop-blur">
                {[
                  ["Login + Register", "Backend-owned session cookie and identity mapping."],
                  ["Chat Workspace", "Primary conversation surface with continuity."],
                  ["Inspector", "Identity, memory, plans, and capabilities."],
                ].map(([title, body]) => (
                  <div key={title} className="rounded-2xl bg-base-200 p-4">
                    <p className="font-display text-xl text-base-900">{title}</p>
                    <p className="mt-2 text-sm leading-7 text-base-800">{body}</p>
                  </div>
                ))}
              </div>
            </div>
          </header>

          <main className="grid gap-6 lg:grid-cols-[1.05fr_1.15fr]">
            <section className="rounded-[2rem] border border-base-300 bg-base-200 p-6">
              <div className="mb-6 flex items-center justify-between gap-3">
                <div>
                  <p className="text-sm uppercase tracking-[0.24em] text-base-800">Session entry</p>
                  <h2 className="font-display text-3xl text-base-900">
                    {authMode === "login" ? "Log in" : "Create account"}
                  </h2>
                </div>
                <div className="badge badge-outline">build {BUILD_REVISION.slice(0, 12)}</div>
              </div>

              <div className="tabs tabs-boxed mb-5 w-fit bg-base-100">
                <button
                  className={`tab ${authMode === "login" ? "tab-active" : ""}`}
                  onClick={() => setAuthMode("login")}
                  type="button"
                >
                  Login
                </button>
                <button
                  className={`tab ${authMode === "register" ? "tab-active" : ""}`}
                  onClick={() => setAuthMode("register")}
                  type="button"
                >
                  Register
                </button>
              </div>

              <form className="space-y-4" onSubmit={(event) => void handleAuthSubmit(event)}>
                <label className="form-control w-full">
                  <div className="label">
                    <span className="label-text text-base-900">Email</span>
                  </div>
                  <input
                    className="input input-bordered w-full"
                    type="email"
                    value={authForm.email}
                    onChange={(event) => setAuthForm((form) => ({ ...form, email: event.target.value }))}
                    placeholder="you@example.com"
                    required
                  />
                </label>

                <label className="form-control w-full">
                  <div className="label">
                    <span className="label-text text-base-900">Password</span>
                  </div>
                  <input
                    className="input input-bordered w-full"
                    type="password"
                    value={authForm.password}
                    onChange={(event) => setAuthForm((form) => ({ ...form, password: event.target.value }))}
                    placeholder="At least 8 characters"
                    required
                  />
                </label>

                {authMode === "register" ? (
                  <label className="form-control w-full">
                    <div className="label">
                      <span className="label-text text-base-900">Display name</span>
                    </div>
                    <input
                      className="input input-bordered w-full"
                      type="text"
                      value={authForm.displayName}
                      onChange={(event) => setAuthForm((form) => ({ ...form, displayName: event.target.value }))}
                      placeholder="How AION should address you"
                    />
                  </label>
                ) : null}

                <button className="btn btn-primary btn-block" disabled={authBusy} type="submit">
                  {authBusy ? "Working..." : authMode === "login" ? "Enter workspace" : "Create account"}
                </button>
              </form>

              {error ? (
                <div className="alert alert-error mt-4">
                  <span>{error}</span>
                </div>
              ) : null}
            </section>

            <section className="grid gap-4">
              {[
                {
                  title: "Auth + Settings",
                  body: "Ownable profile and preference layer backed by `/app/me` and `/app/me/settings`.",
                },
                {
                  title: "Chat",
                  body: "Main product surface for messaging the personality through `/app/chat/message`.",
                },
                {
                  title: "Personality Inspector",
                  body: "Structured sections from `/app/personality/overview` instead of raw debug endpoints.",
                },
              ].map((section) => (
                <article
                  key={section.title}
                  className="rounded-[1.75rem] border border-base-300 bg-base-100 p-6 transition-transform duration-200 hover:-translate-y-1"
                >
                  <div className="mb-3 flex items-center justify-between gap-3">
                    <h2 className="font-display text-2xl text-base-900">{section.title}</h2>
                    <span className="badge badge-outline">Live contract</span>
                  </div>
                  <p className="text-sm leading-7 text-base-800">{section.body}</p>
                </article>
              ))}
            </section>
          </main>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-base-100 text-base-content">
      <div className="mx-auto flex min-h-screen max-w-7xl flex-col px-4 py-5 sm:px-6 lg:px-10">
        <header className="mb-6 overflow-hidden rounded-[2rem] border border-base-300 bg-hero-glow shadow-halo">
          <div className="grid gap-6 px-5 py-6 lg:grid-cols-[1.3fr_0.9fr] lg:px-8">
            <div className="space-y-4">
              <div className="flex flex-wrap items-center gap-3">
                <span className="badge badge-lg border-none bg-base-900 px-4 py-3 font-display text-signal-gold">
                  AION Web
                </span>
                <span className="badge badge-outline">build {BUILD_REVISION.slice(0, 12)}</span>
              </div>
              <div>
                <h1 className="font-display text-3xl leading-tight text-base-900 md:text-5xl">
                  {ROUTE_LABELS[route]}
                </h1>
                <p className="mt-3 max-w-3xl text-sm leading-7 text-base-800 md:text-base">
                  {routeDescription(route)}
                </p>
              </div>
              <div className="flex flex-wrap gap-2">
                {ROUTES.map((entry) => (
                  <button
                    key={entry}
                    className={`btn btn-sm ${route === entry ? "btn-primary" : "btn-ghost border border-base-300"}`}
                    onClick={() => {
                      startTransition(() => {
                        navigate(entry);
                        setRoute(entry);
                      });
                    }}
                    type="button"
                  >
                    {ROUTE_LABELS[entry]}
                  </button>
                ))}
              </div>
            </div>

            <div className="grid gap-3 rounded-[1.5rem] border border-base-300 bg-base-100/80 p-4 backdrop-blur">
              <div className="rounded-2xl bg-base-200 p-4">
                <p className="text-sm uppercase tracking-[0.24em] text-base-800">Signed in as</p>
                <p className="mt-2 font-display text-2xl text-base-900">
                  {me.user.display_name || me.user.email}
                </p>
                <p className="mt-1 text-sm text-base-800">{me.user.email}</p>
              </div>
              <div className="stats bg-base-200 shadow-none">
                <div className="stat px-4 py-3">
                  <div className="stat-title">Language</div>
                  <div className="stat-value text-2xl">
                    {stringValue(me.settings.preferred_language ?? settingsDraft.preferredLanguage, "auto")}
                  </div>
                  <div className="stat-desc">backend-owned preference</div>
                </div>
                <div className="stat px-4 py-3">
                  <div className="stat-title">Proactive</div>
                  <div className="stat-value text-2xl">
                    {Boolean(me.settings.proactive_opt_in) ? "On" : "Off"}
                  </div>
                  <div className="stat-desc">user-controlled opt-in</div>
                </div>
              </div>
              <button className="btn btn-outline" onClick={() => void handleLogout()} type="button">
                Sign out
              </button>
            </div>
          </div>
        </header>

        {toast ? (
          <div className="alert alert-success mb-4">
            <span>{toast}</span>
          </div>
        ) : null}

        {error ? (
          <div className="alert alert-error mb-4">
            <span>{error}</span>
          </div>
        ) : null}

        <main className="flex-1">
          {route === "/chat" ? (
            <div className="grid gap-6 lg:grid-cols-[1.3fr_0.9fr]">
              <section className="rounded-[2rem] border border-base-300 bg-base-100 p-5 shadow-sm">
                <div className="mb-5 flex items-center justify-between gap-3">
                  <div>
                    <p className="text-sm uppercase tracking-[0.24em] text-base-800">Conversation</p>
                    <h2 className="font-display text-3xl text-base-900">Talk to the personality</h2>
                  </div>
                  <div className="badge badge-outline">cookie session</div>
                </div>

                <div className="mb-5 flex max-h-[28rem] min-h-[20rem] flex-col gap-4 overflow-y-auto rounded-[1.5rem] bg-base-200 p-4">
                  {sessionMessages.length === 0 ? (
                    <div className="rounded-2xl border border-dashed border-base-300 bg-base-100 p-5 text-sm leading-7 text-base-800">
                      Start a conversation. This panel keeps the current browser session thread, while the timeline on the
                      right shows recent backend memory entries.
                    </div>
                  ) : null}
                  {sessionMessages.map((message) => (
                    <article
                      key={message.id}
                      className={`max-w-[85%] rounded-[1.5rem] px-4 py-3 text-sm leading-7 ${
                        message.role === "user"
                          ? "ml-auto bg-base-900 text-base-100"
                          : "border border-base-300 bg-base-100 text-base-900"
                      }`}
                    >
                      <p className="mb-2 text-xs uppercase tracking-[0.22em] opacity-70">
                        {message.role === "user" ? "You" : "AION"}
                      </p>
                      <p>{message.text}</p>
                      {"meta" in message && message.meta ? (
                        <p className="mt-2 text-xs opacity-70">{message.meta}</p>
                      ) : null}
                    </article>
                  ))}
                </div>

                <form className="space-y-3" onSubmit={(event) => void handleSendMessage(event)}>
                  <textarea
                    className="textarea textarea-bordered h-32 w-full"
                    placeholder="Send a message to AION..."
                    value={chatText}
                    onChange={(event) => setChatText(event.target.value)}
                  />
                  <div className="flex flex-wrap items-center justify-between gap-3">
                    <p className="text-sm text-base-800">
                      Replies are generated by the existing backend runtime via `/app/chat/message`.
                    </p>
                    <button className="btn btn-primary" disabled={sendingMessage} type="submit">
                      {sendingMessage ? "Sending..." : "Send message"}
                    </button>
                  </div>
                </form>
              </section>

              <aside className="rounded-[2rem] border border-base-300 bg-base-200 p-5">
                <div className="mb-4 flex items-center justify-between gap-3">
                  <div>
                    <p className="text-sm uppercase tracking-[0.24em] text-base-800">Continuity</p>
                    <h2 className="font-display text-2xl text-base-900">Recent memory timeline</h2>
                  </div>
                  {historyLoading ? <span className="loading loading-dots loading-sm text-primary" /> : null}
                </div>

                <div className="space-y-3">
                  {history.length === 0 ? (
                    <div className="rounded-2xl bg-base-100 p-4 text-sm text-base-800">
                      No persisted conversation events yet.
                    </div>
                  ) : null}
                  {history.map((item) => (
                    <article key={item.event_id} className="rounded-2xl bg-base-100 p-4 text-sm shadow-sm">
                      <div className="mb-2 flex items-center justify-between gap-2">
                        <span className="badge badge-outline">{item.source}</span>
                        <span className="text-xs text-base-800">{formatTimestamp(item.event_timestamp)}</span>
                      </div>
                      <p className="font-semibold text-base-900">{item.summary}</p>
                      {item.payload ? (
                        <details className="collapse collapse-arrow mt-3 rounded-box border border-base-300 bg-base-100">
                          <summary className="collapse-title min-h-0 px-4 py-3 text-sm font-medium text-base-900">
                            Event payload
                          </summary>
                          <div className="collapse-content px-4 pb-4">
                            <pre className="overflow-x-auto rounded-xl bg-base-200 p-3 text-xs leading-6 text-base-900">
                              {prettyJson(item.payload)}
                            </pre>
                          </div>
                        </details>
                      ) : null}
                    </article>
                  ))}
                </div>
              </aside>
            </div>
          ) : null}

          {route === "/settings" ? (
            <div className="grid gap-6 lg:grid-cols-[1.05fr_0.95fr]">
              <section className="rounded-[2rem] border border-base-300 bg-base-100 p-5 shadow-sm">
                <div className="mb-6">
                  <p className="text-sm uppercase tracking-[0.24em] text-base-800">User settings</p>
                  <h2 className="font-display text-3xl text-base-900">Preference ownership</h2>
                </div>

                <form className="grid gap-4" onSubmit={(event) => void handleSaveSettings(event)}>
                  <label className="form-control">
                    <div className="label">
                      <span className="label-text text-base-900">Display name</span>
                    </div>
                    <input
                      className="input input-bordered"
                      value={settingsDraft.displayName}
                      onChange={(event) =>
                        setSettingsDraft((draft) => ({ ...draft, displayName: event.target.value }))
                      }
                    />
                  </label>

                  <label className="form-control">
                    <div className="label">
                      <span className="label-text text-base-900">Preferred language</span>
                    </div>
                    <select
                      className="select select-bordered"
                      value={settingsDraft.preferredLanguage}
                      onChange={(event) =>
                        setSettingsDraft((draft) => ({ ...draft, preferredLanguage: event.target.value }))
                      }
                    >
                      <option value="en">English</option>
                      <option value="pl">Polish</option>
                      <option value="de">German</option>
                    </select>
                  </label>

                  <label className="form-control">
                    <div className="label">
                      <span className="label-text text-base-900">Response style</span>
                    </div>
                    <input
                      className="input input-bordered"
                      placeholder="concise, reflective, direct..."
                      value={settingsDraft.responseStyle}
                      onChange={(event) =>
                        setSettingsDraft((draft) => ({ ...draft, responseStyle: event.target.value }))
                      }
                    />
                  </label>

                  <label className="form-control">
                    <div className="label">
                      <span className="label-text text-base-900">Collaboration preference</span>
                    </div>
                    <input
                      className="input input-bordered"
                      placeholder="hands-on, strategic, coaching..."
                      value={settingsDraft.collaborationPreference}
                      onChange={(event) =>
                        setSettingsDraft((draft) => ({
                          ...draft,
                          collaborationPreference: event.target.value,
                        }))
                      }
                    />
                  </label>

                  <label className="label cursor-pointer justify-start gap-3 rounded-2xl border border-base-300 bg-base-200 px-4 py-4">
                    <input
                      className="toggle toggle-primary"
                      type="checkbox"
                      checked={settingsDraft.proactiveOptIn}
                      onChange={(event) =>
                        setSettingsDraft((draft) => ({ ...draft, proactiveOptIn: event.target.checked }))
                      }
                    />
                    <div>
                      <span className="label-text text-base-900">Allow proactive follow-ups</span>
                      <p className="mt-1 text-sm text-base-800">
                        This writes a user-owned preference into backend conclusions, not just browser state.
                      </p>
                    </div>
                  </label>

                  <button className="btn btn-primary w-full sm:w-fit" disabled={savingSettings} type="submit">
                    {savingSettings ? "Saving..." : "Save settings"}
                  </button>
                </form>
              </section>

              <aside className="rounded-[2rem] border border-base-300 bg-base-200 p-5">
                <div className="mb-4">
                  <p className="text-sm uppercase tracking-[0.24em] text-base-800">Current backend snapshot</p>
                  <h2 className="font-display text-2xl text-base-900">Resolved values</h2>
                </div>
                <div className="grid gap-3">
                  {[
                    ["Display name", me.user.display_name || "not set"],
                    ["Preferred language", me.settings.preferred_language || "not set"],
                    ["Response style", me.settings.response_style || "not set"],
                    ["Collaboration preference", me.settings.collaboration_preference || "not set"],
                    ["Proactive opt-in", Boolean(me.settings.proactive_opt_in) ? "enabled" : "disabled"],
                  ].map(([label, value]) => (
                    <div key={label} className="rounded-2xl bg-base-100 p-4">
                      <p className="text-xs uppercase tracking-[0.18em] text-base-800">{label}</p>
                      <p className="mt-2 text-base font-semibold text-base-900">{value}</p>
                    </div>
                  ))}
                </div>
              </aside>
            </div>
          ) : null}

          {route === "/personality" ? (
            <div className="grid gap-6">
              <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
                {[
                  {
                    title: "Goals",
                    value: stringValue(planningSummary?.active_goal_count, "0"),
                    note: "active goals in planning continuity",
                  },
                  {
                    title: "Tasks",
                    value: stringValue(planningSummary?.active_task_count, "0"),
                    note: "current tracked task count",
                  },
                  {
                    title: "Knowledge",
                    value: stringValue(knowledgeSummary?.semantic_conclusion_count, "0"),
                    note: "semantic conclusions stored",
                  },
                  {
                    title: "Preferences",
                    value: stringValue(preferenceSummary?.learned_preference_count, "0"),
                    note: "resolved preference keys",
                  },
                ].map((card) => (
                  <article key={card.title} className="rounded-[1.75rem] border border-base-300 bg-base-100 p-5 shadow-sm">
                    <p className="text-sm uppercase tracking-[0.22em] text-base-800">{card.title}</p>
                    <p className="mt-3 font-display text-4xl text-base-900">{card.value}</p>
                    <p className="mt-2 text-sm text-base-800">{card.note}</p>
                  </article>
                ))}
              </section>

              <section className="rounded-[2rem] border border-base-300 bg-base-100 p-5 shadow-sm">
                <div className="mb-5 flex flex-wrap items-end justify-between gap-4">
                  <div>
                    <p className="text-sm uppercase tracking-[0.24em] text-base-800">Inspector</p>
                    <h2 className="font-display text-3xl text-base-900">All major personality sections</h2>
                  </div>
                  <label className="input input-bordered flex w-full items-center gap-2 sm:max-w-sm">
                    <input
                      className="grow"
                      placeholder="Filter sections or payload text"
                      value={inspectorQuery}
                      onChange={(event) => setInspectorQuery(event.target.value)}
                    />
                  </label>
                </div>

                {overviewLoading ? (
                  <div className="flex items-center gap-3 rounded-2xl bg-base-200 px-4 py-5 text-base-900">
                    <span className="loading loading-spinner loading-sm text-primary" />
                    Loading personality overview from backend.
                  </div>
                ) : null}

                {!overviewLoading && overviewSections.length === 0 ? (
                  <div className="rounded-2xl bg-base-200 px-4 py-5 text-sm text-base-800">
                    No matching inspector sections for this filter.
                  </div>
                ) : null}

                <div className="grid gap-4 lg:grid-cols-2">
                  {overviewSections.map((section) => (
                    <article key={section.key} className="rounded-[1.6rem] border border-base-300 bg-base-200 p-4">
                      <div className="mb-3 flex items-center justify-between gap-3">
                        <div>
                          <h3 className="font-display text-2xl text-base-900">{section.title}</h3>
                          <p className="mt-1 text-sm leading-7 text-base-800">{section.subtitle}</p>
                        </div>
                        <span className="badge badge-outline">{section.key}</span>
                      </div>
                      <pre className="max-h-[24rem] overflow-auto rounded-2xl bg-base-100 p-4 text-xs leading-6 text-base-900">
                        {prettyJson(section.payload)}
                      </pre>
                    </article>
                  ))}
                </div>
              </section>
            </div>
          ) : null}
        </main>
      </div>
    </div>
  );
}
