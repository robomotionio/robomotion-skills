type GithubStarsCacheEntry = {
  value: string;
  expiresAt: number;
  inFlight?: Promise<void>;
};

type GithubStarsCacheStore = Map<string, GithubStarsCacheEntry>;

const DEFAULT_TTL_MS = 15 * 60 * 1000;

const globalStore = globalThis as typeof globalThis & {
  __uiSkillsGithubStarsCache?: GithubStarsCacheStore;
};

const cacheStore: GithubStarsCacheStore =
  globalStore.__uiSkillsGithubStarsCache ??
  (globalStore.__uiSkillsGithubStarsCache = new Map());

const parseMaxAge = (cacheControl: string | null) => {
  if (!cacheControl) return null;

  const match = cacheControl.match(/(?:s-maxage|max-age)=(\d+)/i);
  if (!match) return null;

  const seconds = Number(match[1]);
  if (!Number.isFinite(seconds) || seconds <= 0) return null;

  return seconds * 1000;
};

const formatCompact = (value: number) =>
  new Intl.NumberFormat("en-US", {
    notation: "compact",
    maximumFractionDigits: 1,
  })
    .format(value)
    .toLowerCase()
    .replace(/\s+/g, "");

const normalizeStarsLabel = (value: string) => {
  const trimmed = value.trim().toLowerCase();

  if (/^\d+(?:\.\d+)?[km]$/.test(trimmed)) {
    return trimmed;
  }

  const numeric = Number(trimmed.replace(/,/g, ""));
  if (Number.isFinite(numeric)) {
    return formatCompact(numeric);
  }

  return value.trim();
};

const fetchStarsFromShields = async (
  repo: string,
): Promise<{ stars: string; ttl: number }> => {
  const response = await fetch(
    `https://img.shields.io/github/stars/${repo}.json`,
    {
      headers: {
        Accept: "application/json",
      },
    },
  );

  if (!response.ok) {
    throw new Error(`Shields API returned ${response.status}`);
  }

  const ttl = parseMaxAge(response.headers.get("cache-control")) ?? DEFAULT_TTL_MS;

  const data = (await response.json()) as { value?: string };
  const stars = data.value ? normalizeStarsLabel(data.value) : "";

  if (!stars) {
    throw new Error("Missing or invalid value in Shields response");
  }

  return { stars, ttl };
};

export const getGithubStars = async (
  repo: string,
  fallback: string,
): Promise<string> => {
  const now = Date.now();
  const entry = cacheStore.get(repo);

  const refresh = async () => {
    const { stars, ttl } = await fetchStarsFromShields(repo);

    cacheStore.set(repo, {
      value: stars,
      expiresAt: Date.now() + ttl,
    });
  };

  const queueRefresh = () => {
    const current = cacheStore.get(repo);
    if (current?.inFlight) {
      return current.inFlight;
    }

    const inFlight = refresh()
      .catch(() => {
        if (!cacheStore.has(repo)) {
          cacheStore.set(repo, {
            value: fallback,
            expiresAt: Date.now() + DEFAULT_TTL_MS,
          });
        }
      })
      .finally(() => {
        const latest = cacheStore.get(repo);
        if (latest) {
          delete latest.inFlight;
          cacheStore.set(repo, latest);
        }
      });

    cacheStore.set(repo, {
      value: current?.value ?? fallback,
      expiresAt: current?.expiresAt ?? 0,
      inFlight,
    });

    return inFlight;
  };

  if (entry && now < entry.expiresAt) {
    return entry.value;
  }

  if (entry) {
    void queueRefresh();
    return entry.value;
  }

  await queueRefresh();
  return cacheStore.get(repo)?.value ?? fallback;
};
