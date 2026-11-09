import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { weftSubhostRedirect, w3ftPathRedirect } from "./siliconcordat.mjs";

describe("weftSubhostRedirect", () => {
  it("maps / to /weft", () => {
    const u = new URL("https://weft.siliconcordat.com/");
    assert.equal(weftSubhostRedirect(u), "https://siliconcordat.com/weft");
  });

  it("prefixes extra path without doubling", () => {
    const u = new URL("https://weft.siliconcordat.com/papers/overview/");
    assert.equal(
      weftSubhostRedirect(u),
      "https://siliconcordat.com/weft/papers/overview/"
    );
  });
});

describe("w3ftPathRedirect", () => {
  it("replaces /w3ft with /weft on same origin", () => {
    const u = new URL("https://siliconcordat.com/w3ft/papers/?q=1");
    assert.equal(
      w3ftPathRedirect(u),
      "https://siliconcordat.com/weft/papers/?q=1"
    );
  });

  it("maps bare /w3ft to /weft", () => {
    const u = new URL("https://siliconcordat.com/w3ft");
    assert.equal(w3ftPathRedirect(u), "https://siliconcordat.com/weft");
  });
});
