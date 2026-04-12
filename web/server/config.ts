import path from "node:path";
import fs from "node:fs";
import os from "node:os";

export interface ServerConfig {
  wikiRoot: string;
  port: number;
  host: string;
  author: string;
}

export function parseArgs(argv: string[]): ServerConfig {
  const args = argv.slice(2);
  let wikiRoot: string | null = null;
  let port = 4175;
  let host = "127.0.0.1";
  let author = os.userInfo().username || "me";

  for (let i = 0; i < args.length; i++) {
    const a = args[i]!;
    switch (a) {
      case "--wiki":
      case "-w":
        wikiRoot = args[++i] ?? null;
        break;
      case "--port":
      case "-p":
        port = parseInt(args[++i] ?? "4175", 10);
        break;
      case "--host":
        host = args[++i] ?? host;
        break;
      case "--author":
        author = args[++i] ?? author;
        break;
      case "--help":
      case "-h":
        printHelp();
        process.exit(0);
      default:
        if (a.startsWith("--")) {
          console.error(`unknown flag: ${a}`);
          printHelp();
          process.exit(1);
        }
    }
  }

  if (!wikiRoot) {
    console.error("error: 必须提供 --wiki <root>");
    printHelp();
    process.exit(1);
  }

  const resolved = path.resolve(wikiRoot);
  if (!fs.existsSync(resolved) || !fs.statSync(resolved).isDirectory()) {
    console.error(`error: workbench root 不存在或不是目录: ${resolved}`);
    process.exit(1);
  }

  return { wikiRoot: resolved, port, host, author };
}

function printHelp(): void {
  console.log(`
Usage:
  npm start -- --wiki <workbench-root> [--port 4175] [--host 127.0.0.1] [--author lewis]

Options:
  -w, --wiki     workbench 根目录（必填）。目录内应包含 WORKBENCH.md，
                 以及 compiled/、indexes/、audit/、log/ 等 canonical 目录。
  -p, --port     监听端口（默认: 4175）。
      --host     绑定地址（默认: 127.0.0.1，仅本机）。
      --author   写入 audit 文件的作者名（默认: $USER）。
  -h, --help     显示帮助。
`);
}
