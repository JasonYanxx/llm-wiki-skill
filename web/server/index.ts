import express from "express";
import path from "node:path";
import url from "node:url";
import fs from "node:fs";
import { parseArgs } from "./config.js";
import { createBasicAuthMiddleware } from "./auth.js";
import { handleTree } from "./routes/tree.js";
import { handleFile, handlePage, handleRaw } from "./routes/pages.js";
import { handleAuditList, handleAuditCreate, handleAuditResolve } from "./routes/audit.js";
import { handleGraph } from "./routes/graph.js";
import { handleHealth } from "./routes/health.js";

const cfg = parseArgs(process.argv);

const app = express();
app.use(express.json({ limit: "2mb" }));
app.use(createBasicAuthMiddleware(cfg));

function isLoopbackHost(host: string): boolean {
  return host === "127.0.0.1" || host === "localhost" || host === "::1";
}

// ── API ────────────────────────────────────────────────────────────────────
app.get("/api/tree", handleTree(cfg));
app.get("/api/graph", handleGraph(cfg));
app.get("/api/page", handlePage(cfg));
app.get("/api/raw", handleRaw(cfg));
app.get("/api/file", handleFile(cfg));
app.get("/api/audit", handleAuditList(cfg));
app.post("/api/audit", handleAuditCreate(cfg));
app.patch("/api/audit/:id/resolve", handleAuditResolve(cfg));
app.get("/api/health", handleHealth(cfg));
app.get("/api/config", (_req, res) => {
  res.json({ author: cfg.author, wikiRoot: path.basename(cfg.wikiRoot) });
});

// ── Static client ──────────────────────────────────────────────────────────
const here = path.dirname(url.fileURLToPath(import.meta.url));
const clientDist = path.resolve(here, "../dist/client");
if (!fs.existsSync(clientDist)) {
  console.warn(
    `warning: client bundle not found at ${clientDist}. 请先运行 'npm run build'。`,
  );
}
app.use("/assets", express.static(path.join(clientDist, "assets")));
app.use("/katex", express.static(path.resolve(here, "../node_modules/katex/dist")));
app.get("/", (_req, res) => {
  const index = path.join(clientDist, "index.html");
  if (fs.existsSync(index)) {
    res.sendFile(index);
  } else {
    res.status(500).send("client bundle missing. 请先运行: npm run build");
  }
});

// ── Start ───────────────────────────────────────────────────────────────────
app.listen(cfg.port, cfg.host, () => {
  console.log(`research workbench web server 已启动: http://${cfg.host}:${cfg.port}`);
  console.log(`  workbench root: ${cfg.wikiRoot}`);
  console.log(`  author: ${cfg.author}`);
  if (cfg.authPassword) {
    console.log(`  basic auth: enabled (user: ${cfg.authUser})`);
  } else if (!isLoopbackHost(cfg.host)) {
    console.warn("  warning: LAN access is enabled without authentication.");
    console.warn("           add --auth-pass <password> to require a browser login.");
  }
});
