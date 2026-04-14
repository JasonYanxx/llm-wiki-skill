import { timingSafeEqual } from "node:crypto";
import type { RequestHandler, Response } from "express";
import type { ServerConfig } from "./config.js";

function challenge(res: Response): void {
  res.setHeader("WWW-Authenticate", 'Basic realm="Research Workbench"');
  res.status(401).send("Authentication required.");
}

function safeEqual(left: string, right: string): boolean {
  const leftBuf = Buffer.from(left, "utf8");
  const rightBuf = Buffer.from(right, "utf8");
  if (leftBuf.length !== rightBuf.length) {
    return false;
  }
  return timingSafeEqual(leftBuf, rightBuf);
}

export function createBasicAuthMiddleware(cfg: ServerConfig): RequestHandler {
  const authPassword = cfg.authPassword;
  if (!authPassword) {
    return (_req, _res, next) => next();
  }

  return (req, res, next) => {
    const header = req.headers.authorization;
    if (!header || !header.startsWith("Basic ")) {
      challenge(res);
      return;
    }

    const encoded = header.slice("Basic ".length).trim();
    let decoded = "";
    try {
      decoded = Buffer.from(encoded, "base64").toString("utf8");
    } catch {
      challenge(res);
      return;
    }

    const separator = decoded.indexOf(":");
    if (separator === -1) {
      challenge(res);
      return;
    }

    const username = decoded.slice(0, separator);
    const password = decoded.slice(separator + 1);
    if (!safeEqual(username, cfg.authUser) || !safeEqual(password, authPassword)) {
      challenge(res);
      return;
    }

    next();
  };
}
