// Re-derives the query string that the logsguardian middleware hands to the
// extractor, for Round 5 requests sent exactly as run_large_corpus.py sends them.
// old = pre-25c7e64 derivation (URLSearchParams over Express req.query)
// new = dc380e3 derivation (slice of req.originalUrl after "?")
const fs = require("fs");
const path = require("path");
const readline = require("readline");

const QS_PATH = "/Users/diego/Uvg/Proyecto de Graduacion/logSguarDian-vulnerable-project/node_modules/qs";
const qs = require(QS_PATH);
const extractor = require(path.join(__dirname, "../dev/packages/extractor/build/index.js"));

const INPUT = process.argv[2];
const OUTPUT = process.argv[3];

function pythonQuotePlus(value) {
  return encodeURIComponent(value)
    .replace(/[!'()*]/g, (c) => "%" + c.charCodeAt(0).toString(16).toUpperCase())
    .replace(/%20/g, "+");
}

function wireQuery(item) {
  return `${pythonQuotePlus(item.param)}=${pythonQuotePlus(item.payload)}`;
}

function oldQueryDerivation(expressQuery) {
  return new URLSearchParams(expressQuery).toString();
}

function newQueryDerivation(rawUrl) {
  const queryIndex = rawUrl.indexOf("?");
  return queryIndex >= 0 ? rawUrl.slice(queryIndex + 1) : "";
}

function vectorFor(item, query) {
  return extractor.extractFeatureVector({
    method: item.method,
    path: item.path,
    query,
    body: item.body,
    userAgent: item.userAgent,
    contentType: item.contentType,
    referer: item.referer,
    cookie: item.cookie,
    extraHeaders: item.extraHeaders,
  });
}

function describeRow(item) {
  const wire = item.method === "GET" ? wireQuery(item) : "";
  const rawUrl = item.method === "GET" ? `${item.path}?${wire}` : item.path;
  const expressQuery = item.method === "GET" ? qs.parse(wire) : {};
  return {
    wire,
    prior_reference: item.method === "GET" ? item.stored_query : "",
    old: oldQueryDerivation(expressQuery),
    new: newQueryDerivation(rawUrl),
  };
}

async function main() {
  const out = fs.createWriteStream(OUTPUT);
  const rl = readline.createInterface({ input: fs.createReadStream(INPUT), crlfDelay: Infinity });
  for await (const line of rl) {
    if (!line.trim()) continue;
    const item = JSON.parse(line);
    if (item.source !== "round5") continue;
    const q = describeRow(item);
    out.write(JSON.stringify({
      id: item.id,
      label: item.label,
      method: item.method,
      wire_query: q.wire,
      prior_reference_query: q.prior_reference,
      old_query: q.old,
      new_query: q.new,
      vectors: {
        prior_reference: vectorFor(item, q.prior_reference),
        old: vectorFor(item, q.old),
        new: vectorFor(item, q.new),
      },
    }) + "\n");
  }
  out.end();
}

main();
