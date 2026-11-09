import assert from "node:assert/strict";
import { describe, it } from "node:test";
import worker, {
  weftSubhostRedirect,
  w3ftPathRedirect,
} from "./siliconcordat.mjs";

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

function mockAssets() {
  return {
    fetch: async () => new Response("assets", { status: 200 }),
  };
}

describe("fetch handler", () => {
  it("301 www.siliconcordat.com to .com preserving path and query", async () => {
    const res = await worker.fetch(
      new Request("https://www.siliconcordat.com/ml?x=1"),
      { ASSETS: mockAssets() }
    );
    assert.equal(res.status, 301);
    assert.equal(res.headers.get("Location"), "https://siliconcordat.com/ml?x=1");
  });

  it("does not redirect siliconcordat.org to .com", async () => {
    let assetsCalled = false;
    const res = await worker.fetch(
      new Request("https://siliconcordat.org/ml"),
      {
        ASSETS: {
          fetch: async () => {
            assetsCalled = true;
            return new Response("ok");
          },
        },
      }
    );
    assert.equal(assetsCalled, true);
    assert.equal(res.status, 200);
    assert.equal(await res.text(), "ok");
  });

  it("does not redirect www.siliconcordat.org to .com", async () => {
    let assetsCalled = false;
    const res = await worker.fetch(
      new Request("https://www.siliconcordat.org/ml"),
      {
        ASSETS: {
          fetch: async () => {
            assetsCalled = true;
            return new Response("ok");
          },
        },
      }
    );
    assert.equal(assetsCalled, true);
    assert.equal(res.status, 200);
  });

  it("301 weft.siliconcordat.com via weftSubhostRedirect", async () => {
    const res = await worker.fetch(
      new Request("https://weft.siliconcordat.com/papers/"),
      { ASSETS: mockAssets() }
    );
    assert.equal(res.status, 301);
    assert.equal(
      res.headers.get("Location"),
      "https://siliconcordat.com/weft/papers/"
    );
  });

  it("301 /w3ft paths on same origin", async () => {
    const res = await worker.fetch(
      new Request("https://siliconcordat.com/w3ft/papers/?q=1"),
      { ASSETS: mockAssets() }
    );
    assert.equal(res.status, 301);
    assert.equal(
      res.headers.get("Location"),
      "https://siliconcordat.com/weft/papers/?q=1"
    );
  });
});
