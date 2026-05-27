import type { APIRoute } from "astro";
import { skills } from "../../../data/skills";
import { registry } from "../../../data/registry";

const skillRawModules = import.meta.glob<string>("/skills/*/SKILL.md", {
  eager: true,
  query: "?raw",
  import: "default",
});

const skillRawEntries = Object.entries(skillRawModules).map(([path, raw]) => {
  const entrySlug = path.split("/").at(-2) ?? "";

  return { slug: entrySlug, raw };
});

export function getStaticPaths() {
  return skills.map((skill) => ({
    params: { slug: skill.pathSlug },
  }));
}

export const GET: APIRoute = async ({ params }) => {
  const routeSlug = params.slug ?? "";
  const pathSlug = Array.isArray(routeSlug) ? routeSlug.join("/") : routeSlug;
  const skillEntry = skills.find((skill) => skill.pathSlug === pathSlug);

  if (!skillEntry) {
    return new Response("Skill not found", { status: 404 });
  }

  if (!skillEntry.isRegistry) {
    const localSkill = skillRawEntries.find(
      (entry) => entry.slug === skillEntry.slug,
    );
    if (!localSkill) {
      return new Response("Skill not found", { status: 404 });
    }

    return new Response(localSkill.raw, {
      headers: {
        "Content-Type": "text/plain; charset=utf-8",
        "X-Robots-Tag": "noindex, nofollow",
      },
    });
  }

  const registrySkill = registry.find((entry) => entry.pathSlug === pathSlug);
  if (!registrySkill) {
    return new Response("Skill not found", { status: 404 });
  }

  try {
    const response = await fetch(registrySkill.rawUrl);
    if (!response.ok) {
      const status = response.status === 404 ? 404 : 502;
      return new Response("Skill source unavailable", { status });
    }

    const content = await response.text();
    return new Response(content, {
      headers: {
        "Content-Type": "text/plain; charset=utf-8",
        "X-Robots-Tag": "noindex, nofollow",
      },
    });
  } catch {
    return new Response("Error fetching registry skill", { status: 500 });
  }
};
