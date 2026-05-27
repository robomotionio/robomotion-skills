import type { APIRoute } from "astro";

import type { RegistrySkill } from "../../data/registry";
import { registry } from "../../data/registry";

export const GET: APIRoute = () => {
  const body = registry
    .map(
      (entry: RegistrySkill) =>
        `${entry.pathSlug}\t${entry.rawUrl}\t${entry.description ?? ""}`,
    )
    .join("\n");

  return new Response(`${body}\n`, {
    headers: {
      "Content-Type": "text/plain; charset=utf-8",
      "X-Robots-Tag": "noindex, nofollow",
    },
  });
};
