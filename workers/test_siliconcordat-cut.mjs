import assert from "node:assert/strict";
import { describe, it } from "node:test";
import worker, { w3ftPathRedirect } from "./siliconcordat-cut.mjs";

describe("w3ftPathRedirect", () => {
  it("replaces /w3ft with /weft on same origin", () => {
    const u = new URL("https://siliconcordat.org/w3ft/papers/?q=1");
    assert.equal(
      w3ftPathRedirect(u),
      "https://siliconcordat.org/weft/papers/?q=1"
    );
  });

  it("maps bare /w3ft to /weft", () => {
    const u = new URL("https://siliconcordat.org/w3ft");
    assert.equal(w3ftPathRedirect(u), "https://siliconcordat.org/weft");
  });
});

function mockAssets() {
  return {
    fetch: async () => new Response("assets", { status: 200 }),
  };
}

describe("fetch handler", () => {
  it("301 www.siliconcordat.org to apex preserving path and query", async () => {
    const res = await worker.fetch(
      new Request("https://www.siliconcordat.org/ml?x=1"),
      { ASSETS: mockAssets() }
    );
    assert.equal(res.status, 301);
    assert.equal(
      res.headers.get("Location"),
      "https://siliconcordat.org/ml?x=1"
    );
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
  });

  it("does not redirect www.siliconcordat.org to .com", async () => {
    const res = await worker.fetch(
      new Request("https://www.siliconcordat.org/ml"),
      { ASSETS: mockAssets() }
    );
    assert.equal(res.status, 301);
    assert.equal(
      res.headers.get("Location"),
      "https://siliconcordat.org/ml"
    );
  });

  it("does not redirect siliconcordat.com", async () => {
    let assetsCalled = false;
    const res = await worker.fetch(
      new Request("https://siliconcordat.com/ml"),
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

  it("does not redirect weft.siliconcordat.com", async () => {
    let assetsCalled = false;
    const res = await worker.fetch(
      new Request("https://weft.siliconcordat.com/papers/"),
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

  it("301 /w3ft paths on same origin", async () => {
    const res = await worker.fetch(
      new Request("https://siliconcordat.org/w3ft/papers/?q=1"),
      { ASSETS: mockAssets() }
    );
    assert.equal(res.status, 301);
    assert.equal(
      res.headers.get("Location"),
      "https://siliconcordat.org/weft/papers/?q=1"
    );
  });

  it("adds X-Robots-Tag on staging host profile only", async () => {
    const res = await worker.fetch(
      new Request("https://example.workers.dev/"),
      {
        ASSETS: mockAssets(),
        CUT_HOST: "staging",
      }
    );
    assert.equal(res.status, 200);
    assert.equal(res.headers.get("X-Robots-Tag"), "noindex");
  });

  it("adds X-Robots-Tag on staging host profile for 404 response", async () => {
    const res = await worker.fetch(
      new Request("https://example.workers.dev/nonexistent"),
      {
        ASSETS: {
          fetch: async () => new Response("not found", { status: 404 }),
        },
        CUT_HOST: "staging",
      }
    );
    assert.equal(res.status, 404);
    assert.equal(res.headers.get("X-Robots-Tag"), "noindex");
  });

  it("does not add X-Robots-Tag when CUT_HOST is unset", async () => {
    const res = await worker.fetch(
      new Request("https://example.workers.dev/"),
      { ASSETS: mockAssets() }
    );
    assert.equal(res.headers.get("X-Robots-Tag"), null);
  });
});
