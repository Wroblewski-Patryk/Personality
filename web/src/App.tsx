import { startTransition, useEffect, useMemo, useRef, useState, type ReactNode } from "react";
import {
  ApiError,
  api,
  type AppChatHistoryEntry,
  type AppMeResponse,
  type AppPersonalityOverviewResponse,
  type AppResetDataResponse,
  type AppSettings,
  type AppTelegramLinkStartResponse,
  type AppToolsOverviewResponse,
} from "./lib/api";

type RoutePath = "/login" | "/dashboard" | "/chat" | "/settings" | "/personality" | "/tools";
type AuthMode = "login" | "register";
type UiLanguageCode = "system" | "en" | "pl" | "de";
type ResolvedUiLanguageCode = Exclude<UiLanguageCode, "system">;
type UtcOffsetOption = {
  value: string;
  label: string;
};

const BUILD_REVISION = String(import.meta.env.VITE_APP_BUILD_REVISION ?? "dev");
const RESET_DATA_CONFIRMATION_TEXT = "RESET MY DATA";
const ROUTES: RoutePath[] = ["/dashboard", "/chat", "/personality", "/tools", "/settings"];
const UI_LANGUAGE_OPTIONS: Array<{
  value: UiLanguageCode;
  iconToken: string;
  nativeLabel: string;
  label: Record<ResolvedUiLanguageCode, string>;
  fallbackLabel: ResolvedUiLanguageCode | "browser";
}> = [
  {
    value: "system",
    iconToken: "AUTO",
    nativeLabel: "System",
    label: { en: "System default", pl: "Domyślne systemu", de: "Systemstandard" },
    fallbackLabel: "browser",
  },
  {
    value: "en",
    iconToken: "EN",
    nativeLabel: "English",
    label: { en: "English", pl: "Angielski", de: "Englisch" },
    fallbackLabel: "en",
  },
  {
    value: "pl",
    iconToken: "PL",
    nativeLabel: "Polski",
    label: { en: "Polish", pl: "Polski", de: "Polnisch" },
    fallbackLabel: "pl",
  },
  {
    value: "de",
    iconToken: "DE",
    nativeLabel: "Deutsch",
    label: { en: "German", pl: "Niemiecki", de: "Deutsch" },
    fallbackLabel: "de",
  },
];

const UTC_OFFSET_OPTIONS: UtcOffsetOption[] = Array.from({ length: 105 }, (_, index) => {
  const totalMinutes = -12 * 60 + index * 15;
  const sign = totalMinutes >= 0 ? "+" : "-";
  const absoluteMinutes = Math.abs(totalMinutes);
  const hours = Math.floor(absoluteMinutes / 60);
  const minutes = absoluteMinutes % 60;
  const value = `UTC${sign}${String(hours).padStart(2, "0")}:${String(minutes).padStart(2, "0")}`;
  return {
    value,
    label: `(UTC${sign}${String(hours).padStart(2, "0")}:${String(minutes).padStart(2, "0")})`,
  };
});

const UI_COPY = {
  en: {
    routes: {
      "/login": "Login",
      "/dashboard": "Dashboard",
      "/chat": "Chat",
      "/settings": "Settings",
      "/tools": "Tools",
      "/personality": "Personality",
    } satisfies Record<RoutePath, string>,
    routeDescriptions: {
      "/login": "Authenticate into the product shell.",
      "/dashboard": "Flagship overview of your current goals, signals, flow, and next best actions.",
      "/chat": "One shared conversation thread with your latest exchanged messages and fresh replies from the personality.",
      "/settings": "Profile, interface language, and proactive preferences in one clear place.",
      "/tools": "See what is ready, what needs attention, and what you can use next.",
      "/personality": "Product-facing overview of identity, knowledge, planning, and capabilities.",
    } satisfies Record<RoutePath, string>,
    common: {
      workspace: "Workspace",
      currentSurface: "Current surface",
      account: "Account",
      signedInAs: "Signed in as",
      signOut: "Sign out",
      build: "build",
      uiLanguage: "UI language",
      utcOffset: "UTC offset",
      conversationLanguage: "Conversation language",
      proactive: "Proactive",
      on: "On",
      off: "Off",
      save: "Save settings",
      saving: "Saving...",
      loading: "Loading...",
      interfaceOnly: "Interface only",
      details: "Details",
      inspectPayload: "View details",
      noData: "No data yet.",
      user: "You",
      assistant: "Presence",
      sourceOfTruth: "Current value",
      notSet: "not set",
      system: "System",
      stateLoadingTitle: "Getting things ready",
      stateEmptyTitle: "Nothing to show yet",
      stateSuccessTitle: "Done",
      stateErrorTitle: "Something needs attention",
      stateDetailLabel: "Details",
    },
    auth: {
      badge: "Aviary",
      heroTitle: "A calmer place to continue the conversation.",
      heroBody:
        "Sign in to pick up where you left off, adjust your preferences, and keep Aviary close without digging through setup screens.",
      sessionEntry: "Session entry",
      trustTitle: "What you can expect",
      login: "Log in",
      register: "Create account",
      email: "Email",
      password: "Password",
      displayName: "Display name",
      enterWorkspace: "Enter workspace",
      createAccount: "Create account",
      tabsLogin: "Login",
      tabsRegister: "Register",
      trustCards: [
        {
          title: "Fast return to your workspace",
          body: "Your chat, settings, and linked tools stay one sign-in away.",
        },
        {
          title: "A clear place to manage preferences",
          body: "Profile details, language, and proactive follow-ups stay easy to reach.",
        },
        {
          title: "Built for privacy and control",
          body: "You can reset runtime continuity later without deleting the account itself.",
        },
      ],
    },
    dashboard: {
      eyebrow: "Dashboard",
      title: "Your living overview",
      subtitle: "A calm flagship surface for goals, guidance, memory, and the embodied flow behind your next move.",
    },
    chat: {
      eyebrow: "Conversation",
      title: "Talk to the personality",
      subtitle: "See the latest shared conversation first, whether the recent turns came from the app or a linked channel.",
      emptyThread:
        "Start the conversation here. New turns will appear in this shared thread as soon as they are exchanged.",
      placeholder: "Send a message...",
      composerHint: "Replies land back in this same transcript, so you can stay focused on one conversation.",
      send: "Send message",
      sending: "Sending...",
      thread: "Thread",
      latestMessages: "Latest messages",
      noHistory: "No shared messages yet.",
      transcriptCount: "Transcript items",
      activeChannel: "Recent channels",
      latestLanguage: "Live language",
      messageDetails: "Message details",
      channel: "Channel",
      pending: "Sending now",
    },
    settings: {
      eyebrow: "Settings",
      title: "Personalize the shell",
      subtitle: "Short, mobile-first settings focused on your profile, interface language, and proactive follow-ups.",
      profileTitle: "Profile",
      profileBody: "Choose how the shell identifies you.",
      uiLanguageTitle: "Interface language",
      uiLanguageBody: "Changes labels, copy, and navigation in the app shell only.",
      uiLanguageHelp: "This does not control the language used inside the conversation itself.",
      utcOffsetTitle: "Local time offset",
      utcOffsetBody: "Sets the explicit UTC offset used when the runtime reasons about the current date and time for your profile.",
      utcOffsetHelp: "Choose the offset that matches your current place, for example Switzerland or Poland in winter is usually UTC+01:00.",
      conversationTitle: "Conversation language",
      conversationBody: "The conversation adapts live from context, history, and the current exchange.",
      proactiveTitle: "Proactive follow-ups",
      proactiveBody: "Let Aviary send occasional follow-ups when your account settings allow it.",
      saveHint: "Save your changes when you are ready.",
      conversationRuntimeOwned: "Adaptive and context-aware",
      savedState: "Ready to save",
      resetTitle: "Reset runtime data",
      resetBody:
        "Clear learned runtime continuity, memory, planning state, and queue state for this account without deleting the account or reconfiguring linked tools.",
      resetImpact:
        "This keeps your profile, UI settings, proactive preference, and linked integrations, then revokes every active session including this one.",
      resetConfirmationLabel: "Confirmation text",
      resetConfirmationHint: "Type the exact phrase below to unlock the reset action.",
      resetConfirmationPlaceholder: "RESET MY DATA",
      resetAction: "Reset my runtime data",
      resetting: "Resetting...",
      resetSuccess: "Runtime data reset. Sign in again to start fresh.",
    },
    tools: {
      eyebrow: "Tools",
      title: "Ready tools and channels",
      subtitle: "See what is available now, what needs action, and what is still blocked.",
      groupCount: "Tool groups",
      integral: "Always on",
      ready: "Ready now",
      linkRequired: "Needs linking",
      loading: "Loading your tools overview.",
      empty: "Your tools overview will appear here.",
      currentStatus: "Current status",
      nextStep: "Next step",
      technicalDetails: "Technical details",
      availability: "Availability",
      provider: "Provider",
      control: "Control",
      linkState: "Link state",
      readOnly: "Read only",
      enabledByUser: "Enabled by you",
      disabledByUser: "Disabled by you",
      saving: "Saving...",
      noAction: "No action needed.",
      telegramLinking: "Telegram linking",
      generateCode: "Generate code",
      rotateCode: "Rotate code",
      generating: "Generating...",
      linkCode: "Link code",
      instruction: "Instruction",
      noLinkCode: "No active link code yet. Generate one when you are ready to confirm the chat.",
      capabilities: "Capabilities",
    },
    personality: {
      eyebrow: "Personality",
      title: "Personality overview",
      subtitle: "High-level insight first, with extra detail available only when you want it.",
      goals: "Goals",
      tasks: "Tasks",
      knowledge: "Knowledge",
      preferences: "Preferences",
      filter: "Filter sections",
      loading: "Loading personality overview.",
      empty: "No matching overview sections for this filter.",
      highlights: "Highlights",
    },
  },
  pl: {
    routes: { "/login": "Logowanie", "/chat": "Czat", "/settings": "Ustawienia", "/tools": "Narzędzia", "/personality": "Osobowość" },
    routeDescriptions: {
      "/login": "Zaloguj się do powłoki produktu.",
      "/chat": "Jeden wspólny wątek rozmowy z ostatnimi wiadomościami i świeżymi odpowiedziami osobowości.",
      "/settings": "Profil, język interfejsu i proaktywność w jednym prostym miejscu.",
      "/tools": "Zobacz, co jest gotowe, co wymaga uwagi i z czego możesz skorzystać dalej.",
      "/personality": "Produktowy przegląd tożsamości, wiedzy, planowania i możliwości.",
    },
    common: {
      workspace: "Przestrzeń",
      currentSurface: "Bieżący ekran",
      account: "Konto",
      signedInAs: "Zalogowano jako",
      signOut: "Wyloguj",
      build: "build",
      uiLanguage: "Język UI",
      utcOffset: "Offset UTC",
      conversationLanguage: "Język rozmowy",
      proactive: "Proaktywność",
      on: "Wł.",
      off: "Wył.",
      save: "Zapisz ustawienia",
      saving: "Zapisywanie...",
      loading: "Ładowanie...",
      interfaceOnly: "Tylko interfejs",
      details: "Szczegóły",
      inspectPayload: "Pokaż szczegóły",
      noData: "Brak danych.",
      user: "Ty",
      assistant: "Obecność",
      sourceOfTruth: "Bieżąca wartość",
      notSet: "brak",
      system: "System",
      stateLoadingTitle: "Przygotowuję widok",
      stateEmptyTitle: "Na razie nic tu nie ma",
      stateSuccessTitle: "Gotowe",
      stateErrorTitle: "Coś wymaga uwagi",
      stateDetailLabel: "Szczegóły",
    },
    auth: {
      badge: "Aviary",
      heroTitle: "Spokojne miejsce, żeby wrócić do rozmowy.",
      heroBody:
        "Zaloguj się, aby wrócić do czatu, ustawić preferencje i mieć Aviary blisko bez przedzierania się przez techniczny ekran startowy.",
      sessionEntry: "Wejście do sesji",
      trustTitle: "Czego możesz się spodziewać",
      login: "Zaloguj się",
      register: "Załóż konto",
      email: "Email",
      password: "Hasło",
      displayName: "Nazwa wyświetlana",
      enterWorkspace: "Wejdź do aplikacji",
      createAccount: "Utwórz konto",
      tabsLogin: "Logowanie",
      tabsRegister: "Rejestracja",
      trustCards: [
        {
          title: "Szybki powrót do workspace'u",
          body: "Czat, ustawienia i podpięte narzędzia są dostępne zaraz po zalogowaniu.",
        },
        {
          title: "Jeden prosty panel preferencji",
          body: "Profil, język i proaktywne follow-upy pozostają łatwe do znalezienia i zmiany.",
        },
        {
          title: "Prywatność i kontrola po Twojej stronie",
          body: "Później możesz zresetować continuity runtime'u bez usuwania samego konta.",
        },
      ],
    },
    chat: {
      eyebrow: "Rozmowa",
      title: "Porozmawiaj z osobowością",
      subtitle: "Najpierw widzisz wspólną rozmowę, niezależnie od tego, czy ostatnie wiadomości przyszły z aplikacji czy z podpiętego kanału.",
      emptyThread:
        "Zacznij rozmowę tutaj. Nowe wiadomości pojawią się w tym samym wspólnym wątku zaraz po wymianie.",
      placeholder: "Napisz wiadomość...",
      composerHint: "Odpowiedzi wracają do tego samego transcriptu, żeby cały dialog został w jednym miejscu.",
      send: "Wyślij wiadomość",
      sending: "Wysyłanie...",
      thread: "Wątek",
      latestMessages: "Ostatnie wiadomości",
      noHistory: "Nie ma jeszcze wspólnych wiadomości.",
      transcriptCount: "Elementy transcriptu",
      activeChannel: "Ostatnie kanały",
      latestLanguage: "Język live",
      messageDetails: "Szczegóły wiadomości",
      channel: "Kanał",
      pending: "Wysyłanie",
    },
    settings: {
      eyebrow: "Ustawienia",
      title: "Dopasuj powłokę",
      subtitle: "Krótki, mobile-first widok ustawień skupiony na profilu, języku interfejsu i proaktywnych follow-upach.",
      profileTitle: "Profil",
      profileBody: "Wybierz, jak aplikacja ma Cię opisywać.",
      uiLanguageTitle: "Język interfejsu",
      uiLanguageBody: "Zmienia etykiety, copy i nawigację tylko w powłoce aplikacji.",
      uiLanguageHelp: "To nie steruje językiem używanym wewnątrz samej rozmowy.",
      utcOffsetTitle: "Lokalny offset czasu",
      utcOffsetBody: "Ustawia jawny offset UTC, którego runtime używa przy wnioskowaniu o bieżącej dacie i godzinie dla Twojego profilu.",
      utcOffsetHelp: "Wybierz offset zgodny z Twoim aktualnym miejscem. Na przykład Polska lub Szwajcaria zimą to zwykle UTC+01:00.",
      conversationTitle: "Język rozmowy",
      conversationBody: "Język rozmowy dopasowuje się live na podstawie kontekstu, historii i bieżącej wymiany.",
      proactiveTitle: "Proaktywne follow-upy",
      proactiveBody: "Pozwól Aviary wysyłać okazjonalne follow-upy, gdy pozwalają na to ustawienia Twojego konta.",
      saveHint: "Zapisz zmiany, gdy będziesz gotowy.",
      conversationRuntimeOwned: "Adaptacyjne i oparte na kontekście",
      savedState: "Gotowe do zapisania",
      resetTitle: "Reset danych runtime",
      resetBody:
        "Wyczysc wyuczona ciaglosc runtime, pamiec, stan planowania i kolejki dla tego konta bez usuwania konta ani ponownej konfiguracji podpietych narzedzi.",
      resetImpact:
        "Profil, ustawienia UI, zgoda na proaktywnosc i podpiete integracje zostaja, a wszystkie aktywne sesje, takze ta biezaca, sa uniewazniane.",
      resetConfirmationLabel: "Tekst potwierdzenia",
      resetConfirmationHint: "Wpisz dokladnie ponizsza fraze, aby odblokowac reset.",
      resetConfirmationPlaceholder: "RESET MY DATA",
      resetAction: "Zresetuj dane runtime",
      resetting: "Resetowanie...",
      resetSuccess: "Dane runtime zostaly zresetowane. Zaloguj sie ponownie i zacznij od nowa.",
    },
    tools: {
      eyebrow: "Narzędzia",
      title: "Gotowe narzędzia i kanały",
      subtitle: "Zobacz, co działa już teraz, co wymaga działania, a co nadal jest zablokowane.",
      groupCount: "Grupy narzędzi",
      integral: "Zawsze aktywne",
      ready: "Gotowe teraz",
      linkRequired: "Wymaga podpięcia",
      loading: "Ładowanie przeglądu narzędzi.",
      empty: "Tutaj pojawi się przegląd Twoich narzędzi.",
      currentStatus: "Obecny stan",
      nextStep: "Następny krok",
      technicalDetails: "Szczegóły techniczne",
      availability: "Dostępność",
      provider: "Provider",
      control: "Sterowanie",
      linkState: "Stan podpięcia",
      readOnly: "Tylko podgląd",
      enabledByUser: "Włączone przez Ciebie",
      disabledByUser: "Wyłączone przez Ciebie",
      saving: "Zapisywanie...",
      noAction: "Brak wymaganej akcji.",
      telegramLinking: "Podpinanie Telegrama",
      generateCode: "Wygeneruj kod",
      rotateCode: "Obróć kod",
      generating: "Generowanie...",
      linkCode: "Kod podpięcia",
      instruction: "Instrukcja",
      noLinkCode: "Brak aktywnego kodu. Wygeneruj go, gdy będziesz gotowy potwierdzić czat.",
      capabilities: "Możliwości",
    },
    personality: {
      eyebrow: "Osobowość",
      title: "Przegląd osobowości",
      subtitle: "Najpierw najważniejsze informacje, a dodatkowe szczegóły tylko wtedy, gdy ich potrzebujesz.",
      goals: "Cele",
      tasks: "Zadania",
      knowledge: "Wiedza",
      preferences: "Preferencje",
      filter: "Filtruj sekcje",
      loading: "Ładowanie przeglądu osobowości.",
      empty: "Brak sekcji pasujących do filtra.",
      highlights: "Najważniejsze punkty",
    },
  },
  de: {
    routes: { "/login": "Login", "/chat": "Chat", "/settings": "Einstellungen", "/tools": "Tools", "/personality": "Persönlichkeit" },
    routeDescriptions: {
      "/login": "Melde dich in der Produkthülle an.",
      "/chat": "Ein gemeinsamer Gesprächsthread mit den letzten Nachrichten und neuen Antworten der Persönlichkeit.",
      "/settings": "Profil, Oberflächensprache und proaktive Präferenzen an einem klaren Ort.",
      "/tools": "Sieh, was bereit ist, was Aufmerksamkeit braucht und was du als Nächstes nutzen kannst.",
      "/personality": "Produktorientierter Überblick über Identität, Wissen, Planung und Fähigkeiten.",
    },
    common: {
      workspace: "Workspace",
      currentSurface: "Aktuelle Ansicht",
      account: "Konto",
      signedInAs: "Angemeldet als",
      signOut: "Abmelden",
      build: "build",
      uiLanguage: "UI-Sprache",
      utcOffset: "UTC-Offset",
      conversationLanguage: "Gesprächssprache",
      proactive: "Proaktiv",
      on: "An",
      off: "Aus",
      save: "Einstellungen speichern",
      saving: "Speichern...",
      loading: "Lädt...",
      interfaceOnly: "Nur Oberfläche",
      details: "Details",
      inspectPayload: "Details anzeigen",
      noData: "Noch keine Daten.",
      user: "Du",
      assistant: "Präsenz",
      sourceOfTruth: "Aktueller Wert",
      notSet: "nicht gesetzt",
      system: "System",
      stateLoadingTitle: "Ansicht wird vorbereitet",
      stateEmptyTitle: "Hier ist noch nichts zu sehen",
      stateSuccessTitle: "Erledigt",
      stateErrorTitle: "Etwas braucht Aufmerksamkeit",
      stateDetailLabel: "Details",
    },
    auth: {
      badge: "Aviary",
      heroTitle: "Ein ruhiger Ort, um das Gespräch fortzusetzen.",
      heroBody:
        "Melde dich an, um zum Chat zurückzukehren, Einstellungen anzupassen und Aviary ohne technischen Ballast direkt griffbereit zu haben.",
      sessionEntry: "Sitzung",
      trustTitle: "Was dich erwartet",
      login: "Einloggen",
      register: "Konto erstellen",
      email: "E-Mail",
      password: "Passwort",
      displayName: "Anzeigename",
      enterWorkspace: "Zum Workspace",
      createAccount: "Konto erstellen",
      tabsLogin: "Login",
      tabsRegister: "Registrieren",
      trustCards: [
        {
          title: "Schnell zurück im Workspace",
          body: "Chat, Einstellungen und verbundene Tools sind nach dem Login direkt da.",
        },
        {
          title: "Ein klarer Ort für deine Präferenzen",
          body: "Profil, Sprache und proaktive Follow-ups bleiben leicht erreichbar.",
        },
        {
          title: "Mehr Privatsphäre und Kontrolle",
          body: "Später kannst du die Runtime-Kontinuität zurücksetzen, ohne das Konto zu löschen.",
        },
      ],
    },
    chat: {
      eyebrow: "Gespräch",
      title: "Sprich mit der Persönlichkeit",
      subtitle: "Du siehst zuerst den gemeinsamen Gesprächsverlauf, egal ob die letzten Nachrichten aus der App oder aus einem verknüpften Kanal kamen.",
      emptyThread:
        "Starte die Unterhaltung hier. Neue Nachrichten erscheinen direkt in diesem gemeinsamen Thread, sobald sie ausgetauscht wurden.",
      placeholder: "Sende eine Nachricht...",
      composerHint: "Antworten landen wieder in diesem selben Transkript, damit die ganze Unterhaltung an einem Ort bleibt.",
      send: "Nachricht senden",
      sending: "Senden...",
      thread: "Thread",
      latestMessages: "Letzte Nachrichten",
      noHistory: "Noch keine gemeinsamen Nachrichten.",
      transcriptCount: "Transkript-Einträge",
      activeChannel: "Letzte Kanäle",
      latestLanguage: "Live-Sprache",
      messageDetails: "Nachrichtendetails",
      channel: "Kanal",
      pending: "Wird gesendet",
    },
    settings: {
      eyebrow: "Einstellungen",
      title: "Hülle anpassen",
      subtitle: "Kurzer mobile-first Bereich für Profil, Oberflächensprache und proaktive Follow-ups.",
      profileTitle: "Profil",
      profileBody: "Lege fest, wie dich die App anzeigen soll.",
      uiLanguageTitle: "Oberflächensprache",
      uiLanguageBody: "Ändert nur Labels, Copy und Navigation der App-Hülle.",
      uiLanguageHelp: "Das steuert nicht die Sprache innerhalb des eigentlichen Gesprächs.",
      utcOffsetTitle: "Lokaler Zeit-Offset",
      utcOffsetBody: "Legt den expliziten UTC-Offset fest, den die Runtime für Datum und Uhrzeit deines Profils verwendet.",
      utcOffsetHelp: "Wähle den Offset passend zu deinem aktuellen Ort. Polen oder die Schweiz im Winter sind zum Beispiel meist UTC+01:00.",
      conversationTitle: "Gesprächssprache",
      conversationBody: "Die Gesprächssprache passt sich live aus Kontext, Verlauf und aktueller Unterhaltung an.",
      proactiveTitle: "Proaktive Follow-ups",
      proactiveBody: "Erlaube Aviary gelegentliche Follow-ups, wenn deine Kontoeinstellungen es zulassen.",
      saveHint: "Speichere deine Änderungen, wenn du bereit bist.",
      conversationRuntimeOwned: "Adaptiv und kontextbezogen",
      savedState: "Bereit zum Speichern",
      resetTitle: "Runtime-Daten zurucksetzen",
      resetBody:
        "Loscht gelernte Runtime-Kontinuitat, Erinnerung, Planungszustand und Warteschlangenstatus fur dieses Konto, ohne das Konto oder verknupfte Tools neu aufzusetzen.",
      resetImpact:
        "Profil, UI-Sprache, proaktive Einstellungen und verknupfte Integrationen bleiben erhalten, danach werden alle aktiven Sitzungen inklusive dieser Sitzung widerrufen.",
      resetConfirmationLabel: "Bestatigungstext",
      resetConfirmationHint: "Gib die folgende Phrase exakt ein, um den Reset freizuschalten.",
      resetConfirmationPlaceholder: "RESET MY DATA",
      resetAction: "Meine Runtime-Daten zurucksetzen",
      resetting: "Wird zuruckgesetzt...",
      resetSuccess: "Runtime-Daten wurden zuruckgesetzt. Melde dich erneut an, um frisch zu starten.",
    },
    tools: {
      eyebrow: "Tools",
      title: "Verfügbare Tools und Kanäle",
      subtitle: "Sieh, was jetzt bereit ist, was Aktion braucht und was noch blockiert ist.",
      groupCount: "Tool-Gruppen",
      integral: "Immer aktiv",
      ready: "Jetzt bereit",
      linkRequired: "Benötigt Verknüpfung",
      loading: "Tool-Übersicht wird geladen.",
      empty: "Noch keine Tool-Übersicht geladen.",
      currentStatus: "Aktueller Status",
      nextStep: "Nächster Schritt",
      technicalDetails: "Technische Details",
      availability: "Verfügbarkeit",
      provider: "Provider",
      control: "Steuerung",
      linkState: "Verknüpfungsstatus",
      readOnly: "Nur lesen",
      enabledByUser: "Von dir aktiviert",
      disabledByUser: "Von dir deaktiviert",
      saving: "Speichern...",
      noAction: "Keine Aktion nötig.",
      telegramLinking: "Telegram verknüpfen",
      generateCode: "Code erzeugen",
      rotateCode: "Code erneuern",
      generating: "Erzeugen...",
      linkCode: "Verknüpfungscode",
      instruction: "Anleitung",
      noLinkCode: "Noch kein aktiver Code. Erzeuge ihn, wenn du den Chat bestätigen willst.",
      capabilities: "Fähigkeiten",
    },
    personality: {
      eyebrow: "Persönlichkeit",
      title: "Persönlichkeitsübersicht",
      subtitle: "Zuerst die wichtigsten Einblicke, weitere Details nur dann, wenn du sie sehen willst.",
      goals: "Ziele",
      tasks: "Aufgaben",
      knowledge: "Wissen",
      preferences: "Präferenzen",
      filter: "Sektionen filtern",
      loading: "Persönlichkeitsübersicht wird geladen.",
      empty: "Keine passenden Sektionen für diesen Filter.",
      highlights: "Highlights",
    },
  },
} as const;

