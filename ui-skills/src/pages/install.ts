import type { APIRoute } from "astro";
import installScript from "../../install.sh?raw";
import { skills } from "../data/skills";

export const GET: APIRoute = () => {
  const allSkills = skills.map((s) => s.pathSlug).join(" ");
  const body =
    installScript
      .replace(/ALL_SKILLS=".*"/, `ALL_SKILLS="${allSkills}"`)
      .trim() + "\n";

  return new Response(body, {
    headers: {
      "Content-Type": "text/x-shellscript; charset=utf-8",
      "X-Robots-Tag": "noindex, nofollow",
    },
  });
};
