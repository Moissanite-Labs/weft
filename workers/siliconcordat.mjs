/**
 * ml-siliconcordat: host/path redirects when custom domains are attached later,
 * then static assets from the generated dist/ tree (wrangler.siliconcordat.jsonc).
 */

const CANONICAL_ORIGIN = "https://siliconcordat.com";

const WWW_OR_ALT_HOSTS = new Set([
  "www.siliconcordat.com",
  "siliconcordat.org",
  "www.siliconcordat.org",
]);

/** @param {URL} url */
function weftSubhostRedirect(url) {
  let path = url.pathname || "/";
  if (path === "/") {
    path = "/weft";
  } else if (path.startsWith("/weft/") || path === "/weft") {
    /* already prefixed — should not happen on weft.siliconcordat.com */
  } else {
    path = `/weft${path.startsWith("/") ? path : `/${path}`}`;
  }
  return `${CANONICAL_ORIGIN}${path}${url.search}`;
}

/** @param {URL} url */
function w3ftPathRedirect(url) {
  const rest = url.pathname.slice("/w3ft".length);
  const path =
    !rest || rest === "/"
      ? "/weft"
      : `/weft${rest.startsWith("/") ? rest : `/${rest}`}`;
  return `${url.origin}${path}${url.search}`;
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const host = url.hostname.toLowerCase();

    if (WWW_OR_ALT_HOSTS.has(host)) {
      return Response.redirect(`${CANONICAL_ORIGIN}${url.pathname}${url.search}`, 301);
    }

    if (host === "weft.siliconcordat.com") {
      return Response.redirect(weftSubhostRedirect(url), 301);
    }

    if (url.pathname === "/w3ft" || url.pathname.startsWith("/w3ft/")) {
      return Response.redirect(w3ftPathRedirect(url), 301);
    }

    return env.ASSETS.fetch(request);
  },
};

export { weftSubhostRedirect, w3ftPathRedirect, WWW_OR_ALT_HOSTS };
