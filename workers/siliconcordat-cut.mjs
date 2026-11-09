/**
 * ml-siliconcordat-cut: redirects for siliconcordat.org when domains attach later,
 * then static assets from generated dist-cut/ (wrangler.siliconcordat-cut.jsonc).
 */

const ORG_ORIGIN = "https://siliconcordat.org";

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

    if (host === "www.siliconcordat.org") {
      return Response.redirect(
        `${ORG_ORIGIN}${url.pathname}${url.search}`,
        301
      );
    }

    if (url.pathname === "/w3ft" || url.pathname.startsWith("/w3ft/")) {
      return Response.redirect(w3ftPathRedirect(url), 301);
    }

    return env.ASSETS.fetch(request);
  },
};

export { w3ftPathRedirect };
