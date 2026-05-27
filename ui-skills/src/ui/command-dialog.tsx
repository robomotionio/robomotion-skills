import { Dialog as DialogPrimitive } from "@base-ui/react/dialog";
import {
  useEffect,
  useMemo,
  useState,
  type ChangeEvent,
  type KeyboardEvent as ReactKeyboardEvent,
  type ReactNode,
} from "react";

type CommandItem = {
  slug: string;
  pathSlug: string;
  label: string;
  sourceLabel?: string;
  description?: string;
  searchContent?: string;
};

type CommandDialogProps = {
  items: CommandItem[];
};

type SearchResult = CommandItem & {
  score: number;
  snippet: string;
};

type IndexedCommandItem = CommandItem & {
  slugLower: string;
  labelLower: string;
  pathSlugLower: string;
  sourceLower: string;
  descriptionLower: string;
  contentLower: string;
};

const toSearchResult = (
  item: CommandItem,
  score: number,
  snippet: string,
): SearchResult => ({
  slug: item.slug,
  pathSlug: item.pathSlug,
  label: item.label,
  sourceLabel: item.sourceLabel,
  description: item.description,
  searchContent: item.searchContent,
  score,
  snippet,
});

const MAX_DEFAULT_ITEMS = 14;
const MAX_FILTERED_ITEMS = 24;

const escapeRegExp = (value: string) =>
  value.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
const idForPath = (pathSlug: string) =>
  `skills-search-item-${pathSlug.replace(/[^a-zA-Z0-9_-]/g, "-")}`;
const keycapClass =
  "bg-parchment-200/70 text-parchment-700 rounded-[4px] px-1.5 py-0.5 text-[10px] font-medium leading-none font-mono";