function normalizeRoute(pathname: string): RoutePath {
  if (pathname === "/dashboard" || pathname === "/") {
    return "/dashboard";
  }
  if (pathname === "/settings") {
    return "/settings";
  }
  if (pathname === "/tools") {
    return "/tools";
  }
  if (pathname === "/personality") {
    return "/personality";
  }
  if (pathname === "/chat") {
    return "/chat";
  }
  return "/login";
}
function navigate(path: RoutePath) {
  if (window.location.pathname !== path) {
    window.history.pushState({}, "", path);
  }
}
function normalizeUiLanguage(value: string | null | undefined): UiLanguageCode {
  if (value === "en" || value === "pl" || value === "de" || value === "system") {
    return value;
  }
  return "system";
}

function resolveUiLanguage(value: UiLanguageCode): ResolvedUiLanguageCode {
  if (value !== "system") {
    return value;
  }
  const browserLanguage = typeof window !== "undefined" ? window.navigator.language.toLowerCase() : "en";
  if (browserLanguage.startsWith("pl")) {
    return "pl";
  }
  if (browserLanguage.startsWith("de")) {
    return "de";
  }
  return "en";
}

function uiLanguageMetadata(value: UiLanguageCode) {
  return UI_LANGUAGE_OPTIONS.find((option) => option.value === value) ?? UI_LANGUAGE_OPTIONS[0];
}

function normalizeUtcOffset(value: string | null | undefined) {
  const normalized = String(value ?? "").trim().toUpperCase();
  return UTC_OFFSET_OPTIONS.find((option) => option.value === normalized)?.value ?? "UTC+00:00";
}

function utcOffsetOption(value: string | null | undefined) {
  const normalized = normalizeUtcOffset(value);
  return UTC_OFFSET_OPTIONS.find((option) => option.value === normalized) ?? UTC_OFFSET_OPTIONS[48];
}

