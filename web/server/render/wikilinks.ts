import type MarkdownIt from "markdown-it";

/**
 * markdown-it plugin: turn [[Target]] and [[Target|Alias]] into anchor tags.
 *
 * The resolver decides the final href and whether the target exists.
 * Unresolved links get a `wikilink-dead` class so the client can style them.
 */
export interface WikilinkResolver {
  (target: string): { href: string; exists: boolean } | null;
}

export function wikilinksPlugin(md: MarkdownIt, resolve: WikilinkResolver): void {
  const WIKILINK_RE = /(!)?\[\[([^\]|#]+)(?:#([^\]|]+))?(?:\|([^\]]+))?\]\]/;

  md.inline.ruler.before("link", "wikilink", (state, silent) => {
    const src = state.src;
    const isEmbedStart = src[state.pos] === "!" && src[state.pos + 1] === "[" && src[state.pos + 2] === "[";
    const isLinkStart = src[state.pos] === "[" && src[state.pos + 1] === "[";
    if (!isEmbedStart && !isLinkStart) return false;
    const tail = src.slice(state.pos);
    const m = WIKILINK_RE.exec(tail);
    if (!m || m.index !== 0) return false;

    const isEmbed = Boolean(m[1]);
    const target = m[2]!.trim();
    if (isEmbed && !isImageTarget(target)) return false;

    if (!silent) {
      const anchor = m[3]?.trim();
      const alias = m[4]?.trim();
      const display = alias || target;

      const resolved = resolve(target);
      if (isEmbed) {
        const image = state.push("image", "img", 0);
        image.children = [];
        image.content = alias && !isNumericAlias(alias) ? alias : target;
        image.attrs = [
          ["src", resolved?.href ?? `/api/file?path=${encodeURIComponent(target)}`],
          ["alt", alias && !isNumericAlias(alias) ? alias : target],
          ["class", `wikilink-embed ${resolved?.exists ? "wikilink-embed-alive" : "wikilink-embed-dead"}`],
          ["data-wikilink-target", target],
        ];
        const width = parseWidth(alias);
        if (width) image.attrs.push(["width", width]);
      } else {
        const href =
          resolved?.href ??
          `/?page=${encodeURIComponent(target)}${anchor ? "#" + encodeURIComponent(anchor) : ""}`;

        const open = state.push("link_open", "a", 1);
        open.attrs = [
          ["href", href + (anchor ? `#${anchor}` : "")],
          ["class", `wikilink ${resolved?.exists ? "wikilink-alive" : "wikilink-dead"}`],
          ["data-wikilink-target", target],
        ];
        const text = state.push("text", "", 0);
        text.content = display;
        state.push("link_close", "a", -1);
      }
    }
    state.pos += m[0].length;
    return true;
  });
}

function isImageTarget(target: string): boolean {
  const clean = target.split("#")[0]!.split("?")[0]!;
  return /\.(png|jpe?g|gif|webp|bmp|heic|tiff)$/i.test(clean);
}

function isNumericAlias(alias: string): boolean {
  return /^\d+(?:x\d+)?$/.test(alias);
}

function parseWidth(alias?: string): string | null {
  if (!alias || !isNumericAlias(alias)) return null;
  const width = alias.split("x")[0] ?? "";
  return /^\d+$/.test(width) ? width : null;
}