const plainText = (value?: string) =>
  (value ?? "")
    .replace(/^---[\s\S]*?---/, " ")
    .replace(/`{1,3}[^`]*`{1,3}/g, " ")
    .replace(/[\[\]#>*_~|-]/g, " ")
    .replace(/\s+/g, " ")
    .trim();

const createSnippet = (content: string, query: string) => {
  if (!content || !query) {
    return "";
  }

  const normalizedContent = plainText(content);
  const lowerContent = normalizedContent.toLowerCase();
  const lowerQuery = query.toLowerCase();
  const index = lowerContent.indexOf(lowerQuery);

  if (index === -1) {
    return "";
  }

  const padding = 70;
  const start = Math.max(0, index - padding);
  const end = Math.min(
    normalizedContent.length,
    index + query.length + padding,
  );
  const prefix = start > 0 ? "..." : "";
  const suffix = end < normalizedContent.length ? "..." : "";

  return `${prefix}${normalizedContent.slice(start, end).trim()}${suffix}`;
};

const highlightText = (value: string, query: string): ReactNode => {
  const normalizedQuery = query.trim();

  if (!normalizedQuery) {
    return value;
  }

  const matcher = new RegExp(`(${escapeRegExp(normalizedQuery)})`, "ig");
  const parts = value.split(matcher);

  return parts.map((part, index) =>
    part.toLowerCase() === normalizedQuery.toLowerCase() ? (
      <mark
        key={`${part}-${index}`}
        className="text-parchment-900 rounded-[3px] bg-[#efe6bf] px-[2px]"
      >
        {part}
      </mark>
    ) : (
      <span key={`${part}-${index}`}>{part}</span>
    ),
  );
};

export function CommandDialog({ items }: CommandDialogProps) {
  const [open, setOpen] = useState(false);
  const [query, setQuery] = useState("");
  const [activeIndex, setActiveIndex] = useState(0);

  const indexedItems = useMemo<IndexedCommandItem[]>(
    () =>
      items.map((item) => {
        const contentLower = plainText(item.searchContent).toLowerCase();

        return {
          ...item,
          slugLower: item.slug.toLowerCase(),
          labelLower: item.label.toLowerCase(),
          pathSlugLower: item.pathSlug.toLowerCase(),
          sourceLower: (item.sourceLabel ?? "").toLowerCase(),
          descriptionLower: (item.description ?? "").toLowerCase(),
          contentLower,
        };
      }),
    [items],
  );

  useEffect(() => {
    const onKeyDown = (event: KeyboardEvent) => {
      const isMac = navigator.platform.toLowerCase().includes("mac");
      const isOpenHotkey = isMac
        ? event.metaKey && event.key.toLowerCase() === "k"
        : event.ctrlKey && event.key.toLowerCase() === "k";

      if (!isOpenHotkey) {
        return;
      }

      event.preventDefault();
      setOpen((prev) => {
        const next = !prev;

        if (next) {
          setActiveIndex(0);
        }

        return next;
      });
    };

    window.addEventListener("keydown", onKeyDown);
    return () => window.removeEventListener("keydown", onKeyDown);
  }, []);

  const filteredItems = useMemo<SearchResult[]>(() => {
    const value = query.trim().toLowerCase();

    if (!value) {
      return indexedItems.slice(0, MAX_DEFAULT_ITEMS).map((item) =>
        toSearchResult(item, 0, item.description ?? ""),
      );
    }

    return indexedItems
      .map<SearchResult | null>((item) => {
        let score = 0;

        if (item.slugLower.startsWith(value)) score += 140;
        if (item.slugLower.includes(value)) score += 90;
        if (item.labelLower.includes(value)) score += 80;
        if (item.pathSlugLower.includes(value)) score += 70;
        if (item.sourceLower.includes(value)) score += 40;
        if (item.descriptionLower.includes(value)) score += 30;
        if (item.contentLower.includes(value)) score += 16;

        if (!score) {
          return null;
        }

        const snippet =
          createSnippet(item.searchContent ?? "", value) ||
          createSnippet(item.description ?? "", value) ||
          item.description ||
          "";

        return toSearchResult(item, score, snippet);
      })
      .filter((result): result is SearchResult => Boolean(result))
      .sort((a, b) => {
        if (b.score !== a.score) {
          return b.score - a.score;
        }

        return a.pathSlug.localeCompare(b.pathSlug);
      })
      .slice(0, MAX_FILTERED_ITEMS);
  }, [indexedItems, query]);

  const scrollToItem = (index: number) => {
    const active = filteredItems[index];

    if (!active) {
      return;
    }

    const activeElement = document.getElementById(idForPath(active.pathSlug));
    activeElement?.scrollIntoView({ block: "nearest" });
  };

  const setIndexAndScroll = (index: number) => {
    setActiveIndex(index);
    requestAnimationFrame(() => scrollToItem(index));
  };

  const handleOpenChange = (nextOpen: boolean) => {
    setOpen(nextOpen);

    if (nextOpen) {
      setActiveIndex(0);
    }
  };

  const onInputChange = (event: ChangeEvent<HTMLInputElement>) => {
    setQuery(event.target.value);
    setActiveIndex(0);
  };

  const onSelect = (pathSlug: string) => {
    setOpen(false);
    setQuery("");
    window.location.href = `/skills/${pathSlug}`;
  };

  const onInputKeyDown = (event: ReactKeyboardEvent<HTMLInputElement>) => {
    if (!open) {
      return;
    }

    if (event.key === "ArrowDown") {
      event.preventDefault();
      const nextIndex =
        filteredItems.length === 0
          ? 0
          : (activeIndex + 1) % filteredItems.length;

      setIndexAndScroll(nextIndex);
      return;
    }

    if (event.key === "ArrowUp") {
      event.preventDefault();
      const nextIndex =
        filteredItems.length === 0
          ? 0
          : (activeIndex - 1 + filteredItems.length) % filteredItems.length;

      setIndexAndScroll(nextIndex);
      return;
    }

    if (event.key === "Enter") {
      const selected = filteredItems[activeIndex];
      if (!selected) {
        return;
      }

      event.preventDefault();
      onSelect(selected.pathSlug);
      return;
    }

    if (event.key === "Escape") {
      event.preventDefault();
      setOpen(false);
    }
  };

  return (
    <DialogPrimitive.Root open={open} onOpenChange={handleOpenChange}>
      <DialogPrimitive.Trigger
        aria-label="Open skills search"
        className="hover:bg-parchment-100 text-parchment-700 hover:text-parchment-900 focus-visible:outline-primary inline-flex items-center gap-2 rounded-[6px] border border-transparent bg-transparent px-2.5 py-2 text-[14px] font-[450] tracking-tight transition-colors focus-visible:outline-1 focus-visible:outline-offset-2"
      >
        <svg
          aria-hidden="true"
          xmlns="http://www.w3.org/2000/svg"
          width="16"
          height="16"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
        >
          <circle cx="11" cy="11" r="8" />
          <path d="m21 21-4.3-4.3" />
        </svg>
        Search
        <kbd className={keycapClass}>⌘K</kbd>
      </DialogPrimitive.Trigger>

      <DialogPrimitive.Portal>
        <DialogPrimitive.Backdrop className="fixed inset-0 z-50 bg-black/35 backdrop-blur-sm" />
        <DialogPrimitive.Popup className="fixed top-24 left-1/2 z-50 w-[min(92vw,680px)] -translate-x-1/2 rounded-[12px] border border-neutral-200 bg-white shadow-xl outline-none">
          <DialogPrimitive.Title className="sr-only">
            Search skills
          </DialogPrimitive.Title>
          <div className="border-parchment-200 flex items-center gap-2 border-b px-4 py-3">
            <svg
              aria-hidden="true"
              xmlns="http://www.w3.org/2000/svg"
              width="16"
              height="16"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
              className="text-parchment-500"
            >
              <circle cx="11" cy="11" r="8" />
              <path d="m21 21-4.3-4.3" />
            </svg>
            <input
              autoFocus
              value={query}
              onChange={onInputChange}
              onKeyDown={onInputKeyDown}
              placeholder="Search skills..."
              className="text-parchment-900 placeholder:text-parchment-400 w-full bg-transparent text-base outline-none sm:text-[15px]"
              role="combobox"
              aria-expanded={open}
              aria-controls="skills-search-results"
              aria-activedescendant={
                filteredItems[activeIndex]
                  ? idForPath(filteredItems[activeIndex].pathSlug)
                  : undefined
              }
            />
          </div>

          <div
            className="max-h-[55vh] overflow-y-auto p-2"
            role="listbox"
            id="skills-search-results"
          >
            {filteredItems.length === 0 ? (
              <div className="text-parchment-500 px-2 py-8 text-center text-sm">
                No skills found.
              </div>
            ) : (
              filteredItems.map((item, index) => (
                <button
                  key={item.pathSlug}
                  id={idForPath(item.pathSlug)}
                  role="option"
                  aria-selected={index === activeIndex}
                  type="button"
                  onClick={() => onSelect(item.pathSlug)}
                  onMouseEnter={() => setActiveIndex(index)}
                  className={`w-full rounded-[8px] px-3 py-2 text-left transition-colors ${
                    index === activeIndex
                      ? "bg-parchment-100"
                      : "hover:bg-parchment-100"
                  }`}
                >
                  <div className="text-parchment-900 text-sm font-medium tracking-tight">
                    {highlightText(item.slug, query)}
                  </div>
                  <div className="text-parchment-500 mt-0.5 text-xs">
                    {highlightText(item.sourceLabel ?? "Ibelick", query)}
                  </div>
                  {item.snippet ? (
                    <div className="text-parchment-500 mt-1 line-clamp-2 text-[12px] leading-snug">
                      {highlightText(item.snippet, query)}
                    </div>
                  ) : null}
                </button>
              ))
            )}
          </div>

          <div className="text-parchment-500 border-parchment-200 flex items-center justify-between border-t px-4 py-2 text-[11px]">
            <span>{filteredItems.length} results</span>
            <div className="flex items-center gap-3">
              <span className="flex items-center gap-1.5">
                <span className="flex items-center gap-1">
                  <kbd className={keycapClass}>↑</kbd>
                  <kbd className={keycapClass}>↓</kbd>
                </span>
                move
              </span>
              <span>
                <kbd className={keycapClass}>Enter</kbd> open
              </span>
              <span>
                <kbd className={keycapClass}>Esc</kbd> close
              </span>
            </div>
          </div>
        </DialogPrimitive.Popup>
      </DialogPrimitive.Portal>
    </DialogPrimitive.Root>
  );
}
