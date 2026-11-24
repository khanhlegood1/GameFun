#!/usr/bin/env node
/* check_portal_render.mjs — trang phải THỰC SỰ vẽ được, không chỉ tải được.
 *
 * Một cổng chỉ kiểm HTTP 200 trên `index.html` sẽ xanh trong khi `app.js` ném lỗi
 * và người xem thấy trang trắng. Không có trình duyệt trong CI, nên ở đây dựng một
 * DOM tối thiểu trong Node, nạp `app.js` NGUYÊN VĂN (không sửa), rồi khẳng định
 * những con số đã vẽ ra khớp với `data.json`.
 *
 * Sáu bất biến:
 *   1. `derive()` chạy không ném, và các con số khớp dữ liệu.
 *   2. Mỗi việc trong sổ đều vẽ ra được một dòng (hoặc bị lọc có lý do).
 *   3. Việc bị chặn phải mang nhãn "Đang chờ", KHÔNG phải "Đang mở".
 *   4. ADR `chờ ký` phải hiện chữ "Chờ ký" — không được hiện "Đã nhận".
 *
 * Chạy: node scripts/check_portal_render.mjs
 */
import fs from "node:fs";
import path from "node:path";
import vm from "node:vm";
import { fileURLToPath } from "node:url";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const data = JSON.parse(fs.readFileSync(path.join(ROOT, "portal/data.json"), "utf8"));
const src = fs.readFileSync(path.join(ROOT, "portal/app.js"), "utf8");

const fails = [];
const ok = (cond, msg) => { if (!cond) fails.push(msg); };

/* ---------- DOM tối thiểu ---------- */
class Node_ {
  constructor(tag) {
    this.tagName = (tag || "div").toUpperCase();
    this.children = [];
    this.attrs = {};
    this._text = "";
    this.className = "";
    this.hidden = false;
    this.dataset = {};
    this.classList = {
      _s: new Set(),
      add: (c) => this.classList._s.add(c),
      remove: (c) => this.classList._s.delete(c),
      toggle: (c, on) => (on ? this.classList._s.add(c) : this.classList._s.delete(c)),
      contains: (c) => this.classList._s.has(c),
    };
  }
  get textContent() { return this._text + this.children.map((c) => c.textContent).join(""); }
  set textContent(v) { this._text = String(v ?? ""); this.children = []; }
  append(...ns) { for (const n of ns) this.children.push(typeof n === "string" ? new Node_("#text") : n); this._text += ""; }
  appendChild(n) { this.children.push(n); return n; }
  replaceChildren(...ns) { this.children = []; this._text = ""; this.append(...ns); }
  setAttribute(k, v) { this.attrs[k] = v; }
  removeAttribute(k) { delete this.attrs[k]; }
  addEventListener() {}
  focus() {}
  querySelector() { return null; }
  querySelectorAll() { return []; }
  /* đệ quy tìm theo class, đủ cho phép kiểm */
  all(pred, out = []) {
    if (pred(this)) out.push(this);
    for (const c of this.children) if (c.all) c.all(pred, out);
    return out;
  }
}
class TextNode extends Node_ {
  constructor(t) { super("#text"); this._text = String(t); }
}

const registry = new Map();
const byId = (id) => {
  if (!registry.has(id)) registry.set(id, new Node_("div"));
  return registry.get(id);
};
const documentStub = {
  createElement: (t) => new Node_(t),
  createTextNode: (t) => new TextNode(t),
  querySelector: (sel) => (sel.startsWith("#") ? byId(sel.slice(1)) : null),
  querySelectorAll: () => [],
  addEventListener: () => {},
  body: new Node_("body"),
};

/* ---------- chạy app.js ---------- */
const ctx = {
  document: documentStub,
  window: { addEventListener: () => {} },
  fetch: async () => ({ ok: true, json: async () => data }),
  console,
  Date,
  Math,
  Set,
  Map,
  Object,
  Array,
  JSON,
  String,
  Number,
  encodeURIComponent,
  setTimeout,
};
ctx.globalThis = ctx;
ctx.window.document = documentStub;

let thrown = null;
try {
  vm.createContext(ctx);
  vm.runInContext(src, ctx, { filename: "portal/app.js" });
} catch (e) {
  thrown = e;
}
ok(!thrown, `app.js ném lỗi khi nạp: ${thrown && thrown.message}`);

/* ---------- chờ boot() xong rồi kiểm ---------- */
const tick = () => new Promise((r) => setTimeout(r, 50));

