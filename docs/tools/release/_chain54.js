// 版本链凭据：逐字节统计 + SHA256
const fs = require("fs");
const path = require("path");
const crypto = require("crypto");

const repo = "C:\\Users\\D_A\\WorkBuddy\\2026-10-05-13-53-42\\repo\\haiyu-zongdui-tankuangjingniang";
const OUT = "C:\\Users\\D_A\\WorkBuddy\\2026-10-05-13-53-42\\_chain54.txt";

const targets = [];
for (const n of fs.readdirSync(path.join(repo, "docs", "versions")).sort()) {
  targets.push(["docs/versions/" + n, path.join(repo, "docs", "versions", n)]);
}
targets.push(["root(现行)", path.join(repo, "海底小纵队·探矿鲸娘.user.js")]);

const L = [];
function w(s) { L.push(s); }

for (const [label, p] of targets) {
  const b = fs.readFileSync(p);
  const crlf = (b.toString("latin1").match(/\r\n/g) || []).length;
  // 裸 LF = 所有 \n 减去 \r\n
  const allLF = (b.toString("latin1").match(/\n/g) || []).length;
  const bareLF = allLF - crlf;
  const sha = crypto.createHash("sha256").update(b).digest("hex");
  w(label + " | bytes=" + b.length + " | CRLF=" + crlf + " | bareLF=" + bareLF + " | sha256=" + sha);
}

fs.writeFileSync(OUT, L.join("\n"), "utf8");
console.log("ok " + L.length);