function formatTimestamp(value: string | undefined, locale: string | undefined) {
  if (!value) {
    return "unknown time";
  }

  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return value;
  }

  return new Intl.DateTimeFormat(locale, {
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

function truncateText(value: string, maxLength: number) {
  const trimmed = value.trim();
  if (trimmed.length <= maxLength) {
    return trimmed;
  }

  return `${trimmed.slice(0, Math.max(0, maxLength - 1)).trimEnd()}...`;
}

function transcriptMetadataSummary(entry: AppChatHistoryEntry) {
  if (!entry.metadata) {
    return null;
  }

  const language = stringValue(entry.metadata.language, "").trim();
  const tone = stringValue(entry.metadata.tone, "").trim();
  const runtimeRole = stringValue(entry.metadata.runtime_role, "").trim();
  const actionStatus = stringValue(entry.metadata.action_status, "").trim();

  const parts = [
    language ? `lang ${language}` : null,
    tone ? `tone ${tone}` : null,
    runtimeRole ? `role ${runtimeRole}` : null,
    actionStatus ? `action ${actionStatus}` : null,
  ].filter(Boolean);

  return parts.length > 0 ? parts.join(" | ") : null;
}

function routeDescription(route: RoutePath, locale: ResolvedUiLanguageCode) {
  const localized = UI_COPY[locale].routeDescriptions as Record<string, string>;
  return localized[route] ?? UI_COPY.en.routeDescriptions[route];
}

function routeLabel(route: RoutePath, locale: ResolvedUiLanguageCode) {
  const localized = UI_COPY[locale].routes as Record<string, string>;
  return localized[route] ?? UI_COPY.en.routes[route];
}

function localeLanguageLabel(option: (typeof UI_LANGUAGE_OPTIONS)[number], locale: ResolvedUiLanguageCode) {
  return option.label[locale];
}

function localeOptionDisplay(option: (typeof UI_LANGUAGE_OPTIONS)[number], locale: ResolvedUiLanguageCode) {
  return `${option.iconToken} ${option.nativeLabel}${localeLanguageLabel(option, locale) === option.nativeLabel ? "" : ` · ${localeLanguageLabel(option, locale)}`}`;
}

function titleCaseFromStatus(value: string) {
  return value
    .split("_")
    .filter(Boolean)
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(" ");
}

function toolStatusClass(status: string) {
  if (status === "integral_active" || status === "provider_ready") {
    return "badge-success";
  }
  if (status === "provider_ready_link_required") {
    return "badge-warning";
  }
  if (status === "planned_placeholder") {
    return "badge-ghost";
  }
  return "badge-outline";
}

function formatToolState(status: string) {
  if (status === "integral_active") {
    return "Always on";
  }
  if (status === "provider_ready") {
    return "Ready to use";
  }
  if (status === "provider_ready_link_required") {
    return "Link required";
  }
  if (status === "planned_placeholder") {
    return "Planned";
  }
  return titleCaseFromStatus(status);
}

function summarizeToolAction(nextActions: string[], fallback: string) {
  const action = nextActions[0];
  if (!action) {
    return fallback;
  }
  return action.replaceAll("_", " ");
}

function summaryLines(sectionKey: string, payload: unknown): string[] {
  const record = payload && typeof payload === "object" ? (payload as Record<string, unknown>) : {};
  if (sectionKey === "identity_state") {
    const profile = (record.profile as Record<string, unknown> | undefined) ?? {};
    const preferenceSummary = (record.preference_summary as Record<string, unknown> | undefined) ?? {};
    return [
      `Preferred conversation language: ${stringValue(profile.preferred_language, "unknown")}`,
      `Learned preferences available: ${stringValue(preferenceSummary.learned_preference_count, "0")}`,
    ];
  }
  if (sectionKey === "learned_knowledge") {
    const knowledgeSummary = (record.knowledge_summary as Record<string, unknown> | undefined) ?? {};
    return [
      `Patterns captured: ${stringValue(knowledgeSummary.semantic_conclusion_count, "0")}`,
      `Mood-aware takeaways: ${stringValue(knowledgeSummary.affective_conclusion_count, "0")}`,
    ];
  }
  if (sectionKey === "planning_state") {
    const continuitySummary = (record.continuity_summary as Record<string, unknown> | undefined) ?? {};
    return [
      `Active goals: ${stringValue(continuitySummary.active_goal_count, "0")}`,
      `Active tasks: ${stringValue(continuitySummary.active_task_count, "0")}`,
    ];
  }
  if (sectionKey === "role_skill_state") {
    const selectionSummary = (record.selection_visibility_summary as Record<string, unknown> | undefined) ?? {};
    return [
      `Skills currently listed: ${stringValue(selectionSummary.catalog_skill_count, "0")}`,
      `Current selection view: ${stringValue(selectionSummary.runtime_selection_surface, "available")}`,
    ];
  }
  if (sectionKey === "capability_catalog") {
    const posture = (record.tool_and_connector_posture as Record<string, unknown> | undefined) ?? {};
    return [
      `Organizer setup: ${stringValue(posture.organizer_stack_state, "unknown")}`,
      `Tool families available: ${Array.isArray(posture.selectable_tool_families) ? posture.selectable_tool_families.length : 0}`,
    ];
  }
  if (sectionKey === "api_readiness") {
    return [
      `Product stage: ${stringValue(record.product_stage, "unknown")}`,
      `Internal checks available: ${stringValue(record.internal_inspection_path, "yes")}`,
    ];
  }
  return [prettyJson(payload).slice(0, 140)];
}

function StatePanel({
  tone,
  title,
  body,
  loading = false,
}: {
  tone: "neutral" | "success" | "error";
  title: string;
  body: string;
  loading?: boolean;
}) {
  const toneClasses =
    tone === "error"
      ? "border-error/30 bg-error/5 text-base-900"
      : tone === "success"
        ? "border-success/30 bg-success/10 text-base-900"
        : "border-base-300 bg-base-200 text-base-900";

  return (
    <div className={`rounded-2xl border px-4 py-5 ${toneClasses}`}>
      <div className="flex items-start gap-3">
        {loading ? <span className="loading loading-spinner loading-sm mt-0.5 text-primary" /> : null}
        <div>
          <p className="text-sm font-semibold">{title}</p>
          <p className="mt-1 text-sm leading-7 text-base-800">{body}</p>
        </div>
      </div>
    </div>
  );
}
function FeedbackBanner({
  tone,
  title,
  body,
  detail,
  detailLabel,
}: {
  tone: "success" | "error";
  title: string;
  body: string;
  detail?: string | null;
  detailLabel: string;
}) {
  const toneClasses =
    tone === "error"
      ? "border-error/40 bg-error/8 text-base-900"
      : "border-success/40 bg-success/12 text-base-900";

  return (
    <div className={`mb-4 rounded-[1.5rem] border px-4 py-4 shadow-sm ${toneClasses}`}>
      <p className="text-sm font-semibold">{title}</p>
      <p className="mt-1 text-sm leading-7 text-base-800">{body}</p>
      {detail ? (
        <details className="mt-3">
          <summary className="cursor-pointer text-sm font-medium text-base-900">{detailLabel}</summary>
          <p className="mt-2 break-words rounded-xl bg-base-100/80 px-3 py-3 text-sm leading-7 text-base-800">
            {detail}
          </p>
        </details>
      ) : null}
    </div>
  );
}

function MetricCard({
  eyebrow,
  value,
  detail,
  accent = "default",
  className = "",
}: {
  eyebrow: string;
  value: string;
  detail: string;
  accent?: "default" | "teal" | "gold";
  className?: string;
}) {
  const accentClasses =
    accent === "teal"
      ? "border-[#8eb8b2]/30 bg-[#eff7f5]"
      : accent === "gold"
        ? "border-[#d2b07f]/30 bg-[#fcf6ea]"
        : "border-base-300 bg-base-100";

  return (
    <article className={`rounded-[1.5rem] border p-4 shadow-sm ${accentClasses} ${className}`.trim()}>
      <p className="text-xs uppercase tracking-[0.22em] text-base-800">{eyebrow}</p>
      <p className="mt-3 font-display text-3xl text-base-900">{value}</p>
      <p className="mt-2 text-sm leading-7 text-base-800">{detail}</p>
    </article>
  );
}

function ModuleEntryCard({
  label,
  title,
  body,
  meta,
  onClick,
}: {
  label: string;
  title: string;
  body: string;
  meta: string;
  onClick: () => void;
}) {
  return (
    <button
      className="aion-panel-soft group rounded-[1.6rem] p-4 text-left transition duration-200 hover:-translate-y-0.5 hover:border-[#7ea79f]/35"
      onClick={onClick}
      type="button"
    >
      <p className="text-[11px] uppercase tracking-[0.24em] text-base-800">{label}</p>
      <div className="mt-3 flex items-start justify-between gap-3">
        <div>
          <h3 className="font-display text-2xl text-base-900">{title}</h3>
          <p className="mt-2 text-sm leading-7 text-base-800">{body}</p>
        </div>
        <span className="aion-chip rounded-full px-3 py-1 text-[11px] font-semibold uppercase tracking-[0.18em] text-base-900">
          {meta}
        </span>
      </div>
      <div className="mt-4 flex items-center justify-between text-sm text-base-800">
        <span>Open space</span>
        <span className="font-semibold text-base-900 transition group-hover:translate-x-1">→</span>
      </div>
    </button>
  );
}

function FlowRail({
  items,
}: {
  items: Array<{
    eyebrow: string;
    title: string;
    body: string;
  }>;
}) {
  return (
    <div className="grid gap-4">
      {items.map((item) => (
        <article key={item.title} className="aion-flow-line pl-8">
          <span className="absolute left-0 top-1 flex h-5 w-5 items-center justify-center rounded-full border border-[#8eb8b2]/35 bg-[#f6faf8] text-[10px] font-semibold text-[#567671]">
            •
          </span>
          <p className="text-[11px] uppercase tracking-[0.22em] text-base-800">{item.eyebrow}</p>
          <h4 className="mt-1 font-display text-xl text-base-900">{item.title}</h4>
          <p className="mt-2 text-sm leading-7 text-base-800">{item.body}</p>
        </article>
      ))}
    </div>
  );
}

function MotifFigurePanel({
  title,
  body,
  highlights,
}: {
  title: string;
  body: string;
  highlights: Array<{ label: string; value: string }>;
}) {
  return (
    <div className="aion-panel aion-halo aion-motif-panel rounded-[2rem] p-5">
      <div className="grid gap-5 lg:grid-cols-[minmax(0,0.85fr)_minmax(0,1.15fr)] lg:items-center">
        <div className="aion-figure">
          <div className="aion-figure-grid" />
        </div>
        <div className="space-y-4">
          <div>
            <p className="text-[11px] uppercase tracking-[0.24em] text-base-800">Embodied cognition</p>
            <h3 className="mt-2 font-display text-3xl text-base-900">{title}</h3>
            <p className="mt-3 text-sm leading-7 text-base-800">{body}</p>
          </div>
          <div className="grid gap-3 sm:grid-cols-2">
            {highlights.map((item) => (
              <div key={item.label} className="aion-chip rounded-[1.3rem] px-4 py-3">
                <p className="text-[11px] uppercase tracking-[0.22em] text-base-800">{item.label}</p>
                <p className="mt-2 text-sm font-semibold leading-6 text-base-900">{item.value}</p>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

function RouteHeroPanel({
  eyebrow,
  title,
  body,
  chips,
  className = "",
}: {
  eyebrow: string;
  title: string;
  body: string;
  chips: string[];
  className?: string;
}) {
  return (
    <section className={`aion-panel aion-halo rounded-[2rem] p-5 ${className}`}>
      <div className="grid gap-5 lg:grid-cols-[minmax(0,1.2fr)_minmax(18rem,0.8fr)] lg:items-end">
        <div className="max-w-3xl">
          <p className="text-sm uppercase tracking-[0.24em] text-base-800">{eyebrow}</p>
          <h2 className="mt-2 font-display text-3xl text-base-900 md:text-4xl">{title}</h2>
          <p className="mt-3 text-sm leading-7 text-base-800 md:text-base">{body}</p>
        </div>
        <div className="flex flex-wrap gap-2 lg:justify-end">
          {chips.map((chip) => (
            <span key={chip} className="aion-chip rounded-full px-3 py-1 text-xs font-semibold uppercase tracking-[0.18em] text-base-900">
              {chip}
            </span>
          ))}
        </div>
      </div>
    </section>
  );
}

function InsightPanel({
  eyebrow,
  title,
  body,
  children,
  className = "",
}: {
  eyebrow: string;
  title: string;
  body: string;
  children: ReactNode;
  className?: string;
}) {
  return (
    <section className={`aion-panel-soft rounded-[2rem] p-5 ${className}`}>
      <div className="mb-4 max-w-3xl">
        <p className="text-sm uppercase tracking-[0.24em] text-base-800">{eyebrow}</p>
        <h3 className="mt-2 font-display text-2xl text-base-900">{title}</h3>
        <p className="mt-3 text-sm leading-7 text-base-800">{body}</p>
      </div>
      {children}
    </section>
  );
}

function PersonalityLayerCard({
  zone,
  title,
  symbol,
  body,
  highlights,
}: {
  zone: string;
  title: string;
  symbol: string;
  body: string;
  highlights: string[];
}) {
  return (
    <article className="aion-panel-soft rounded-[1.7rem] p-4">
      <div className="mb-4 flex items-start justify-between gap-3">
        <div>
          <p className="text-[11px] uppercase tracking-[0.22em] text-base-800">{zone}</p>
          <h4 className="mt-2 font-display text-2xl text-base-900">{title}</h4>
        </div>
        <span className="aion-chip flex h-11 w-11 items-center justify-center rounded-full text-lg font-semibold text-base-900">
          {symbol}
        </span>
      </div>
      <p className="text-sm leading-7 text-base-800">{body}</p>
      <div className="mt-4 flex flex-wrap gap-2">
        {highlights.map((item) => (
          <span key={item} className="aion-chip-ghost rounded-full px-3 py-1 text-xs font-medium">
            {item}
          </span>
        ))}
      </div>
    </article>
  );
}

function ShellNavButton({
  label,
  description,
  active,
  token,
  onClick,
}: {
  label: string;
  description: string;
  active: boolean;
  token: string;
  onClick: () => void;
}) {
  return (
    <button
      className={`aion-nav-button ${active ? "aion-nav-button-active" : ""}`}
      onClick={onClick}
      type="button"
    >
      <span className={`aion-nav-token ${active ? "aion-nav-token-active" : ""}`}>{token}</span>
      <span className="min-w-0 flex-1 text-left">
        <span className="block text-sm font-semibold text-base-900">{label}</span>
        <span className="mt-0.5 block truncate text-xs text-base-800">{description}</span>
      </span>
    </button>
  );
}

function AviaryWordmark({ className = "", compact = false }: { className?: string; compact?: boolean }) {
  return (
    <div
      aria-label="Aviary"
      className={`aion-brand-lockup ${compact ? "aion-brand-lockup-compact" : ""} ${className}`.trim()}
    >
      <img alt="" aria-hidden="true" className="aion-brand-mark" src="/aviary-logomark.svg" />
      <span className="aion-brand-word">AVIARY</span>
    </div>
  );
}

function ChatFlowStage({
  label,
  title,
  detail,
  active = false,
}: {
  label: string;
  title: string;
  detail: string;
  active?: boolean;
}) {
  return (
    <article className={`aion-chat-flow-stage ${active ? "aion-chat-flow-stage-active" : ""}`}>
      <span className={`aion-chat-flow-icon ${active ? "aion-chat-flow-icon-active" : ""}`}>{label}</span>
      <div>
        <p className="text-base font-semibold text-base-900">{title}</p>
        <p className="mt-1 text-sm leading-6 text-base-800">{detail}</p>
      </div>
    </article>
  );
}

function ChatFeatureCard({
  token,
  title,
  body,
}: {
  token: string;
  title: string;
  body: string;
}) {
  return (
    <article className="aion-feature-card">
      <span className="aion-feature-token">{token}</span>
      <div>
        <p className="text-base font-semibold text-base-900">{title}</p>
        <p className="mt-1 text-sm leading-6 text-base-800">{body}</p>
      </div>
    </article>
  );
}

function ShellUtilityBar({
  currentSurface,
  currentUserLabel,
  accountPanelOpen,
  onAccountClick,
}: {
  currentSurface: string;
  currentUserLabel: string;
  accountPanelOpen: boolean;
  onAccountClick: () => void;
}) {
  return (
    <header className="aion-utility-bar hidden xl:grid">
      <div className="aion-utility-context">
        <span className="aion-utility-context-emblem">✦</span>
        <div className="min-w-0">
          <p className="aion-utility-context-label">Aviary workspace</p>
          <p className="aion-utility-context-copy">{currentSurface}</p>
        </div>
      </div>
      <label className="aion-utility-search" aria-label="Search workspace">
        <span className="aion-utility-search-icon">⌕</span>
        <input readOnly type="text" value="" placeholder="Search Aviary or ask anything..." />
        <span className="aion-utility-search-shortcut">⌘K</span>
      </label>
      <div className="aion-utility-actions">
        <button className="aion-utility-pill" type="button">
          <span className="aion-utility-pill-dot" />
          Focus mode
        </button>
        <button className="aion-utility-pill" type="button">
          ✧
          Quick capture
        </button>
        <button className="aion-utility-icon-pill" type="button" aria-label="Notifications">
          3
        </button>
        <button
          className={`aion-utility-account ${accountPanelOpen ? "aion-utility-account-active" : ""}`}
          onClick={onAccountClick}
          type="button"
        >
          <span className="aion-utility-account-avatar">{currentUserLabel.slice(0, 1).toUpperCase()}</span>
          <span className="aion-utility-account-copy">{currentUserLabel}</span>
        </button>
      </div>
    </header>
  );
}

function PersonalityTimelineRow({
  token,
  title,
  detail,
  value,
}: {
  token: string;
  title: string;
  detail: string;
  value: string;
}) {
  return (
    <article className="aion-personality-timeline-row">
      <span className="aion-personality-timeline-token">{token}</span>
      <div className="min-w-0">
        <p className="text-sm font-semibold text-base-900">{title}</p>
        <p className="mt-1 text-xs leading-6 text-base-800">{detail}</p>
      </div>
      <div className="aion-personality-timeline-track" aria-hidden="true">
        <span />
      </div>
      <span className="aion-personality-timeline-value">{value}</span>
    </article>
  );
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
  const [pendingChatMessage, setPendingChatMessage] = useState<AppChatHistoryEntry | null>(null);
  const [chatText, setChatText] = useState("");
  const [overview, setOverview] = useState<AppPersonalityOverviewResponse | null>(null);
  const [, setOverviewLoading] = useState(false);
  const [toolsOverview, setToolsOverview] = useState<AppToolsOverviewResponse | null>(null);
  const [toolsLoading, setToolsLoading] = useState(false);
  const [savingToolId, setSavingToolId] = useState<string | null>(null);
  const [telegramLinkStart, setTelegramLinkStart] = useState<AppTelegramLinkStartResponse | null>(null);
  const [telegramLinkBusy, setTelegramLinkBusy] = useState(false);
  const [authForm, setAuthForm] = useState({
    email: "",
    password: "",
    displayName: "",
  });
  const [settingsDraft, setSettingsDraft] = useState({
    displayName: "",
    uiLanguage: "system" as UiLanguageCode,
    utcOffset: "UTC+00:00",
    proactiveOptIn: false,
  });
  const [savingSettings, setSavingSettings] = useState(false);
  const [resetConfirmationText, setResetConfirmationText] = useState("");
  const [resettingData, setResettingData] = useState(false);
  const [accountPanelOpen, setAccountPanelOpen] = useState(false);
  const transcriptContainerRef = useRef<HTMLDivElement | null>(null);
  const transcriptMessageRefs = useRef<Record<string, HTMLArticleElement | null>>({});
  const initialTranscriptScrollDoneRef = useRef(false);
  const pendingAssistantScrollIdRef = useRef<string | null>(null);

  useEffect(() => {
    const onPopState = () => {
      setRoute(normalizeRoute(window.location.pathname));
    };

    window.addEventListener("popstate", onPopState);
    return () => window.removeEventListener("popstate", onPopState);
  }, []);

  useEffect(() => {
    setError(null);
    setAccountPanelOpen(false);
  }, [route]);

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
          uiLanguage: normalizeUiLanguage(snapshot.settings.ui_language),
          utcOffset: normalizeUtcOffset(snapshot.settings.utc_offset),
          proactiveOptIn: Boolean(snapshot.settings.proactive_opt_in),
        });
        if (route === "/login") {
          startTransition(() => {
            navigate("/dashboard");
            setRoute("/dashboard");
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
    if (!me || (route !== "/chat" && route !== "/dashboard")) {
      setPendingChatMessage(null);
      initialTranscriptScrollDoneRef.current = false;
      pendingAssistantScrollIdRef.current = null;
      return;
    }

    let cancelled = false;
    setHistoryLoading(true);
    void api
      .getChatHistory()
      .then((payload) => {
        if (!cancelled) {
          setError(null);
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

  const transcriptItems = useMemo(
    () => (pendingChatMessage ? [...history, pendingChatMessage] : history),
    [history, pendingChatMessage],
  );
  const transcriptIsPreview = transcriptItems.length === 0;
  const visibleTranscriptItems = useMemo<AppChatHistoryEntry[]>(
    () =>
      transcriptItems.length > 0
        ? transcriptItems
        : [
            {
              message_id: "preview-assistant-1",
              event_id: "preview-assistant-1",
              role: "assistant",
              text: "Good morning.\nI reviewed our last conversation and the notes from today.\nHow can I support you right now?",
              channel: "app",
              timestamp: "2026-04-26T09:41:00Z",
            },
            {
              message_id: "preview-user-1",
              event_id: "preview-user-1",
              role: "user",
              text: "I'd like to plan my day and focus on the project we discussed yesterday.",
              channel: "app",
              timestamp: "2026-04-26T09:42:00Z",
            },
            {
              message_id: "preview-assistant-2",
              event_id: "preview-assistant-2",
              role: "assistant",
              text:
                "Perfect. I prepared a calm plan based on your goals, energy rhythm, and current priorities.\n\n1. Deep work block      10:00–12:00\n2. Project research     12:30–14:00\n3. Content creation     15:00–17:00\n\nShall we refine the details together?",
              channel: "app",
              timestamp: "2026-04-26T09:43:00Z",
            },
          ],
    [transcriptItems],
  );

  useEffect(() => {
    if (route !== "/chat") {
      transcriptMessageRefs.current = {};
      return;
    }

    const container = transcriptContainerRef.current;
    if (!container || transcriptItems.length === 0) {
      return;
    }

    if (!initialTranscriptScrollDoneRef.current) {
      container.scrollTop = container.scrollHeight;
      initialTranscriptScrollDoneRef.current = true;
      return;
    }

    const pendingAssistantScrollId = pendingAssistantScrollIdRef.current;
    if (!pendingAssistantScrollId) {
      return;
    }

    const target = transcriptMessageRefs.current[pendingAssistantScrollId];
    if (!target) {
      return;
    }

    target.scrollIntoView({ block: "start", behavior: "smooth" });
    pendingAssistantScrollIdRef.current = null;
  }, [route, transcriptItems]);

  useEffect(() => {
    if (!me || (route !== "/personality" && route !== "/chat" && route !== "/dashboard") || overview) {
      return;
    }

    let cancelled = false;
    setOverviewLoading(true);
    void api
      .getPersonalityOverview()
      .then((payload) => {
        if (!cancelled) {
          setError(null);
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
  }, [me, route, overview]);

  useEffect(() => {
    if (!me || (route !== "/tools" && route !== "/chat" && route !== "/dashboard") || toolsOverview) {
      return;
    }

    let cancelled = false;
    setToolsLoading(true);
    void api
      .getToolsOverview()
      .then((payload) => {
        if (!cancelled) {
          setError(null);
          setToolsOverview(payload);
        }
      })
      .catch((caught) => {
        if (!cancelled) {
          setError(caught instanceof Error ? caught.message : "Failed to load tools overview.");
        }
      })
      .finally(() => {
        if (!cancelled) {
          setToolsLoading(false);
        }
      });

    return () => {
      cancelled = true;
    };
  }, [me, route, toolsOverview]);

  const planningSummary = (overview?.planning_state as Record<string, unknown> | undefined)?.continuity_summary as
    | Record<string, unknown>
    | undefined;
  const knowledgeSummary = (overview?.learned_knowledge as Record<string, unknown> | undefined)?.knowledge_summary as
    | Record<string, unknown>
    | undefined;
  const preferenceSummary = (overview?.identity_state as Record<string, unknown> | undefined)?.preference_summary as
    | Record<string, unknown>
    | undefined;
  const selectedUiLanguage = normalizeUiLanguage(
    route === "/settings" ? settingsDraft.uiLanguage : me?.settings.ui_language ?? settingsDraft.uiLanguage,
  );
  const selectedUtcOffset = normalizeUtcOffset(
    route === "/settings" ? settingsDraft.utcOffset : me?.settings.utc_offset ?? settingsDraft.utcOffset,
  );
  const resolvedUiLanguage = resolveUiLanguage(selectedUiLanguage);
  const selectedUiLanguageMetadata = uiLanguageMetadata(selectedUiLanguage);
  const selectedUtcOffsetMetadata = utcOffsetOption(selectedUtcOffset);
  const copy = UI_COPY[resolvedUiLanguage];
  const recentChannelsLabel = useMemo(() => {
    const recentChannels = Array.from(new Set(history.map((item) => item.channel))).filter(Boolean);
    return recentChannels.length > 0 ? recentChannels.join(" • ") : copy.common.noData;
  }, [copy.common.noData, history]);
  const currentUserLabel = me?.user.display_name || me?.user.email || "Account";
  const accountSummaryItems = [
    {
      label: copy.common.uiLanguage,
      value: localeOptionDisplay(selectedUiLanguageMetadata, resolvedUiLanguage),
    },
    {
      label: copy.common.utcOffset,
      value: selectedUtcOffsetMetadata.value,
    },
    {
      label: copy.common.proactive,
      value: Boolean(me?.settings.proactive_opt_in) ? copy.common.on : copy.common.off,
    },
  ];
  const successBody = toast ?? null;
  const errorBody = error ? error.split("\n")[0] : null;
  const errorDetail = error && errorBody !== error ? error : null;
  const latestAssistantMessage =
    [...transcriptItems].reverse().find((entry) => entry.role === "assistant")?.text ?? copy.chat.emptyThread;
  const latestUserMessage = [...transcriptItems].reverse().find((entry) => entry.role === "user")?.text ?? "";
  const dashboardFlowItems = [
    {
      eyebrow: "Foreground",
      title: "Event to context",
      body: "New turns are normalized first, then anchored in perception and context before anything is expressed.",
    },
    {
      eyebrow: "Decision",
      title: "Motivation, role, planning",
      body: "The personality chooses the right posture, priorities, and plan instead of replying from an empty shell.",
    },
    {
      eyebrow: "Continuity",
      title: "Expression, action, memory, reflection",
      body: "Replies land in the shared transcript while memory and reflection keep continuity alive in the background.",
    },
  ];
  const dashboardHeroChips = [
    `${stringValue(planningSummary?.active_goal_count, "0")} goals`,
    `${stringValue(knowledgeSummary?.semantic_conclusion_count, "0")} memories`,
    `${stringValue(preferenceSummary?.learned_preference_count, "0")} learned cues`,
  ];
  const dashboardSignalCards = [
    {
      placement: "left",
      eyebrow: "Memory",
      value: stringValue(knowledgeSummary?.semantic_conclusion_count, "0"),
      detail: "Total memories",
      note: "Continuity held across recent sessions.",
    },
    {
      placement: "left",
      eyebrow: "Reflection",
      value: stringValue(knowledgeSummary?.affective_conclusion_count, "0"),
      detail: "Insights gained",
      note: "Slower learning shaping future replies.",
    },
    {
      placement: "left",
      eyebrow: "Context",
      value: recentChannelsLabel === copy.common.noData ? "Ready" : "Live",
      detail: "Relevance",
      note: recentChannelsLabel,
    },
    {
      placement: "right",
      eyebrow: "Motivation",
      value: stringValue(planningSummary?.active_goal_count, "0") === "0" ? "Steady" : "Aligned",
      detail: "Current posture",
      note: "Goals and values stay in the foreground.",
    },
    {
      placement: "right",
      eyebrow: "Planning",
      value: `${stringValue(planningSummary?.active_goal_count, "0")} / ${stringValue(planningSummary?.active_task_count, "0")}`,
      detail: "Goals / tasks",
      note: "Visible focus instead of hidden process.",
    },
    {
      placement: "right",
      eyebrow: "Action",
      value: stringValue(toolsOverview?.summary.provider_ready_count, "0"),
      detail: "Ready capabilities",
      note: "Execution stays safely product-bounded.",
    },
  ];
  const dashboardGuidanceCards = [
    {
      title: "Deep work window",
      body: stringValue(planningSummary?.active_goal_count, "0") === "0"
        ? "Shape one meaningful goal to give the day a stronger center."
        : "Your active goals are ready for a focused work block.",
      action: "Focus",
    },
    {
      title: "Build momentum",
      body: latestUserMessage
        ? `Stay close to your latest thread: ${truncateText(latestUserMessage, 72)}`
        : "The next message can become the anchor for a clearer plan.",
      action: "View goal",
    },
    {
      title: "Reflect and integrate",
      body: stringValue(knowledgeSummary?.affective_conclusion_count, "0") === "0"
        ? "A short reflection can start your first layer of deeper learning."
        : "Recent reflections are ready to inform the next response.",
      action: "Reflect",
    },
    {
      title: "Connection opportunity",
      body: recentChannelsLabel === copy.common.noData
        ? "Link another surface when you want continuity outside the web shell."
        : `Continuity is already alive across: ${recentChannelsLabel}.`,
      action: "See context",
    },
  ];
  const dashboardCognitiveSteps = [
    { token: "O", title: "Observe", detail: "Input" },
    { token: "U", title: "Understand", detail: "Intent" },
    { token: "C", title: "Connect", detail: "Pattern" },
    { token: "R", title: "Reflect", detail: "Insight", active: true },
    { token: "P", title: "Plan", detail: "Path" },
    { token: "A", title: "Act", detail: "Delivery" },
  ];
  const dashboardGoalRows = [
    { title: "Build a stronger daily rhythm", value: "72%" },
    { title: "Improve continuity across channels", value: "58%" },
    { title: "Capture reusable insights", value: "41%" },
    { title: "Shape a more embodied personality", value: "33%" },
  ];
  const dashboardMemoryBars = [
    { label: "Mon", height: "18%" },
    { label: "Tue", height: "30%" },
    { label: "Wed", height: "52%" },
    { label: "Thu", height: "44%" },
    { label: "Fri", height: "68%" },
    { label: "Sat", height: "90%" },
    { label: "Sun", height: "76%" },
  ];
  const dashboardReflectionRows = [
    { title: "Clarity on the next chapter", tag: "Clarity" },
    { title: "Decision framework update", tag: "Growth" },
    { title: "Values realignment", tag: "Alignment" },
    { title: "Letting go of distractions", tag: "Awareness" },
  ];
  const dashboardCurrentPhase = {
    title: "Reflect",
    body: "Generating insight from recent experiences, active goals, and the latest conversation context.",
  };
  const dashboardBottomStats = [
    { label: "System harmony", value: "92%", detail: "Optimal" },
    { label: "Conscious", value: "High", detail: "Balance across layers" },
    { label: "Subconscious", value: "Strong", detail: "Pattern depth" },
  ];
  const personalityLayers = [
    {
      zone: "Head · identity",
      title: "Identity",
      symbol: "◌",
      body: "Profile continuity, learned preferences, and language posture shape how the personality recognizes the current relationship.",
      highlights: [
        currentUserLabel,
        `${stringValue(preferenceSummary?.learned_preference_count, "0")} learned preferences`,
      ],
    },
    {
      zone: "Near head · planning",
      title: "Planning",
      symbol: "⌁",
      body: "Goals, tasks, and milestones stay visible as the active foreground direction instead of remaining hidden in raw payloads.",
      highlights: [
        `${stringValue(planningSummary?.active_goal_count, "0")} goals`,
        `${stringValue(planningSummary?.active_task_count, "0")} tasks`,
      ],
    },
    {
      zone: "Hand · learned knowledge",
      title: "Learned knowledge",
      symbol: "✦",
      body: "Patterns and affective takeaways become a reusable memory surface that supports future replies without overwhelming the route.",
      highlights: [
        `${stringValue(knowledgeSummary?.semantic_conclusion_count, "0")} semantic conclusions`,
        `${stringValue(knowledgeSummary?.affective_conclusion_count, "0")} affective conclusions`,
      ],
    },
    {
      zone: "Body · role + skills",
      title: "Role and skills",
      symbol: "↗",
      body: "Role posture and skill availability stay visible as product capabilities, while execution boundaries remain safely backend-owned.",
      highlights: [
        ...summaryLines("role_skill_state", overview?.role_skill_state ?? {}).slice(0, 2),
      ],
    },
  ];
  const personalityFlowItems = [
    {
      eyebrow: "Conscious loop",
      title: "Perception to expression",
      body: "Foreground cognition stays readable: context, motivation, role, planning, and expression all map into visible product zones.",
    },
    {
      eyebrow: "Action boundary",
      title: "Action and side effects",
      body: "Useful capabilities stay visible without moving execution authority into the client.",
    },
    {
      eyebrow: "Subconscious loop",
      title: "Memory and reflection",
      body: "Reflection remains a slower background layer that shapes continuity over time instead of crowding the live route.",
    },
  ];
  const toolsHeroChips = [
    `${stringValue(toolsOverview?.summary.provider_ready_count, "0")} ready`,
    `${stringValue(toolsOverview?.summary.link_required_count, "0")} needs linking`,
    `${stringValue(toolsOverview?.summary.integral_enabled_count, "0")} always on`,
  ];
  const settingsHeroChips = [
    localeOptionDisplay(selectedUiLanguageMetadata, resolvedUiLanguage),
    selectedUtcOffsetMetadata.value,
    Boolean(me?.settings.proactive_opt_in) ? copy.common.on : copy.common.off,
  ];
  const shellNavItems = [
    {
      route: "/dashboard" as const,
      label: routeLabel("/dashboard", resolvedUiLanguage),
      description: "Flagship overview",
      token: "D",
    },
    {
      route: "/chat" as const,
      label: routeLabel("/chat", resolvedUiLanguage),
      description: "Active conversation",
      token: "C",
    },
    {
      route: "/personality" as const,
      label: routeLabel("/personality", resolvedUiLanguage),
      description: "Identity map",
      token: "P",
    },
    {
      route: "/tools" as const,
      label: routeLabel("/tools", resolvedUiLanguage),
      description: "Connected capabilities",
      token: "T",
    },
    {
      route: "/settings" as const,
      label: routeLabel("/settings", resolvedUiLanguage),
      description: "Profile and shell",
      token: "S",
    },
  ];
  const chatTopControls = [
    {
      label: "Memory continuity",
      value: Boolean(preferenceSummary?.learned_preference_count) ? copy.common.on : copy.common.off,
    },
    {
      label: "Language",
      value: stringValue(me?.settings.preferred_language, copy.common.system).toUpperCase(),
    },
    {
      label: "Linked channels",
      value: recentChannelsLabel,
    },
  ];
  const chatQuickActions = ["Plan my day", "Summarize", "What did I learn?", "Brainstorm"];
  const chatComposerTools = ["Attach", "Voice", "Memory", "Tools"];
  const chatCurrentFocus =
    stringValue(planningSummary?.active_goal_count, "0") !== "0" ? "Project planning" : "Conversation continuity";
  const chatSupportCards = [
    {
      eyebrow: "Intent",
      title: chatCurrentFocus,
      body:
        chatCurrentFocus === "Project planning"
          ? "Create a meaningful next plan around your active priorities."
          : "Stay close to the current conversation and keep continuity steady.",
      accent: "Clarity & planning",
    },
    {
      eyebrow: "Memory highlights",
      title: `${stringValue(preferenceSummary?.learned_preference_count, "0")} learned cues`,
      body:
        Boolean(preferenceSummary?.learned_preference_count)
          ? "The personality can lean on earlier preferences and remembered patterns from your shared work."
          : "The conversation is ready to collect the first continuity signals that matter to you.",
      accent: "Continuity",
    },
  ];
  const chatFeatures = [
    {
      token: "C",
      title: "Continuity",
      body: "Remembers what matters between sessions without turning chat into an admin view.",
    },
    {
      token: "L",
      title: "Linked channels",
      body: "Keeps one conversation posture across the app and connected touchpoints.",
    },
    {
      token: "M",
      title: "Memory",
      body: "Turns useful moments into a calmer, more personal long-term context.",
    },
    {
      token: "P",
      title: "Privacy",
      body: "Preserves a high-trust tone so the workspace stays personal, not extractive.",
    },
  ];
  const chatActiveSummary = "Live";
  const personalityPreviewCallouts = [
    {
      key: "identity",
      className: "aion-personality-callout aion-personality-callout-identity",
      eyebrow: "Identity",
      title: "Stable",
      body: currentUserLabel,
    },
    {
      key: "knowledge",
      className: "aion-personality-callout aion-personality-callout-knowledge",
      eyebrow: "Learned knowledge",
      title: `${stringValue(knowledgeSummary?.semantic_conclusion_count, "0")} patterns`,
      body: "Books, concepts, and reusable insights.",
    },
    {
      key: "planning",
      className: "aion-personality-callout aion-personality-callout-planning",
      eyebrow: "Planning",
      title: `${stringValue(planningSummary?.active_goal_count, "0")} active goals`,
      body: "Current focus and next milestones.",
    },
    {
      key: "skills",
      className: "aion-personality-callout aion-personality-callout-skills",
      eyebrow: "Skills",
      title: stringValue((overview?.role_skill_state as Record<string, unknown> | undefined)?.skill_count, "18"),
      body: "Visible capabilities and tools.",
    },
    {
      key: "role",
      className: "aion-personality-role-card",
      eyebrow: "Role",
      title: "Advisor & creator",
      body: "Strategic, thoughtful, supportive.",
    },
  ];
  const personalityTimelineRows = [
    {
      token: "M",
      title: "Memory",
      detail: "Experiences and stored recall",
      value: `${stringValue(knowledgeSummary?.semantic_conclusion_count, "0")} notes`,
    },
    {
      token: "R",
      title: "Reflection",
      detail: "Insights and slower learning",
      value: `${stringValue(knowledgeSummary?.affective_conclusion_count, "0")} insights`,
    },
    {
      token: "C",
      title: "Context",
      detail: "Environment and active inputs",
      value: recentChannelsLabel,
    },
    {
      token: "M",
      title: "Motivation",
      detail: "Drivers, values, and current goals",
      value: `${stringValue(planningSummary?.active_goal_count, "0")} aligned`,
    },
    {
      token: "A",
      title: "Action",
      detail: "Tasks and execution posture",
      value: `${stringValue(planningSummary?.active_task_count, "0")} active`,
    },
    {
      token: "E",
      title: "Expression",
      detail: "Communication style and language",
      value: stringValue(me?.settings.preferred_language, "adaptive"),
    },
  ];
  const personalityConsciousSignals = [
    { label: "Focus", value: stringValue(planningSummary?.active_goal_count, "0") !== "0" ? "High" : "Steady" },
    { label: "Clarity", value: "87%" },
    { label: "Energy", value: "Steady" },
    { label: "Load", value: stringValue(planningSummary?.active_task_count, "0") === "0" ? "Light" : "Moderate" },
  ];
  const personalitySubconsciousSignals = [
    { label: "Patterns", value: `${stringValue(knowledgeSummary?.semantic_conclusion_count, "0")}` },
    { label: "Associations", value: `${stringValue(knowledgeSummary?.affective_conclusion_count, "0")}` },
    { label: "Preferences", value: `${stringValue(preferenceSummary?.learned_preference_count, "0")}` },
    { label: "Intuition", value: "Strong" },
  ];
  const personalityRecentActivity = [
    { title: "Updated project plan", when: "2h ago" },
    { title: "Completed reflection cycle", when: "5h ago" },
    { title: "Learned preference captured", when: "Yesterday" },
  ];
  const personalityPreviewTabs = ["Overview", "Knowledge", "Skills", "Memories", "Settings"];

  function changeRoute(nextRoute: RoutePath) {
    startTransition(() => {
      navigate(nextRoute);
      setRoute(nextRoute);
    });
  }

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
        uiLanguage: normalizeUiLanguage(snapshot.settings.ui_language),
        utcOffset: normalizeUtcOffset(snapshot.settings.utc_offset),
        proactiveOptIn: Boolean(snapshot.settings.proactive_opt_in),
      });
      setAuthForm({ email: authForm.email, password: "", displayName: authForm.displayName });
      setToast(authMode === "login" ? "You're back in." : "Your account is ready.");
      startTransition(() => {
        navigate("/dashboard");
        setRoute("/dashboard");
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
      setToolsOverview(null);
      setTelegramLinkStart(null);
      setHistory([]);
      setPendingChatMessage(null);
      setToast("You have been signed out.");
      startTransition(() => {
        navigate("/login");
        setRoute("/login");
      });
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Failed to sign out.");
    }
  }

  async function handleResetData() {
    if (!me || resetConfirmationText.trim() !== RESET_DATA_CONFIRMATION_TEXT) {
      return;
    }

    setResettingData(true);
    setError(null);

    try {
      const summary: AppResetDataResponse = await api.resetData(resetConfirmationText.trim());
      setMe(null);
      setOverview(null);
      setToolsOverview(null);
      setTelegramLinkStart(null);
      setHistory([]);
      setPendingChatMessage(null);
      setResetConfirmationText("");
      setToast(`${copy.settings.resetSuccess} ${summary.total_deleted_records} items cleared.`);
      startTransition(() => {
        navigate("/login");
        setRoute("/login");
      });
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Failed to reset runtime data.");
    } finally {
      setResettingData(false);
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
        ui_language: settingsDraft.uiLanguage,
        utc_offset: settingsDraft.utcOffset,
        proactive_opt_in: settingsDraft.proactiveOptIn,
      });
      const freshMe = await refreshMe();
      setSettingsDraft({
        displayName: freshMe.user.display_name ?? "",
        uiLanguage: normalizeUiLanguage(nextSettings.ui_language),
        utcOffset: normalizeUtcOffset(nextSettings.utc_offset),
        proactiveOptIn: Boolean(nextSettings.proactive_opt_in),
      });
      setToast("Your changes have been saved.");
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
    setChatText("");

    try {
      const reply = await api.sendChatMessage(text);
      const pendingMessageId = `${reply.event_id}:assistant`;
      pendingAssistantScrollIdRef.current = pendingMessageId;
      setPendingChatMessage({
        message_id: pendingMessageId,
        event_id: reply.event_id,
        role: "assistant",
        text: reply.reply.message,
        channel: reply.reply.channel,
        timestamp: new Date().toISOString(),
        metadata: {
          language: reply.reply.language,
          tone: reply.reply.tone,
          runtime_role: reply.runtime?.role ?? null,
          action_status: reply.runtime?.action_status ?? null,
        },
      });
      const freshHistory = await api.getChatHistory();
      setHistory(freshHistory.items);
      setPendingChatMessage(null);
    } catch (caught) {
      setPendingChatMessage(null);
      setError(caught instanceof Error ? caught.message : "Message delivery failed.");
    } finally {
      setSendingMessage(false);
    }
  }

  async function handleToolToggle(toolId: string, nextValue: boolean) {
    const payloadByToolId: Record<string, Record<string, boolean>> = {
      telegram: { telegram_enabled: nextValue },
      clickup: { clickup_enabled: nextValue },
      google_calendar: { google_calendar_enabled: nextValue },
      google_drive: { google_drive_enabled: nextValue },
    };

    const payload = payloadByToolId[toolId];
    if (!payload) {
      return;
    }

    setSavingToolId(toolId);
    setError(null);

    try {
      const nextOverview = await api.patchToolsPreferences(payload);
      setToolsOverview(nextOverview);
      if (toolId === "telegram" && !nextValue) {
        setTelegramLinkStart(null);
      }
      setToast("Your tool choices have been saved.");
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Failed to save tool preference.");
    } finally {
      setSavingToolId(null);
    }
  }

  async function handleStartTelegramLink() {
    setTelegramLinkBusy(true);
    setError(null);

    try {
      const linkStart = await api.startTelegramLink();
      const nextOverview = await api.getToolsOverview();
      setTelegramLinkStart(linkStart);
      setToolsOverview(nextOverview);
      setToast("Your Telegram link code is ready.");
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Failed to start Telegram linking.");
    } finally {
      setTelegramLinkBusy(false);
    }
  }

  if (initializing) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-base-100 px-6 text-base-content">
        <div className="w-full max-w-md">
          <StatePanel
            tone="neutral"
            title={copy.common.stateLoadingTitle}
            body="Checking your session and opening your workspace."
            loading
          />
        </div>
      </div>
    );
  }

  if (!me) {
    return (
      <div className="min-h-screen bg-base-100 text-base-content">
        <div className="mx-auto flex min-h-screen max-w-7xl flex-col px-5 py-6 sm:px-6 md:px-8 md:py-8 xl:px-10">
          <header className="mb-8 overflow-hidden rounded-[2rem] border border-base-300 bg-hero-glow shadow-halo">
            <div className="grid gap-6 px-5 py-6 md:gap-8 md:px-8 md:py-8 lg:grid-cols-[1.2fr_0.9fr] xl:px-10">
              <div className="space-y-5">
                <p className="text-sm uppercase tracking-[0.24em] text-base-900">{copy.auth.badge}</p>
                <div className="space-y-3">
                  <h1 className="font-display text-4xl leading-tight text-base-900 md:text-6xl">
                    {copy.auth.heroTitle}
                  </h1>
                  <p className="max-w-2xl text-base leading-7 text-base-800 md:text-lg">
                    {copy.auth.heroBody}
                  </p>
                </div>
                <div className="grid gap-3 sm:grid-cols-3">
                  {copy.auth.trustCards.map((card) => (
                    <article key={card.title} className="rounded-[1.5rem] bg-base-100/75 p-4 backdrop-blur">
                      <p className="font-display text-lg text-base-900">{card.title}</p>
                      <p className="mt-2 text-sm leading-7 text-base-800">{card.body}</p>
                    </article>
                  ))}
                </div>
              </div>

              <div className="grid gap-4 rounded-[1.5rem] border border-base-300 bg-base-100/80 p-4 backdrop-blur">
                <div className="rounded-2xl bg-base-200 p-5">
                  <p className="text-sm uppercase tracking-[0.24em] text-base-800">{copy.auth.trustTitle}</p>
                  <div className="mt-4 grid gap-3">
                    {copy.auth.trustCards.map((card, index) => (
                      <div key={card.title} className="rounded-[1.25rem] bg-base-100 px-4 py-4">
                        <div className="flex items-start gap-3">
                          <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-base-900 font-display text-sm text-signal-gold">
                            {index + 1}
                          </span>
                          <div>
                            <p className="font-display text-xl text-base-900">{card.title}</p>
                            <p className="mt-2 text-sm leading-7 text-base-800">{card.body}</p>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          </header>

          <main className="grid gap-5 md:gap-6 lg:grid-cols-[1.05fr_1.15fr]">
            <section className="rounded-[2rem] border border-base-300 bg-base-200 p-6">
              <div className="mb-6">
                <div>
                  <p className="text-sm uppercase tracking-[0.24em] text-base-800">{copy.auth.sessionEntry}</p>
                  <h2 className="font-display text-3xl text-base-900">
                    {authMode === "login" ? copy.auth.login : copy.auth.register}
                  </h2>
                </div>
              </div>

              <div className="tabs tabs-boxed mb-5 w-fit bg-base-100">
                <button
                  className={`tab ${authMode === "login" ? "tab-active" : ""}`}
                  onClick={() => setAuthMode("login")}
                  type="button"
                >
                  {copy.auth.tabsLogin}
                </button>
                <button
                  className={`tab ${authMode === "register" ? "tab-active" : ""}`}
                  onClick={() => setAuthMode("register")}
                  type="button"
                >
                  {copy.auth.tabsRegister}
                </button>
              </div>

              <form className="space-y-4" onSubmit={(event) => void handleAuthSubmit(event)}>
                <label className="form-control w-full">
                    <div className="label">
                    <span className="label-text text-base-900">{copy.auth.email}</span>
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
                    <span className="label-text text-base-900">{copy.auth.password}</span>
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
                      <span className="label-text text-base-900">{copy.auth.displayName}</span>
                    </div>
                    <input
                      className="input input-bordered w-full"
                      type="text"
                      value={authForm.displayName}
                      onChange={(event) => setAuthForm((form) => ({ ...form, displayName: event.target.value }))}
                      placeholder="How the personality should address you"
                    />
                  </label>
                ) : null}

                <button className="btn btn-primary btn-block" disabled={authBusy} type="submit">
                  {authBusy ? copy.common.loading : authMode === "login" ? copy.auth.enterWorkspace : copy.auth.createAccount}
                </button>
              </form>

              {errorBody ? (
                <div className="mt-4">
                  <FeedbackBanner
                    tone="error"
                    title={copy.common.stateErrorTitle}
                    body={errorBody}
                    detail={errorDetail}
                    detailLabel={copy.common.stateDetailLabel}
                  />
                </div>
              ) : null}
            </section>

            <section className="grid gap-4">
              {[
                {
                  title: "Continue in one place",
                  body: "Move from sign-in straight into chat, settings, tools, and personality context without a fragmented shell.",
                },
                {
                  title: "Stay oriented",
                  body: "The product keeps the main actions close so returning to Aviary feels lightweight instead of procedural.",
                },
                {
                  title: "Keep ownership",
                  body: "Your account remains yours: preferences are editable and runtime data can be reset later when needed.",
                },
              ].map((section) => (
                <article
                  key={section.title}
                  className="rounded-[1.75rem] border border-base-300 bg-base-100 p-6 transition-transform duration-200 hover:-translate-y-1"
                >
                  <h2 className="mb-3 font-display text-2xl text-base-900">{section.title}</h2>
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
    <div className="aion-shell min-h-screen text-base-content">
      <div className="mx-auto max-w-[112rem] px-4 pb-24 pt-4 sm:px-5 md:px-6 md:pb-8 md:pt-5 xl:px-8">
        <div className="aion-shell-frame grid gap-4 xl:grid-cols-[13rem_minmax(0,1fr)]">
          <aside className="aion-app-rail hidden xl:flex xl:min-h-[calc(100vh-3rem)] xl:flex-col">
            <div>
              <AviaryWordmark className="max-w-full" />
              <p className="mt-2 text-sm text-base-800">Your conscious companion</p>
            </div>

            <nav className="mt-8 grid gap-2">
              {shellNavItems.map((item) => (
                <ShellNavButton
                  key={item.route}
                  label={item.label}
                  description={item.description}
                  active={route === item.route}
                  token={item.token}
                  onClick={() => changeRoute(item.route)}
                />
              ))}
            </nav>

            <div className="mt-auto grid gap-3">
              <section className="aion-panel-soft aion-rail-health rounded-[1.8rem] p-4">
                <p className="text-xs uppercase tracking-[0.2em] text-base-800">System health</p>
                <div className="aion-rail-health-orb" aria-hidden="true">
                  <span>92%</span>
                </div>
                <p className="text-base font-semibold text-base-900">Optimal</p>
                <p className="mt-2 text-sm leading-6 text-base-800">All systems aligned and ready for thoughtful work.</p>
              </section>

              <section className="aion-panel-soft rounded-[1.8rem] p-4">
                <p className="text-xs uppercase tracking-[0.2em] text-base-800">{copy.common.signedInAs}</p>
                <p className="mt-3 font-display text-xl text-base-900">{currentUserLabel}</p>
                <p className="mt-1 text-sm text-base-800">{me.user.email}</p>
                <div className="mt-4 flex flex-wrap gap-2">
                  {accountSummaryItems.slice(0, 2).map((item) => (
                    <span key={item.label} className="aion-chip-ghost rounded-full px-3 py-1 text-xs font-medium">
                      {item.value}
                    </span>
                  ))}
                </div>
                <button className="btn btn-outline mt-4 w-full" onClick={() => void handleLogout()} type="button">
                  {copy.common.signOut}
                </button>
              </section>

              <section className="aion-panel-soft aion-rail-story rounded-[1.8rem] p-4">
                <p className="text-base font-semibold leading-7 text-base-900">“Clarity is the lamp that makes the path.”</p>
                <div className="mt-4">
                  <AviaryWordmark compact />
                </div>
              </section>
            </div>
          </aside>

          <div className="aion-shell-stage grid gap-4">
            <ShellUtilityBar
              currentSurface={routeLabel(route, resolvedUiLanguage)}
              currentUserLabel={currentUserLabel}
              accountPanelOpen={accountPanelOpen}
              onAccountClick={() => setAccountPanelOpen((value) => !value)}
            />

            <header className="aion-panel rounded-[2rem] xl:hidden">
              <div className="flex flex-wrap items-center gap-3 px-4 py-4 sm:px-5">
                <div className="min-w-0 flex-1">
                  <div className="flex flex-wrap items-center gap-3">
                    <div className="aion-wordmark-mobile-badge">
                      <AviaryWordmark compact />
                    </div>
                    <p className="text-xs uppercase tracking-[0.18em] text-base-800">
                      {copy.common.build} {BUILD_REVISION.slice(0, 12)}
                    </p>
                  </div>
                  <div className="mt-3">
                    <p className="text-xs uppercase tracking-[0.24em] text-base-800">{copy.common.workspace}</p>
                    <h1 className="font-display text-2xl text-base-900 sm:text-3xl">{routeLabel(route, resolvedUiLanguage)}</h1>
                  </div>
                </div>

                <button
                  className={`btn btn-sm ${accountPanelOpen ? "btn-primary" : "btn-outline"}`}
                  onClick={() => setAccountPanelOpen((value) => !value)}
                  type="button"
                >
                  {copy.common.account}
                </button>
              </div>

              <div className="border-t border-base-300/70 px-4 py-3 sm:px-5">
                <div className="flex gap-2 overflow-x-auto pb-1">
                  {ROUTES.map((entry) => (
                    <button
                      key={entry}
                      className={`btn btn-sm whitespace-nowrap ${route === entry ? "btn-primary" : "btn-ghost border border-base-300"}`}
                      onClick={() => changeRoute(entry)}
                      type="button"
                    >
                      {routeLabel(entry, resolvedUiLanguage)}
                    </button>
                  ))}
                </div>
              </div>
            </header>

            {accountPanelOpen ? (
              <section className="aion-panel-soft rounded-[1.8rem] p-4 xl:hidden">
                <div className="grid gap-3 lg:grid-cols-[minmax(0,1.1fr)_minmax(0,0.9fr)]">
                  <div className="aion-panel-soft rounded-[1.4rem] p-4">
                    <p className="text-sm uppercase tracking-[0.24em] text-base-800">{copy.common.signedInAs}</p>
                    <p className="mt-2 font-display text-2xl text-base-900">{currentUserLabel}</p>
                    <p className="mt-1 text-sm text-base-800">{me.user.email}</p>
                  </div>
                  <div className="grid gap-3 sm:grid-cols-[minmax(0,1fr)_auto]">
                    <div className="grid gap-3 sm:grid-cols-2">
                      {accountSummaryItems.map((item) => (
                        <div key={item.label} className="aion-panel-soft rounded-[1.4rem] p-4">
                          <p className="text-xs uppercase tracking-[0.18em] text-base-800">{item.label}</p>
                          <p className="mt-2 text-base font-semibold text-base-900">{item.value}</p>
                        </div>
                      ))}
                    </div>
                    <button className="btn btn-outline sm:self-end" onClick={() => void handleLogout()} type="button">
                      {copy.common.signOut}
                    </button>
                  </div>
                </div>
              </section>
            ) : null}

            {successBody ? (
              <FeedbackBanner
                tone="success"
                title={copy.common.stateSuccessTitle}
                body={successBody}
                detailLabel={copy.common.stateDetailLabel}
              />
            ) : null}

            {errorBody ? (
              <FeedbackBanner
                tone="error"
                title={copy.common.stateErrorTitle}
                body={errorBody}
                detail={errorDetail}
                detailLabel={copy.common.stateDetailLabel}
              />
            ) : null}

            <main className="flex-1">
          {route === "/dashboard" ? (
            <section className="grid gap-4">
              <section className="aion-panel aion-dashboard-stage">
                <div className="aion-dashboard-stage-main">
                  <div className="aion-dashboard-stage-copy">
                    <span className="aion-chat-headline-emblem">✦</span>
                    <div>
                      <p className="text-xs uppercase tracking-[0.24em] text-[#8d785f]">Good morning</p>
                      <h2 className="mt-2 font-display text-4xl text-base-900">
                        Welcome back, {currentUserLabel}
                      </h2>
                      <p className="mt-3 max-w-2xl text-sm leading-7 text-base-800">
                        Here is what feels most alive in your Aviary workspace today.
                      </p>
                      <div className="mt-4 flex flex-wrap gap-2">
                        {dashboardHeroChips.map((chip) => (
                          <span
                            key={chip}
                            className="aion-chip-ghost rounded-full px-3 py-2 text-[11px] font-semibold uppercase tracking-[0.18em]"
                          >
                            {chip}
                          </span>
                        ))}
                      </div>
                    </div>
                  </div>

                  <div className="aion-dashboard-hero-grid">
                    <div className="aion-dashboard-signal-column">
                      {dashboardSignalCards
                        .filter((card) => card.placement === "left")
                        .map((card) => (
                          <article key={card.eyebrow} className="aion-dashboard-signal-card">
                            <p className="aion-dashboard-signal-eyebrow">{card.eyebrow}</p>
                            <p className="aion-dashboard-signal-value">{card.value}</p>
                            <p className="aion-dashboard-signal-detail">{card.detail}</p>
                            <div className="aion-dashboard-signal-wave" aria-hidden="true" />
                            <p className="aion-dashboard-signal-note">{card.note}</p>
                          </article>
                        ))}
                    </div>

                    <div className="aion-dashboard-figure-stage">
                      <div className="aion-dashboard-figure-atmosphere" aria-hidden="true" />
                      <div className="aion-dashboard-figure-halo" aria-hidden="true" />
                      <img
                        className="aion-dashboard-figure-image"
                        src="/aion-personality-figure-reference-v1.png"
                        alt="Embodied personality overview"
                      />
                      <div className="aion-dashboard-figure-caption">
                        <p className="aion-dashboard-figure-caption-label">Embodied cognition field</p>
                        <p className="aion-dashboard-figure-caption-copy">
                          Identity, memory, planning, and reflection staying visible in one calm orchestration space.
                        </p>
                      </div>
                      <div className="aion-dashboard-figure-badge">
                        <span className="aion-dashboard-figure-badge-core">✦</span>
                      </div>
                    </div>

                    <div className="aion-dashboard-signal-column">
                      {dashboardSignalCards
                        .filter((card) => card.placement === "right")
                        .map((card) => (
                          <article key={card.eyebrow} className="aion-dashboard-signal-card">
                            <p className="aion-dashboard-signal-eyebrow">{card.eyebrow}</p>
                            <p className="aion-dashboard-signal-value">{card.value}</p>
                            <p className="aion-dashboard-signal-detail">{card.detail}</p>
                            <div className="aion-dashboard-signal-wave" aria-hidden="true" />
                            <p className="aion-dashboard-signal-note">{card.note}</p>
                          </article>
                        ))}
                    </div>
                  </div>
                </div>

                <aside className="aion-dashboard-guidance-panel">
                  <div className="mb-5">
                    <p className="text-sm uppercase tracking-[0.22em] text-base-800">Insights and guidance</p>
                    <h3 className="mt-2 font-display text-2xl text-base-900">Curated for you</h3>
                  </div>
                  <div className="grid gap-3">
                    {dashboardGuidanceCards.map((card, index) => (
                      <article
                        key={card.title}
                        className={`aion-dashboard-guidance-card ${
                          index === 0
                            ? "aion-dashboard-guidance-card-primary"
                            : index === 1
                              ? "aion-dashboard-guidance-card-secondary"
                              : "aion-dashboard-guidance-card-tertiary"
                        }`}
                      >
                        <div>
                          <p className="text-base font-semibold text-base-900">{card.title}</p>
                          <p className="mt-2 text-sm leading-6 text-base-800">{card.body}</p>
                        </div>
                        <button className="aion-dashboard-mini-action" type="button">
                          {card.action}
                        </button>
                      </article>
                    ))}
                  </div>

                  <section className="aion-dashboard-recent-panel">
                    <div className="mb-4 flex items-center justify-between gap-3">
                      <div>
                        <p className="text-sm uppercase tracking-[0.22em] text-base-800">Recent activity</p>
                        <h4 className="mt-2 font-display text-xl text-base-900">What just changed</h4>
                      </div>
                      <button className="aion-dashboard-link" type="button">
                        View all
                      </button>
                    </div>
                    <div className="grid gap-3">
                      {personalityRecentActivity.map((item) => (
                        <article key={item.title} className="aion-dashboard-recent-row">
                          <div>
                            <p className="text-sm font-semibold text-base-900">{item.title}</p>
                            <p className="mt-1 text-sm text-base-800">Captured in the living continuity layer.</p>
                          </div>
                          <span className="text-xs uppercase tracking-[0.18em] text-base-800">{item.when}</span>
                        </article>
                      ))}
                    </div>
                  </section>

                  <section className="aion-dashboard-side-story">
                    <p className="text-sm uppercase tracking-[0.22em] text-base-800">Today's intention</p>
                    <p className="mt-4 font-display text-2xl leading-tight text-base-900">
                      Create with clarity.
                      <br />
                      Serve with purpose.
                    </p>
                  </section>
                </aside>
              </section>

              <section className="aion-panel aion-dashboard-flow-panel">
                <div className="aion-dashboard-flow-header">
                  <div>
                    <p className="text-sm uppercase tracking-[0.22em] text-base-800">Cognitive flow</p>
                    <h3 className="mt-2 font-display text-2xl text-base-900">Live orchestration</h3>
                  </div>
                  <div className="aion-chip-ghost rounded-full px-3 py-2 text-xs font-semibold uppercase tracking-[0.18em]">
                    Current phase: Reflect
                  </div>
                </div>
                <div className="aion-dashboard-flow-layout">
                  <div className="aion-dashboard-flow-track">
                    {dashboardCognitiveSteps.map((step) => (
                      <article
                        key={step.title}
                        className={`aion-dashboard-flow-step ${step.active ? "aion-dashboard-flow-step-active" : ""}`}
                      >
                        <span className="aion-dashboard-flow-icon">{step.token}</span>
                        <p className="mt-3 text-base font-semibold text-base-900">{step.title}</p>
                        <p className="mt-1 text-sm text-base-800">{step.detail}</p>
                      </article>
                    ))}
                  </div>
                  <aside className="aion-dashboard-flow-sidecard">
                    <p className="text-sm uppercase tracking-[0.2em] text-base-800">Current phase</p>
                    <p className="mt-3 font-display text-3xl text-base-900">{dashboardCurrentPhase.title}</p>
                    <p className="mt-3 text-sm leading-7 text-base-800">{dashboardCurrentPhase.body}</p>
                    <button className="aion-dashboard-action-button mt-5" type="button">
                      View full flow
                    </button>
                  </aside>
                </div>
                <div className="aion-dashboard-flow-notes">
                  {dashboardFlowItems.map((item) => (
                    <article key={item.title} className="aion-dashboard-flow-note">
                      <p className="text-[11px] uppercase tracking-[0.2em] text-base-800">{item.eyebrow}</p>
                      <p className="mt-2 text-base font-semibold text-base-900">{item.title}</p>
                      <p className="mt-2 text-sm leading-6 text-base-800">{item.body}</p>
                    </article>
                  ))}
                </div>
              </section>

              <section className="grid gap-4 xl:grid-cols-[minmax(0,1fr)_minmax(0,0.8fr)_minmax(0,0.9fr)]">
                <article className="aion-panel-soft aion-dashboard-card">
                  <div className="flex items-center justify-between gap-3">
                    <div>
                      <p className="text-sm uppercase tracking-[0.2em] text-base-800">Active goals</p>
                      <h3 className="mt-2 font-display text-2xl text-base-900">What is in motion</h3>
                    </div>
                    <button className="aion-dashboard-link" type="button">
                      View all
                    </button>
                  </div>
                  <div className="mt-5 grid gap-4">
                    {dashboardGoalRows.map((goal) => (
                      <div key={goal.title}>
                        <div className="flex items-center justify-between gap-3 text-sm text-base-900">
                          <span>{goal.title}</span>
                          <span>{goal.value}</span>
                        </div>
                        <div className="aion-dashboard-progress mt-2">
                          <span style={{ width: goal.value }} />
                        </div>
                      </div>
                    ))}
                  </div>
                </article>

                <article className="aion-panel-soft aion-dashboard-card">
                  <p className="text-sm uppercase tracking-[0.2em] text-base-800">Current focus</p>
                  <div className="aion-dashboard-focus-orb" aria-hidden="true" />
                  <p className="font-display text-2xl text-base-900">{chatCurrentFocus}</p>
                  <p className="mt-3 text-sm leading-7 text-base-800">
                    Building a coherent next step from your active conversation, memory, and planning posture.
                  </p>
                  <button className="aion-dashboard-action-button mt-5" type="button">
                    Enter focus
                  </button>
                </article>

                <article className="aion-panel-soft aion-dashboard-card">
                  <div className="flex items-center justify-between gap-3">
                    <div>
                      <p className="text-sm uppercase tracking-[0.2em] text-base-800">Memory growth</p>
                      <h3 className="mt-2 font-display text-2xl text-base-900">
                        {stringValue(knowledgeSummary?.semantic_conclusion_count, "0")}
                      </h3>
                    </div>
                    <span className="aion-chip-ghost rounded-full px-3 py-2 text-xs font-semibold uppercase tracking-[0.18em]">
                      This week
                    </span>
                  </div>
                  <p className="mt-2 text-sm text-[#5f8f93]">Useful memories stored and made easier to reuse.</p>
                  <div className="aion-dashboard-bar-chart mt-6">
                    {dashboardMemoryBars.map((bar) => (
                      <div key={bar.label} className="aion-dashboard-bar-item">
                        <span className="aion-dashboard-bar-fill" style={{ height: bar.height }} />
                        <span className="aion-dashboard-bar-label">{bar.label}</span>
                      </div>
                    ))}
                  </div>
                </article>
              </section>

              <section className="grid gap-4">
                <article className="aion-panel aion-dashboard-summary-band">
                  <div className="aion-dashboard-summary-layout">
                    <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
                      {dashboardBottomStats.map((stat) => (
                        <div key={stat.label} className="aion-dashboard-summary-item">
                          <p className="text-sm uppercase tracking-[0.2em] text-base-800">{stat.label}</p>
                          <p className="mt-3 font-display text-3xl text-base-900">{stat.value}</p>
                          <p className="mt-2 text-sm text-base-800">{stat.detail}</p>
                        </div>
                      ))}
                    </div>
                    <div className="aion-dashboard-summary-scenic">
                      <div className="aion-dashboard-summary-scenic-copy">
                        <p className="text-sm uppercase tracking-[0.2em] text-base-800">Weekly summary</p>
                        <p className="mt-3 font-display text-2xl leading-tight text-base-900">
                          Meaningful progress
                          <br />
                          with steadier intention.
                        </p>
                        <p className="mt-3 max-w-md text-sm leading-7 text-base-800">
                          The shell now holds your goals, memory, and reflections in one calmer path.
                        </p>
                        <div className="mt-4 flex flex-wrap gap-2">
                          {dashboardReflectionRows.slice(0, 3).map((row) => (
                            <span
                              key={row.tag}
                              className="aion-chip-ghost rounded-full px-3 py-2 text-[11px] font-semibold uppercase tracking-[0.18em]"
                            >
                              {row.tag}
                            </span>
                          ))}
                        </div>
                        <button className="aion-dashboard-action-button mt-5" type="button">
                          See full report
                        </button>
                      </div>
                    </div>
                  </div>
                </article>
              </section>

            </section>
          ) : null}

          {route === "/chat" ? (
            <section className="grid gap-4">
              <section className="aion-chat-workspace">
                <div className="aion-chat-topbar">
                  <div className="aion-chat-headline">
                    <span className="aion-chat-headline-emblem">✦</span>
                    <div>
                    <p className="text-xs uppercase tracking-[0.24em] text-[#8d785f]">Active conversation</p>
                    <div className="mt-2 flex flex-wrap items-center gap-3">
                      <h2 className="font-display text-3xl text-base-900">{routeLabel("/chat", resolvedUiLanguage)}</h2>
                      <span className="inline-flex items-center gap-2 text-sm text-[#5f8f93]">
                        <span className="h-2 w-2 rounded-full bg-[#79b7b9]" />
                        {chatActiveSummary}
                      </span>
                    </div>
                    <p className="mt-2 text-sm leading-7 text-base-800">{routeDescription("/chat", resolvedUiLanguage)}</p>
                    </div>
                  </div>
                  <div className="aion-chat-topbar-controls">
                    {chatTopControls.map((item, index) => (
                      <div
                        key={item.label}
                        className={`aion-chat-control-pill ${
                          index === 0
                            ? "aion-chat-control-pill-emphasis"
                            : index === chatTopControls.length - 1
                              ? "aion-chat-control-pill-wide"
                              : ""
                        }`}
                      >
                        <span className="aion-chat-control-label">{item.label}</span>
                        <span className="aion-chat-control-badge">{item.value}</span>
                      </div>
                    ))}
                  </div>
                </div>

                <div className="aion-chat-stage">
                  <div className="grid gap-4">
                    <div
                      ref={transcriptContainerRef}
                      className="aion-chat-transcript"
                    >
                      {historyLoading && transcriptItems.length === 0 ? (
                        <StatePanel
                          tone="neutral"
                          title={copy.common.stateLoadingTitle}
                          body={copy.common.loading}
                          loading
                        />
                      ) : null}
                      {visibleTranscriptItems.map((message) => {
                        const metadataSummary = transcriptMetadataSummary(message);
                        const isUser = message.role === "user";
                        const isPending = pendingChatMessage?.message_id === message.message_id;

                        return (
                          <div
                            key={message.message_id}
                            ref={(node) => {
                              transcriptMessageRefs.current[message.message_id] = node;
                            }}
                            className={`aion-chat-message-row ${isUser ? "justify-end" : "justify-start"}`}
                          >
                            {!isUser ? <span className="aion-chat-avatar">A</span> : null}
                            <article className={`aion-chat-message ${isUser ? "aion-chat-message-user" : "aion-chat-message-assistant"}`}>
                              <div className="aion-chat-message-meta">
                                <span>{formatTimestamp(message.timestamp, resolvedUiLanguage)}</span>
                                {isPending ? <span>{copy.chat.pending}</span> : null}
                                {transcriptIsPreview ? <span>Starter preview</span> : null}
                              </div>
                              <p className="aion-chat-message-copy">{message.text}</p>
                              {metadataSummary && !transcriptIsPreview ? (
                                <p className="aion-chat-message-summary">{metadataSummary}</p>
                              ) : null}
                            </article>
                          </div>
                        );
                      })}
                    </div>

                    <div className="aion-chat-composer-zone">
                      <div className="aion-chat-action-tray">
                        {chatQuickActions.map((action) => (
                          <button
                            key={action}
                            className="aion-chat-action-chip"
                            type="button"
                            onClick={() => setChatText(action)}
                          >
                            {action}
                          </button>
                        ))}
                      </div>
                      <form className="aion-chat-composer" onSubmit={(event) => void handleSendMessage(event)}>
                        <div className="aion-chat-composer-primary">
                          <button className="aion-chat-icon-button" type="button" aria-label="Add context">
                            +
                          </button>
                          <div className="aion-chat-input-stack">
                            <textarea
                              className="aion-chat-input"
                              placeholder={copy.chat.placeholder}
                              value={chatText}
                              onChange={(event) => setChatText(event.target.value)}
                            />
                            <div className="aion-chat-composer-support">
                              {chatComposerTools.map((tool) => (
                                <button key={tool} className="aion-chat-support-button" type="button">
                                  {tool}
                                </button>
                              ))}
                            </div>
                          </div>
                          <button className="aion-chat-icon-button hidden sm:inline-flex" type="button" aria-label="Voice input">
                            M
                          </button>
                          <button
                            aria-label={copy.chat.send}
                            className="aion-chat-send"
                            disabled={sendingMessage}
                            type="submit"
                          >
                            {sendingMessage ? "..." : "➜"}
                          </button>
                        </div>
                      </form>
                      <p className="px-2 text-sm text-base-800">{copy.chat.composerHint}</p>
                    </div>
                  </div>

                  <aside className="aion-chat-support-column">
                    <aside className="aion-chat-portrait-panel">
                      <div className="aion-chat-portrait-overlay">
                        <p className="text-[11px] uppercase tracking-[0.22em] text-[#5f8f93]">Planning</p>
                        <p className="mt-2 font-display text-2xl text-base-900">{chatCurrentFocus}</p>
                        <div className="mt-4 space-y-2 text-sm text-base-800">
                          <div className="flex items-center justify-between gap-3">
                            <span>Current focus</span>
                            <span className="font-semibold text-base-900">High</span>
                          </div>
                          <div className="flex items-center justify-between gap-3">
                            <span>Knowledge bridge</span>
                            <span className="font-semibold text-[#5f8f93]">72%</span>
                          </div>
                        </div>
                      </div>
                      <div className="aion-chat-portrait-copy">
                        <span className="aion-chip rounded-full px-3 py-1 text-xs font-semibold uppercase tracking-[0.18em] text-base-900">
                          Embodied cognition
                        </span>
                        <p className="mt-4 max-w-[13rem] text-sm leading-7 text-base-800">
                          Understanding leads to clarity. Clarity leads to action.
                        </p>
                      </div>
                    </aside>

                    <section className="aion-chat-context-panel">
                      <div className="mb-4 flex items-center justify-between gap-3">
                        <div>
                          <p className="text-sm font-semibold text-base-900">Conversation context</p>
                          <p className="mt-1 text-sm text-[#5f8f93]">Live support</p>
                        </div>
                        <span className="aion-chat-live-dot" />
                      </div>
                      <div className="grid gap-3">
                        {chatSupportCards.map((card) => (
                          <article key={card.eyebrow} className="aion-chat-support-card">
                            <p className="text-[11px] uppercase tracking-[0.18em] text-base-800">{card.eyebrow}</p>
                            <div className="mt-2 flex items-start justify-between gap-3">
                              <h3 className="font-display text-xl text-base-900">{card.title}</h3>
                              <span className="aion-chat-support-accent">{card.accent}</span>
                            </div>
                            <p className="mt-2 text-sm leading-6 text-base-800">{card.body}</p>
                          </article>
                        ))}
                      </div>
                    </section>

                  </aside>
                </div>
              </section>
            </section>
          ) : null}

          {route === "/settings" ? (
            <div className="grid gap-6">
              <RouteHeroPanel
                eyebrow={copy.settings.eyebrow}
                title={copy.settings.title}
                body={copy.settings.subtitle}
                chips={settingsHeroChips}
              />

              <section className="aion-panel rounded-[2rem] p-5">
                <form className="grid gap-4 md:grid-cols-2" onSubmit={(event) => void handleSaveSettings(event)}>
                <section className="aion-panel-soft rounded-[1.6rem] p-4">
                  <p className="text-sm uppercase tracking-[0.2em] text-base-800">{copy.settings.profileTitle}</p>
                  <h3 className="mt-2 font-display text-2xl text-base-900">{copy.auth.displayName}</h3>
                  <p className="mt-2 text-sm leading-7 text-base-800">{copy.settings.profileBody}</p>
                  <label className="form-control mt-4">
                    <input
                      className="input input-bordered"
                      value={settingsDraft.displayName}
                      onChange={(event) =>
                        setSettingsDraft((draft) => ({ ...draft, displayName: event.target.value }))
                      }
                      placeholder={copy.auth.displayName}
                    />
                  </label>
                </section>

                <section className="aion-panel-soft rounded-[1.6rem] p-4">
                  <div className="flex flex-wrap items-start justify-between gap-3">
                    <div>
                      <p className="text-sm uppercase tracking-[0.2em] text-base-800">{copy.settings.uiLanguageTitle}</p>
                      <h3 className="mt-2 font-display text-2xl text-base-900">{copy.common.uiLanguage}</h3>
                    </div>
                    <div className="aion-chip rounded-[1rem] px-3 py-2">
                      <p className="text-[10px] uppercase tracking-[0.18em] text-base-800">{copy.common.details}</p>
                      <p className="mt-1 text-sm font-semibold text-base-900">{copy.common.interfaceOnly}</p>
                    </div>
                  </div>
                  <p className="mt-2 text-sm leading-7 text-base-800">{copy.settings.uiLanguageBody}</p>
                  <label className="form-control mt-4">
                    <select
                      className="select select-bordered"
                      value={settingsDraft.uiLanguage}
                      onChange={(event) =>
                        setSettingsDraft((draft) => ({
                          ...draft,
                          uiLanguage: normalizeUiLanguage(event.target.value),
                        }))
                      }
                    >
                      {UI_LANGUAGE_OPTIONS.map((option) => (
                        <option key={option.value} value={option.value}>
                          {localeOptionDisplay(option, resolvedUiLanguage)}
                        </option>
                      ))}
                    </select>
                  </label>
                  <p className="mt-3 text-sm text-base-800">{copy.settings.uiLanguageHelp}</p>
                </section>

                <section className="aion-panel-soft rounded-[1.6rem] p-4">
                  <p className="text-sm uppercase tracking-[0.2em] text-base-800">{copy.settings.utcOffsetTitle}</p>
                  <h3 className="mt-2 font-display text-2xl text-base-900">{copy.common.utcOffset}</h3>
                  <p className="mt-2 text-sm leading-7 text-base-800">{copy.settings.utcOffsetBody}</p>
                  <label className="form-control mt-4">
                    <select
                      className="select select-bordered"
                      value={settingsDraft.utcOffset}
                      onChange={(event) =>
                        setSettingsDraft((draft) => ({
                          ...draft,
                          utcOffset: normalizeUtcOffset(event.target.value),
                        }))
                      }
                    >
                      {UTC_OFFSET_OPTIONS.map((option) => (
                        <option key={option.value} value={option.value}>
                          {option.value}
                        </option>
                      ))}
                    </select>
                  </label>
                  <p className="mt-3 text-sm text-base-800">{copy.settings.utcOffsetHelp}</p>
                </section>

                <section className="aion-panel-soft rounded-[1.6rem] p-4">
                  <p className="text-sm uppercase tracking-[0.2em] text-base-800">{copy.settings.conversationTitle}</p>
                  <h3 className="mt-2 font-display text-2xl text-base-900">{copy.common.conversationLanguage}</h3>
                  <p className="mt-2 text-sm leading-7 text-base-800">{copy.settings.conversationBody}</p>
                  <div className="mt-4 grid gap-3 sm:grid-cols-2">
                    <div className="aion-chip rounded-[1.2rem] p-4">
                      <p className="text-xs uppercase tracking-[0.18em] text-base-800">{copy.common.sourceOfTruth}</p>
                      <p className="mt-2 text-base font-semibold text-base-900">
                        {stringValue(me.settings.preferred_language, copy.common.notSet)}
                      </p>
                    </div>
                    <div className="aion-chip rounded-[1.2rem] p-4">
                      <p className="text-xs uppercase tracking-[0.18em] text-base-800">{copy.common.details}</p>
                      <p className="mt-2 text-base font-semibold text-base-900">{selectedUtcOffsetMetadata.value}</p>
                    </div>
                  </div>
                </section>

                <section className="aion-panel-soft rounded-[1.6rem] p-4">
                  <p className="text-sm uppercase tracking-[0.2em] text-base-800">{copy.settings.proactiveTitle}</p>
                  <h3 className="mt-2 font-display text-2xl text-base-900">{copy.common.proactive}</h3>
                  <label className="mt-4 flex cursor-pointer items-start gap-3 rounded-[1.2rem] bg-base-100 px-4 py-4">
                    <input
                      className="toggle toggle-primary mt-1"
                      type="checkbox"
                      checked={settingsDraft.proactiveOptIn}
                      onChange={(event) =>
                        setSettingsDraft((draft) => ({ ...draft, proactiveOptIn: event.target.checked }))
                      }
                    />
                    <div>
                      <span className="text-base font-semibold text-base-900">{copy.settings.proactiveTitle}</span>
                      <p className="mt-1 text-sm leading-7 text-base-800">{copy.settings.proactiveBody}</p>
                    </div>
                  </label>
                </section>

                <section className="rounded-[1.6rem] border border-error/40 bg-error/5 p-4 md:col-span-2 shadow-sm">
                  <p className="text-sm uppercase tracking-[0.2em] text-error">{copy.settings.resetTitle}</p>
                  <h3 className="mt-2 font-display text-2xl text-base-900">{copy.settings.resetAction}</h3>
                  <p className="mt-3 max-w-4xl text-sm leading-7 text-base-900">{copy.settings.resetBody}</p>
                  <p className="mt-3 max-w-4xl text-sm leading-7 text-base-800">{copy.settings.resetImpact}</p>

                  <div className="mt-4 grid gap-4 lg:grid-cols-[minmax(0,1fr)_auto] lg:items-end">
                    <label className="form-control">
                      <div className="label">
                        <span className="label-text text-base-900">{copy.settings.resetConfirmationLabel}</span>
                      </div>
                      <input
                        className="input input-bordered border-error/40 bg-base-100"
                        value={resetConfirmationText}
                        onChange={(event) => setResetConfirmationText(event.target.value)}
                        placeholder={copy.settings.resetConfirmationPlaceholder}
                      />
                      <div className="label">
                        <span className="label-text text-base-800">
                          {copy.settings.resetConfirmationHint} <code>{RESET_DATA_CONFIRMATION_TEXT}</code>
                        </span>
                      </div>
                    </label>

                    <button
                      className="btn btn-error w-full lg:w-fit"
                      disabled={resettingData || resetConfirmationText.trim() !== RESET_DATA_CONFIRMATION_TEXT}
                      type="button"
                      onClick={() => {
                        void handleResetData();
                      }}
                    >
                      {resettingData ? copy.settings.resetting : copy.settings.resetAction}
                    </button>
                  </div>
                </section>

                <div className="md:col-span-2">
                  <div className="aion-panel sticky bottom-[4.5rem] rounded-[1.6rem] p-4 md:bottom-0">
                    <div className="flex flex-wrap items-center justify-between gap-3">
                      <div>
                        <p className="text-sm font-semibold text-base-900">{copy.settings.savedState}</p>
                        <p className="text-sm text-base-800">{copy.settings.saveHint}</p>
                      </div>
                      <button className="btn btn-primary w-full sm:w-fit" disabled={savingSettings} type="submit">
                        {savingSettings ? copy.common.saving : copy.common.save}
                      </button>
                    </div>
                  </div>
                </div>
              </form>
            </section>
            </div>
          ) : null}

          {route === "/tools" ? (
            <div className="grid gap-6">
              <RouteHeroPanel
                eyebrow={copy.tools.eyebrow}
                title={copy.tools.title}
                body={copy.tools.subtitle}
                chips={toolsHeroChips}
              />

              <section className="aion-panel rounded-[2rem] p-5">
                <div className="mb-5 max-w-3xl">
                  <p className="text-sm uppercase tracking-[0.24em] text-base-800">{copy.tools.eyebrow}</p>
                  <h2 className="font-display text-3xl text-base-900">{copy.tools.title}</h2>
                  <p className="mt-3 text-sm leading-7 text-base-800">{copy.tools.subtitle}</p>
                </div>

                      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
                {[
                  {
                    title: copy.tools.groupCount,
                    value: stringValue(toolsOverview?.summary.total_groups, "0"),
                    note: "Clear groups for the tools you can browse here",
                  },
                  {
                    title: copy.tools.integral,
                    value: stringValue(toolsOverview?.summary.integral_enabled_count, "0"),
                    note: "Capabilities that stay available as part of the product",
                  },
                  {
                    title: copy.tools.ready,
                    value: stringValue(toolsOverview?.summary.provider_ready_count, "0"),
                    note: "Tools that are ready to use today",
                  },
                  {
                    title: copy.tools.linkRequired,
                    value: stringValue(toolsOverview?.summary.link_required_count, "0"),
                    note: "Channels waiting for a quick linking step",
                  },
                ].map((card) => (
                  <article key={card.title} className="aion-panel-soft rounded-[1.75rem] p-5">
                    <p className="text-sm uppercase tracking-[0.22em] text-base-800">{card.title}</p>
                    <p className="mt-3 font-display text-4xl text-base-900">{card.value}</p>
                    <p className="mt-2 text-sm text-base-800">{card.note}</p>
                  </article>
                ))}
                </div>
              </section>

              <section className="aion-panel rounded-[2rem] p-5">
                <div className="mb-5 flex flex-wrap items-end justify-between gap-4">
                  <div>
                    <p className="text-sm uppercase tracking-[0.24em] text-base-800">{copy.tools.eyebrow}</p>
                    <h2 className="font-display text-3xl text-base-900">{copy.tools.title}</h2>
                  </div>
                  <div className="aion-chip rounded-[1rem] px-3 py-2">
                    <p className="text-[10px] uppercase tracking-[0.18em] text-base-800">{copy.tools.groupCount}</p>
                    <p className="mt-1 text-sm font-semibold text-base-900">
                      {toolsOverview ? `${toolsOverview.summary.total_items} items` : "workspace snapshot"}
                    </p>
                  </div>
                </div>

                {toolsLoading ? (
                  <StatePanel tone="neutral" title={copy.common.stateLoadingTitle} body={copy.tools.loading} loading />
                ) : null}

                {!toolsLoading && !toolsOverview ? (
                  <StatePanel tone="neutral" title={copy.common.stateEmptyTitle} body={copy.tools.empty} />
                ) : null}

                <div className="grid gap-5">
                  {toolsOverview?.groups.map((group) => (
                    <article key={group.id} className="aion-panel-soft rounded-[1.6rem] p-4">
                      <div className="mb-4 flex flex-wrap items-start justify-between gap-3">
                        <div>
                          <h3 className="font-display text-2xl text-base-900">{group.title}</h3>
                          <p className="mt-1 max-w-3xl text-sm leading-7 text-base-800">{group.description}</p>
                        </div>
                        <div className="rounded-[1rem] bg-base-100 px-3 py-2">
                          <p className="text-[10px] uppercase tracking-[0.18em] text-base-800">{copy.tools.groupCount}</p>
                          <p className="mt-1 text-sm font-semibold text-base-900">{group.item_count} items</p>
                        </div>
                      </div>

                      <div className="grid gap-4 lg:grid-cols-2">
                        {group.items.map((item) => (
                          <section key={item.id} className="rounded-[1.4rem] border border-base-300 bg-base-100 p-4">
                            <div className="mb-3 flex flex-wrap items-start justify-between gap-3">
                              <div>
                                <div className="flex flex-wrap items-center gap-2">
                                  <h4 className="font-display text-xl text-base-900">{item.label}</h4>
                                  {item.integral ? (
                                    <span className="rounded-full bg-primary/12 px-3 py-1 text-[11px] font-semibold uppercase tracking-[0.18em] text-primary">
                                      {copy.tools.integral}
                                    </span>
                                  ) : null}
                                </div>
                                <p className="mt-2 text-sm leading-7 text-base-800">{item.description}</p>
                              </div>
                              <div className={`badge ${toolStatusClass(item.status)}`}>{formatToolState(item.status)}</div>
                            </div>

                            <div className="mb-4 grid gap-3 lg:grid-cols-2">
                              <div className="rounded-2xl bg-base-200 p-3">
                                <p className="text-xs uppercase tracking-[0.18em] text-base-800">{copy.tools.availability}</p>
                                <p className="mt-2 text-base font-semibold text-base-900">
                                  {item.enabled ? copy.common.on : copy.common.off}
                                </p>
                              </div>
                              <div className="rounded-2xl bg-base-200 p-3">
                                <p className="text-xs uppercase tracking-[0.18em] text-base-800">{copy.tools.provider}</p>
                                <p className="mt-2 text-base font-semibold text-base-900">
                                  {item.provider.name.replaceAll("_", " ")}
                                </p>
                                <p className="mt-1 text-xs text-base-800">
                                  {item.provider.ready
                                    ? "ready"
                                    : item.provider.configured
                                      ? "configured"
                                      : "not configured"}
                                </p>
                              </div>
                              <div className="rounded-2xl bg-base-200 p-3">
                                <p className="text-xs uppercase tracking-[0.18em] text-base-800">{copy.tools.control}</p>
                                {item.user_control.toggle_allowed ? (
                                  <label className="mt-2 flex items-center gap-3">
                                    <input
                                      className="toggle toggle-primary"
                                      type="checkbox"
                                      checked={Boolean(item.user_control.requested_enabled)}
                                      disabled={savingToolId === item.id}
                                      onChange={(event) => {
                                        void handleToolToggle(item.id, event.target.checked);
                                      }}
                                    />
                                    <span className="text-base font-semibold text-base-900">
                                      {savingToolId === item.id
                                        ? copy.tools.saving
                                        : item.user_control.requested_enabled
                                          ? copy.tools.enabledByUser
                                          : copy.tools.disabledByUser}
                                    </span>
                                  </label>
                                ) : (
                                  <p className="mt-2 text-base font-semibold text-base-900">{copy.tools.readOnly}</p>
                                )}
                              </div>
                              <div className="rounded-2xl bg-base-200 p-3">
                                <p className="text-xs uppercase tracking-[0.18em] text-base-800">{copy.tools.linkState}</p>
                                <p className="mt-2 text-base font-semibold text-base-900">
                                  {titleCaseFromStatus(item.link_state)}
                                </p>
                              </div>
                            </div>

                            <div className="space-y-3">
                              <div className="rounded-2xl border border-base-300 px-4 py-3">
                                <p className="text-xs uppercase tracking-[0.18em] text-base-800">{copy.tools.currentStatus}</p>
                                <p className="mt-2 text-sm leading-7 text-base-900">{item.status_reason}</p>
                              </div>

                              <div className="rounded-2xl border border-base-300 px-4 py-3">
                                <p className="text-xs uppercase tracking-[0.18em] text-base-800">{copy.tools.nextStep}</p>
                                <p className="mt-2 text-sm leading-7 text-base-900">
                                  {summarizeToolAction(item.next_actions, copy.tools.noAction)}
                                </p>
                              </div>

                              {item.id === "telegram" &&
                              item.user_control.requested_enabled &&
                              item.provider.ready &&
                              item.link_state !== "linked" ? (
                                <div className="rounded-2xl border border-base-300 px-4 py-4">
                                  <div className="flex flex-wrap items-start justify-between gap-3">
                                    <div>
                                      <p className="text-xs uppercase tracking-[0.18em] text-base-800">
                                        {copy.tools.telegramLinking}
                                      </p>
                                      <p className="mt-2 max-w-2xl text-sm leading-7 text-base-900">
                      Generate a short code, then send it to the configured Aviary Telegram bot from
                                        the chat you want to attach to this identity.
                                      </p>
                                    </div>
                                    <button
                                      className="btn btn-primary btn-sm"
                                      disabled={telegramLinkBusy}
                                      type="button"
                                      onClick={() => {
                                        void handleStartTelegramLink();
                                      }}
                                    >
                                      {telegramLinkBusy
                                        ? copy.tools.generating
                                        : telegramLinkStart
                                          ? copy.tools.rotateCode
                                          : copy.tools.generateCode}
                                    </button>
                                  </div>

                                  {telegramLinkStart ? (
                                    <div className="mt-4 grid gap-3 sm:grid-cols-[minmax(0,0.7fr)_minmax(0,1.3fr)]">
                                      <div className="rounded-2xl bg-base-200 p-3">
                                        <p className="text-xs uppercase tracking-[0.18em] text-base-800">{copy.tools.linkCode}</p>
                                        <p className="mt-2 font-display text-3xl tracking-[0.18em] text-base-900">
                                          {telegramLinkStart.link_code}
                                        </p>
                                        <p className="mt-2 text-xs text-base-800">
                                          Expires in about {telegramLinkStart.expires_in_seconds} seconds.
                                        </p>
                                      </div>
                                      <div className="rounded-2xl bg-base-200 p-3">
                                        <p className="text-xs uppercase tracking-[0.18em] text-base-800">
                                          {copy.tools.instruction}
                                        </p>
                                        <p className="mt-2 text-sm leading-7 text-base-900">
                                          {telegramLinkStart.instruction_text}
                                        </p>
                                      </div>
                                    </div>
                                  ) : (
                                    <p className="mt-4 text-sm text-base-800">
                                      {copy.tools.noLinkCode}
                                    </p>
                                  )}
                                </div>
                              ) : null}

                              <details className="rounded-2xl border border-base-300 bg-base-100">
                                <summary className="cursor-pointer px-4 py-3 text-sm font-semibold text-base-900">
                                  {copy.tools.technicalDetails}
                                </summary>
                                <div className="grid gap-3 px-4 pb-4 sm:grid-cols-2">
                                  <div className="rounded-2xl bg-base-200 p-3">
                                    <p className="text-xs uppercase tracking-[0.18em] text-base-800">{copy.tools.capabilities}</p>
                                    <div className="mt-3 flex flex-wrap gap-2">
                                      {item.capabilities.length > 0 ? (
                                        item.capabilities.map((capability) => (
                                          <span
                                            key={capability}
                                            className="rounded-full border border-base-300 bg-base-100 px-3 py-1 text-xs font-medium text-base-900"
                                          >
                                            {capability}
                                          </span>
                                        ))
                                      ) : (
                                        <span className="text-sm text-base-800">{copy.common.noData}</span>
                                      )}
                                    </div>
                                  </div>
                                  <div className="rounded-2xl bg-base-200 p-3">
                                    <p className="text-xs uppercase tracking-[0.18em] text-base-800">{copy.common.sourceOfTruth}</p>
                                    <div className="mt-3 flex flex-wrap gap-2">
                                      {item.source_of_truth.length > 0 ? (
                                        item.source_of_truth.map((source) => (
                                          <span
                                            key={source}
                                            className="rounded-full bg-base-100 px-3 py-1 text-xs font-medium text-base-800"
                                          >
                                            {source}
                                          </span>
                                        ))
                                      ) : (
                                        <span className="text-sm text-base-800">{copy.common.noData}</span>
                                      )}
                                    </div>
                                  </div>
                                </div>
                              </details>
                            </div>
                          </section>
                        ))}
                      </div>
                    </article>
                  ))}
                </div>
              </section>
            </div>
          ) : null}

          {route === "/personality" ? (
            <div className="grid gap-6">
              <section className="aion-panel-soft rounded-[1.8rem] p-5">
                <div className="flex flex-wrap items-end justify-between gap-4">
                  <div className="max-w-3xl">
                    <p className="text-sm uppercase tracking-[0.24em] text-base-800">{copy.personality.eyebrow}</p>
                    <h2 className="mt-2 font-display text-4xl text-base-900">{copy.personality.title}</h2>
                    <p className="mt-3 text-sm leading-7 text-base-800">{copy.personality.subtitle}</p>
                  </div>
                  <div className="flex flex-wrap gap-2">
                    {[
                      `${stringValue(planningSummary?.active_goal_count, "0")} goals`,
                      `${stringValue(knowledgeSummary?.semantic_conclusion_count, "0")} patterns`,
                      `${stringValue(preferenceSummary?.learned_preference_count, "0")} preferences`,
                    ].map((chip) => (
                      <span
                        key={chip}
                        className="aion-chip-ghost rounded-full px-3 py-2 text-[11px] font-semibold uppercase tracking-[0.18em]"
                      >
                        {chip}
                      </span>
                    ))}
                  </div>
                </div>
              </section>

              <section className="aion-panel-soft aion-personality-preview-nav rounded-[1.8rem] p-3">
                <div className="flex flex-wrap gap-2">
                  {personalityPreviewTabs.map((tab, index) => (
                    <span
                      key={tab}
                      className={`aion-personality-preview-tab ${index === 0 ? "aion-personality-preview-tab-active" : ""}`}
                    >
                      {tab}
                    </span>
                  ))}
                </div>
              </section>

              <div className="grid gap-6 xl:grid-cols-[minmax(0,1.3fr)_minmax(22rem,0.74fr)]">
                <div className="grid gap-6">
                  <section className="aion-panel aion-personality-hero">
                    <div className="aion-personality-hero-stage">
                      <div className="aion-personality-hero-figure">
                        {personalityPreviewCallouts.map((callout) => (
                          <article key={callout.key} className={callout.className}>
                            <p className="text-[10px] uppercase tracking-[0.18em] text-base-800">{callout.eyebrow}</p>
                            <p className="mt-2 font-display text-xl text-base-900">{callout.title}</p>
                            <p className="mt-2 text-sm leading-6 text-base-800">{callout.body}</p>
                          </article>
                        ))}
                      </div>
                    </div>

                    <div className="aion-personality-timeline-panel">
                      <div className="mb-4">
                        <p className="text-sm uppercase tracking-[0.24em] text-base-800">Mind layers timeline</p>
                        <h3 className="mt-2 font-display text-2xl text-base-900">Embodied personality layers in motion</h3>
                      </div>
                      <div className="grid gap-3">
                        {personalityTimelineRows.map((row) => (
                          <PersonalityTimelineRow
                            key={row.title}
                            token={row.token}
                            title={row.title}
                            detail={row.detail}
                            value={row.value}
                          />
                        ))}
                      </div>
                    </div>
                  </section>

                </div>

                <div className="grid gap-6">
                  <InsightPanel
                    eyebrow="Conscious layer"
                    title="Active awareness and current cognition"
                    body="The foreground loop stays visible through focus, clarity, active load, and the present task horizon."
                    className="aion-personality-side-panel aion-personality-side-panel-conscious"
                  >
                    <div className="grid gap-3">
                      {personalityConsciousSignals.map((item) => (
                        <div key={item.label} className="aion-personality-signal-row">
                          <span className="aion-personality-signal-label">{item.label}</span>
                          <span className="aion-personality-signal-value">{item.value}</span>
                        </div>
                      ))}
                    </div>
                  </InsightPanel>

                  <InsightPanel
                    eyebrow="Subconscious layer"
                    title="Background patterns and latent knowledge"
                    body="Longer memory, associations, and learned preferences stay active without crowding the live route."
                    className="aion-personality-side-panel aion-personality-side-panel-subconscious"
                  >
                    <div className="grid gap-3">
                      {personalitySubconsciousSignals.map((item) => (
                        <div key={item.label} className="aion-personality-signal-row">
                          <span className="aion-personality-signal-label">{item.label}</span>
                          <span className="aion-personality-signal-value">{item.value}</span>
                        </div>
                      ))}
                    </div>
                  </InsightPanel>

                  <InsightPanel
                    eyebrow="Recent activity"
                    title="Latest internal movement"
                    body="Recent changes stay readable before the user opens the deeper sections."
                    className="aion-personality-side-panel aion-personality-side-panel-recent"
                  >
                    <div className="grid gap-3">
                      {personalityRecentActivity.map((item) => (
                        <div key={item.title} className="aion-personality-activity-row">
                          <div>
                            <p className="text-sm font-semibold text-base-900">{item.title}</p>
                            <p className="mt-1 text-sm text-base-800">{item.when}</p>
                          </div>
                          <span className="aion-chip-ghost rounded-full px-3 py-1 text-xs font-medium">View</span>
                        </div>
                      ))}
                    </div>
                  </InsightPanel>

                  <InsightPanel
                    eyebrow="Highlights"
                    title="Current product signals"
                    body="These summary cards keep the route readable before the user opens any deeper detail."
                    className="aion-personality-side-panel aion-personality-side-panel-highlight"
                  >
                    <div className="aion-personality-highlight-grid">
                      {[
                        {
                          title: copy.personality.goals,
                          value: stringValue(planningSummary?.active_goal_count, "0"),
                          note: "Goals the personality is currently following",
                          accent: "gold" as const,
                        },
                        {
                          title: copy.personality.tasks,
                          value: stringValue(planningSummary?.active_task_count, "0"),
                          note: "Tasks currently being tracked",
                          accent: "default" as const,
                        },
                        {
                          title: copy.personality.knowledge,
                          value: stringValue(knowledgeSummary?.semantic_conclusion_count, "0"),
                          note: "Learned patterns kept available",
                          accent: "teal" as const,
                        },
                        {
                          title: copy.personality.preferences,
                          value: stringValue(preferenceSummary?.learned_preference_count, "0"),
                          note: "Preferences the personality has picked up",
                          accent: "default" as const,
                        },
                      ].map((card, index) => (
                        <MetricCard
                          key={card.title}
                          eyebrow={card.title}
                          value={card.value}
                          detail={card.note}
                          accent={card.accent}
                          className={
                            index === 0
                              ? "aion-personality-highlight-card aion-personality-highlight-card-primary"
                              : "aion-personality-highlight-card"
                          }
                        />
                      ))}
                    </div>
                  </InsightPanel>
                </div>
              </div>

            </div>
          ) : null}
            </main>

            {route === "/chat" ? (
              <section className="aion-panel aion-chat-feature-strip">
                {chatFeatures.map((feature) => (
                  <ChatFeatureCard key={feature.title} token={feature.token} title={feature.title} body={feature.body} />
                ))}
              </section>
            ) : null}
          </div>
        </div>

        {route !== "/chat" ? (
          <nav className="fixed inset-x-0 bottom-0 z-30 border-t border-base-300 bg-base-100/95 px-3 py-3 backdrop-blur md:hidden">
            <div className="mx-auto grid max-w-2xl grid-cols-5 gap-2">
              {ROUTES.map((entry) => (
                <button
                  key={entry}
                  className={`rounded-[1.2rem] px-3 py-3 text-sm font-medium transition ${
                    route === entry
                      ? "bg-base-900 text-base-100 shadow-sm"
                      : "border border-base-300 bg-base-200 text-base-900"
                  }`}
                  onClick={() => changeRoute(entry)}
                  type="button"
                >
                  {routeLabel(entry, resolvedUiLanguage)}
                </button>
              ))}
            </div>
          </nav>
        ) : null}
      </div>
    </div>
  );
}