const run = async () => {
  await tick();
  if (thrown) return report();

  const appHidden = byId("app").hidden;
  ok(appHidden === false, "app vẫn bị ẩn sau khi nạp data.json — người xem thấy trang trắng");

  /* 1. KPI khớp dữ liệu */
  const kpis = byId("kpis").all((n) => n.className && n.className.includes("kpi-v")).map((n) => n.textContent);
  const open = data.actions.filter((a) => a.status === "OPEN");
  ok(kpis[0] === String(open.length), `KPI 'Việc đang mở' = ${kpis[0]}, sổ có ${open.length} việc OPEN`);

  /* 2. Mỗi việc mở vẽ ra một dòng */
  const rows = byId("task-body").all((n) => n.tagName === "TR" && n.className.includes("task"));
  ok(rows.length === open.length, `vẽ ${rows.length} dòng, sổ có ${open.length} việc đang mở`);
  const drawnIds = rows.map((r) => {
    const idNode = r.all((n) => n.className === "id")[0];
    return idNode ? idNode.textContent : null;
  });
  for (const a of open) ok(drawnIds.includes(a.id), `việc ${a.id} không được vẽ ra`);

  /* 3. Việc bị chặn phải mang nhãn "Đang chờ" */
  for (const a of open) {
    const row = rows.find((r) => r.all((n) => n.className === "id")[0]?.textContent === a.id);
    if (!row) continue;
    const label = row.all((n) => n.className && n.className.includes("chip"))[0]?.textContent || "";
    if ((a.blocked_by || []).length) {
      ok(label.includes("Đang chờ"), `${a.id} bị chặn bởi ${a.blocked_by.join(",")} nhưng nhãn là "${label}"`);
    }
    if (a.due && a.due < new Date().toISOString().slice(0, 10)) {
      ok(label.includes("Quá hạn"), `${a.id} quá hạn (${a.due}) nhưng nhãn là "${label}"`);
    }
  }

  /* 4. ADR chờ ký không được hiện như đã nhận */
  const adrCards = byId("adr-list").all((n) => n.className === "adr-card");
  ok(adrCards.length === data.adr.items.length, `vẽ ${adrCards.length} ADR, dữ liệu có ${data.adr.items.length}`);
  const needSig = data.adr.items.filter((i) => i.needs_signature);
  for (const item of needSig) {
    const card = adrCards.find((c) => c.all((n) => n.className === "id")[0]?.textContent === item.id.replace("ADR-", ""));
    if (!card) { fails.push(`ADR ${item.id} không được vẽ ra`); continue; }
    const chip = card.all((n) => n.className && n.className.includes("chip"))[0]?.textContent || "";
    ok(!chip.includes("Đã nhận") || item.state === "accepted",
      `${item.id} còn 'chờ ký' nhưng hiện ra là "${chip.trim()}"`);
  }

  /* 5. Không nhãn người nào được đọc thành "LKLXK".
   * `aria-hidden` chỉ ảnh hưởng trình đọc màn hình — bộ trích văn bản, ảnh chụp
   * màn hình cho nhà đầu tư, và bản in PDF đều đọc hết. Nên phần CHỮ phải là tên
   * người thật, không phải hai lần mã ghép lại.
   */
  for (const code of Object.keys(data.people || {})) {
    const shown = byId("task-body").all((n) => n.className === "owner-name");
    const texts = shown.map((n) => n.textContent);
    const dup = texts.filter((x) => x === code + code || (x.length === 4 && x.slice(2) === code));
    ok(dup.length === 0, `mã người "${code}" bị lặp thành "${dup[0]}" — phải hiện TÊN, không hiện mã hai lần`);
  }
  const nameShown = byId("task-body").all((n) => n.className === "owner-name").map((n) => n.textContent);
  const expected = Object.values(data.people || {}).map((p) => p.name);
  for (const nm of expected) {
    ok(nameShown.includes(nm), `tên "${nm}" không xuất hiện ở cột Người — cột này đang hiện mã, không hiện tên`);
  }

  /* 6. Hàng đợi quyết định phải có, và đúng là những việc đang chặn việc khác */
  const queue = byId("queue").all((n) => n.className === "queue-card");
  const blockers = new Set(open.flatMap((a) => a.blocked_by || []));
  for (const b of blockers) {
    ok(queue.some((c) => c.all((n) => n.className === "id")[0]?.textContent === b),
      `${b} đang chặn việc khác nhưng không có trong hàng đợi quyết định`);
  }
  report();
};

function report() {
  if (fails.length) {
    console.log(`PORTAL RENDER: FAIL — ${fails.length} vi phạm`);
    for (const f of fails) console.log("  -", f);
    process.exit(1);
  }
  const open = data.actions.filter((a) => a.status === "OPEN").length;
  console.log(`PORTAL RENDER: PASS — app.js chạy trong DOM tối thiểu · ${open} việc vẽ ra · ` +
    `${data.adr.items.length} ADR · nhãn khớp dữ liệu`);
  process.exit(0);
}

run();
