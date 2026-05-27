import type { APIRoute } from "astro";
import { skills, type Skill } from "../data/skills";

const SITE_URL = "https://www.ui-skills.com";

const escapeXml = (value: string) =>
  value
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/\"/g, "&quot;")
    .replace(/'/g, "&apos;");

const buildTopicRoutes = (allSkills: Skill[]) =>
  Array.from(new Set(allSkills.flatMap((skill) => skill.topics ?? []))).map(
    (topic) => `/skills/${topic}`,
  );

const buildGroupPaths = (allSkills: Skill[]) =>
  Array.from(
    new Set(
      allSkills.flatMap((skill) => {
        const segments = skill.pathSlug.split("/");
        if (segments.length <= 1) {
          return [];
        }

        return segments
          .slice(0, -1)
          .map((_, index) => segments.slice(0, index + 1).join("/"));
      }),
    ),
  );

export const GET: APIRoute = ({ site }) => {
  const origin = site?.origin ?? SITE_URL;

  const staticRoutes = ["/", "/skills", "/skills/topics"];
  const topicRoutes = buildTopicRoutes(skills);
  const groupRoutes = buildGroupPaths(skills).map((path) => `/skills/${path}`);
  const skillRoutes = skills.map((skill) => `/skills/${skill.pathSlug}`);
  const allRoutes = Array.from(
    new Set([...staticRoutes, ...topicRoutes, ...groupRoutes, ...skillRoutes]),
  );

  const urlset = allRoutes
    .map((route) => {
      const normalizedRoute =
        route === "/" ? "/" : route.endsWith("/") ? route : `${route}/`;
      const loc = new URL(normalizedRoute, origin).toString();
      return `<url><loc>${escapeXml(loc)}</loc></url>`;
    })
    .join("");

  const body = `<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">${urlset}</urlset>`;

  return new Response(body, {
    headers: {
      "Content-Type": "application/xml; charset=utf-8",
    },
  });
};
