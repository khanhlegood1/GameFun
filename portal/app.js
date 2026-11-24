/* Game9K · Project Control Room
 * Không framework, không bước build: đọc ./data.json rồi vẽ.
 * Mọi con số trên màn hình đều đến từ data.json (sinh bởi scripts/gen_portal_data.py),
 * không có số nào gõ tay trong tệp này — đó là điều kiện để nhà đầu tư nhìn thấy
 * đúng thứ đang nằm trong repo.
 */
"use strict";

const STATE = {
  data: null,
  tab: "open",
  q: "",
  adrFilter: "all",
};

const $ = (sel, root = document) => root.querySelector(sel);
const el = (tag, cls, text) => {
  const n = document.createElement(tag);
  if (cls) n.className = cls;
  if (text != null) n.textContent = text;
  return n;
};
const esc = (s) => String(s ?? "");

/* ---------- ngày tháng ---------- */
const VN_DOW = ["CN", "T2", "T3", "T4", "T5", "T6", "T7"];
function todayISO() {
  // Dùng giờ máy người xem để tô "hôm nay"; `as_of` của dữ liệu hiển thị riêng.
  const d = new Date();
  const p = (n) => String(n).padStart(2, "0");
  return `${d.getFullYear()}-${p(d.getMonth() + 1)}-${p(d.getDate())}`;
}
function parseISO(iso) {
  if (!iso) return null;
  const m = /^(\d{4})-(\d{2})-(\d{2})$/.exec(iso);
  if (!m) return null;
  return new Date(Date.UTC(+m[1], +m[2] - 1, +m[3]));
}
function daysBetween(aISO, bISO) {
  const a = parseISO(aISO), b = parseISO(bISO);
  if (!a || !b) return null;
  return Math.round((b - a) / 86400000);
}
function fmtVN(iso) {
  const d = parseISO(iso);
  if (!d) return "—";
  return `${VN_DOW[d.getUTCDay()]}, ${d.getUTCDate()}/${d.getUTCMonth() + 1}/${d.getUTCFullYear()}`;
}
function fmtShort(iso) {
  const d = parseISO(iso);
  if (!d) return "—";
  return `${String(d.getUTCDate()).padStart(2, "0")}/${String(d.getUTCMonth() + 1).padStart(2, "0")}`;
}
function greeting() {
  const h = new Date().getHours();
  if (h < 11) return "Chào buổi sáng";
  if (h < 14) return "Chào buổi trưa";
  if (h < 18) return "Chào buổi chiều";
  return "Chào buổi tối";
}

/* ---------- trạng thái ---------- */
// Trạng thái HIỂN THỊ suy ra từ dữ liệu, không lưu trong dữ liệu:
// một việc bị chặn mà vẫn OPEN thì nhãn phải là "đang chờ", không phải "đang làm".
function actionState(a, deps, today) {
  if (a.status === "DONE") return "done";
  if (a.status === "DROPPED") return "dropped";
  if (a.due && a.due < today) return "overdue";
  if ((a.blocked_by || []).length) return "blocked";
  return "open";
}
const STATE_LABEL = {
  open: "Đang mở",
  blocked: "Đang chờ",
  overdue: "Quá hạn",
  done: "Xong",
  dropped: "Đã bỏ",
};
const ADR_LABEL = {
  proposed: "Chờ ký",
  accepted: "Đã nhận",
  rejected: "Từ chối",
  superseded: "Đã thay thế",
  missing: "Thiếu tệp",
  unknown: "Không rõ",
};

/* ---------- dữ liệu dẫn xuất ---------- */
function derive(d) {
  const today = todayISO();
  const acts = d.actions.slice();
  const byId = Object.fromEntries(acts.map((a) => [a.id, a]));
  const blockedBy = {};
  const blocks = {};
  for (const a of acts) {
    blockedBy[a.id] = (a.blocked_by || []).slice();
    for (const b of blockedBy[a.id]) (blocks[b] ||= []).push(a.id);
  }
  const rows = acts.map((a) => ({
    ...a,
    state: actionState(a, blockedBy, today),
    daysLeft: a.due ? daysBetween(today, a.due) : null,
    asks: (a.blocked_by || []).map((id) => byId[id]).filter(Boolean),
  }));
  const open = rows.filter((r) => r.state !== "done" && r.state !== "dropped");
  const depth = (id) => { // số bậc chờ phía sau, để biết cái nào là gốc của dây chuyền
    let n = 0, cur = id, seen = new Set();
    while (blockedBy[cur]?.length && !seen.has(cur)) { seen.add(cur); cur = blockedBy[cur][0]; n++; }
    return n;
  };
  for (const r of rows) r.depth = depth(r.id);
  const roots = open.filter((r) => (blocks[r.id] || []).length);
  const adr = d.adr.items.map((i) => ({ ...i, isSigned: i.state === "accepted" && !i.needs_signature }));
  return {
    today, rows, open, byId, blocks, blockedBy, roots,
    adr,
    counts: {
      total: rows.length,
      open: open.length,
      done: rows.filter((r) => r.state === "done").length,
      blocked: rows.filter((r) => r.state === "blocked").length,
      overdue: rows.filter((r) => r.state === "overdue").length,
      untouchable: open.filter((r) => r.depth > 0).length,
      adrTotal: adr.length,
      adrProposed: adr.filter((i) => i.state === "proposed").length,
      adrMissing: adr.filter((i) => i.state === "missing").length,
    },
  };
}

/* ---------- vẽ ---------- */
function chip(state, kind) {
  const c = el("span", `chip chip-${state}`);
  c.append(el("i", "dot"));
  c.append(document.createTextNode(kind === "adr" ? ADR_LABEL[state] || state : STATE_LABEL[state] || state));
  return c;
}

// Tên hiển thị đọc từ data.people — không gõ lại trong tệp này.
let PEOPLE = {};
function displayName(code) {
  if (code === "AGENT") return "Tác nhân";
  const p = PEOPLE[code];
  return (p && p.name) || code;
}
function initials(code) {
  if (code === "AGENT") return "🤖";
  const n = displayName(code).trim().split(/\s+/);
  return (n[n.length - 2]?.[0] || n[0]?.[0] || "?").toUpperCase() + (n[n.length - 1]?.[0] || "").toUpperCase();
}
function ownerBadge(code) {
  // Avatar là trang trí: `aria-hidden` để trình đọc màn hình không đọc "LKLXK".
  // Nhưng `aria-hidden` KHÔNG ngăn bộ trích văn bản — nên phần chữ phải là tên
  // thật ("Lê Xuân Khánh"), không phải mã lặp lại mã ("LK" + "LXK").
  const b = el("span", "owner");
  const av = el("span", "avatar", initials(code));
  av.setAttribute("aria-hidden", "true");
  av.title = displayName(code);
  b.append(av);
  b.append(el("span", "owner-name", displayName(code)));
  return b;
}

function renderHeader(D, d) {
  $("#greet").textContent = `${greeting()}, Khánh`;
  $("#today").textContent = fmtVN(D.today);
  $("#asof").textContent = `Dữ liệu chốt ngày ${fmtVN(d.as_of)}`;
}

function renderKpis(D) {
  const box = $("#kpis");
  box.replaceChildren();
  const kpis = [
    { k: "Việc đang mở", v: D.counts.open, s: `trên tổng ${D.counts.total}`, tone: "brand" },
    { k: "Không thể tự bắt đầu", v: D.counts.untouchable, s: "đang chờ một việc khác", tone: "warn" },
    { k: "Quá hạn", v: D.counts.overdue, s: "phải quyết hoặc dời", tone: D.counts.overdue ? "bad" : "ok" },
    { k: "ADR chờ ký", v: D.counts.adrProposed, s: `trên ${D.counts.adrTotal} ADR`, tone: "warn" },
  ];
  for (const x of kpis) {
    const c = el("div", `kpi kpi-${x.tone}`);
    c.append(el("div", "kpi-v", String(x.v)));
    c.append(el("div", "kpi-k", x.k));
    c.append(el("div", "kpi-s", x.s));
    box.append(c);
  }
}

function chainOf(row, D) {
  // "P10 ← P9 ← P8": đường chờ dài nhất, để thấy nó bắt đầu từ đâu.
  const parts = [row];
  let cur = row, guard = 0;
  while ((cur.blocked_by || []).length && guard++ < 12) {
    const next = D.byId[cur.blocked_by[0]];
    if (!next) break;
    parts.push(next);
    cur = next;
  }
  return parts;
}

function renderChain(row, D) {
  const parts = chainOf(row, D);
  if (parts.length < 2) return el("span", "muted", "—");
  const box = el("div", "chain");
  parts.forEach((p, i) => {
    if (i) box.append(el("span", "chain-arrow", "←"));
    const t = el("span", `chain-node ${p.status === "DONE" ? "is-done" : ""}`);
    t.append(el("b", null, p.id));
    box.append(t);
  });
  return box;
}

function taskRow(row, D) {
  const tr = el("tr", `task task-${row.state}`);
  tr.tabIndex = 0;
  tr.setAttribute("role", "button");
  tr.setAttribute("aria-label", `Chi tiết ${row.id}: ${row.title}`);

  const c1 = el("td", "cell-id");
  c1.append(el("span", "id", row.id));
  if (row.depth > 0) c1.append(el("span", "depth", `+${row.depth}`));

  const c2 = el("td", "cell-title");
  const t = el("div", "t-title", row.title);
  c2.append(t);
  const meta = el("div", "t-meta");
  meta.append(el("span", null, row.source_doc || row.source || ""));
  if (row.blocked_by?.length) meta.append(el("span", "t-ask", `· chờ ${row.blocked_by.join(", ")}`));
  c2.append(meta);

  const c3 = el("td", "cell-owner");
  c3.append(ownerBadge(row.owner));

  const c4 = el("td", "cell-state");
  c4.append(chip(row.state));

  const c5 = el("td", "cell-due");
  const due = el("div", "due", fmtShort(row.due));
  if (row.daysLeft != null && row.state !== "done") {
    const late = row.daysLeft < 0;
    due.append(el("span", late ? "due-late" : "due-left",
      late ? `trễ ${Math.abs(row.daysLeft)}n` : `còn ${row.daysLeft}n`));
  } else if (row.status === "DONE" && row.done_on) {
    due.append(el("span", "due-left", `xong ${fmtShort(row.done_on)}`));
  }
  c5.append(due);

  const c6 = el("td", "cell-chain");
  c6.append(renderChain(row, D));

  tr.append(c1, c2, c3, c4, c5, c6);
  tr.addEventListener("click", () => openTask(row, D));
  tr.addEventListener("keydown", (e) => {
    if (e.key === "Enter" || e.key === " ") { e.preventDefault(); openTask(row, D); }
  });
  return tr;
}

function renderBoard(D) {
  const body = $("#task-body");
  body.replaceChildren();
  const q = STATE.q.trim().toLowerCase();
  let rows = D.rows.slice();

  if (STATE.tab === "open") rows = rows.filter((r) => r.state !== "done" && r.state !== "dropped");
  else if (STATE.tab === "blocked") rows = rows.filter((r) => r.state === "blocked" || r.depth > 0);
  else if (STATE.tab === "done") rows = rows.filter((r) => r.state === "done");

  if (q) {
    rows = rows.filter((r) =>
      [r.id, r.title, r.why, r.owner, r.due, r.source_doc].join(" ").toLowerCase().includes(q));
  }
  // Việc chờ người lên trước, rồi theo hạn; việc không có hạn xuống cuối.
  rows.sort((a, b) => {
    const rank = { overdue: 0, blocked: 1, open: 2, done: 3, dropped: 4 };
    if (rank[a.state] !== rank[b.state]) return rank[a.state] - rank[b.state];
    if (a.due && b.due && a.due !== b.due) return a.due < b.due ? -1 : 1;
    if (a.due && !b.due) return -1;
    if (!a.due && b.due) return 1;
    return a.id.localeCompare(b.id);
  });

  if (!rows.length) {
    const tr = el("tr");
    const td = el("td", "empty");
    td.colSpan = 6;
    td.textContent = q ? `Không có việc nào khớp “${STATE.q}”.` : "Không có việc nào trong mục này.";
    tr.append(td);
    body.append(tr);
  } else {
    for (const r of rows) body.append(taskRow(r, D));
  }
  $("#task-count").textContent = `${rows.length} việc`;
}

function renderDecisionQueue(D) {
  // Việc mà chỉ MỘT người quyết được, và nhiều việc khác đang chờ nó.
  const box = $("#queue");
  box.replaceChildren();
  const gates = D.rows
    .filter((r) => r.state !== "done" && (D.blocks[r.id] || []).length)
    .sort((a, b) => (D.blocks[b.id] || []).length - (D.blocks[a.id] || []).length);
  if (!gates.length) { box.append(el("p", "muted", "Không có việc nào đang chặn việc khác.")); return; }
  for (const g of gates) {
    const card = el("button", "queue-card");
    card.type = "button";
    const top = el("div", "queue-top");
    top.append(el("span", "id", g.id));
    top.append(chip(g.state));
    card.append(top);
    card.append(el("div", "queue-title", g.title));
    card.append(el("div", "queue-note", `Mở khoá ${(D.blocks[g.id] || []).length} việc: ${(D.blocks[g.id] || []).join(" · ")}`));
    const who = el("div", "queue-who");
    who.append(ownerBadge(g.owner));
    who.append(el("span", "muted", g.due ? `hạn ${fmtShort(g.due)}` : "chưa có hạn"));
    card.append(who);
    card.addEventListener("click", () => openTask(g, D));
    box.append(card);
  }
}

function renderAdr(D) {
  const box = $("#adr-list");
  box.replaceChildren();
  let items = D.adr.slice();
  if (STATE.adrFilter !== "all") items = items.filter((i) => i.state === STATE.adrFilter);
  if (!items.length) { box.append(el("p", "muted", "Không có ADR nào trong mục này.")); return; }
  for (const i of items) {
    const card = el(i.file ? "a" : "div", "adr-card");
    if (i.file) {
      card.href = `./docs/08-adr/${encodeURIComponent(i.file)}`;
      card.target = "_blank";
      card.rel = "noopener";
    }
    const head = el("div", "adr-head");
    head.append(el("span", "id", i.id.replace("ADR-", "")));
    head.append(chip(i.state, "adr"));
    card.append(head);
    const title = el("div", "adr-title", i.title.replace(/\*\*/g, "").replace(/`/g, ""));
    card.append(title);
    const foot = el("div", "adr-foot");
    foot.append(el("span", "adr-imp", i.impact || "—"));
    if (i.date) foot.append(el("span", "muted", fmtShort(i.date)));
    if (!i.file) foot.append(el("span", "adr-warn", "chỉ có trong chỉ mục — chưa có tệp trong repo"));
    card.append(foot);
    box.append(card);
  }
}

/* ---------- drawer ---------- */
function openTask(row, D) {
  const back = $("#drawer-back");
  const panel = $("#drawer");
  $("#drawer-id").textContent = row.id;
  $("#drawer-title").textContent = row.title;
  const body = $("#drawer-body");
  body.replaceChildren();

  const chips = el("div", "drawer-chips");
  chips.append(chip(row.state));
  chips.append(ownerBadge(row.owner));
  if (row.due) chips.append(el("span", "pk", `hạn ${fmtVN(row.due)}`));
  if (row.done_on) chips.append(el("span", "pk", `xong ${fmtVN(row.done_on)}`));
  body.append(chips);

  const section = (h, text) => {
    if (!text) return;
    const w = el("section", "sec");
    w.append(el("h4", null, h));
    w.append(el("p", null, text));
    body.append(w);
  };
  section("Vì sao việc này tồn tại", row.why);
  section("Cần gì để đóng", row.evidence_required);
  section("Nếu quá hạn", row.block_if_unmet_note || (row.block_if_unmet ? `Hành động: ${row.block_if_unmet}` : ""));
  section("Vì sao người này chứ không phải tác nhân", row.owner_reason);

  if (row.blocked_by?.length) {
    const w = el("section", "sec sec-chain");
    w.append(el("h4", null, "Đang chờ"));
    w.append(renderChain(row, D));
    for (const b of row.asks) {
      const line = el("div", "ask-line");
      line.append(el("span", "id", b.id));
      line.append(el("span", null, ` ${b.title}`));
      w.append(line);
    }
    if (row.blocked_by_note) w.append(el("p", "muted", row.blocked_by_note));
    body.append(w);
  }
  if ((D.blocks[row.id] || []).length) {
    const w = el("section", "sec");
    w.append(el("h4", null, "Đóng việc này sẽ mở khoá"));
    for (const id of D.blocks[row.id]) {
      const b = D.byId[id];
      const line = el("div", "ask-line");
      line.append(el("span", "id", id));
      line.append(el("span", null, ` ${b?.title || ""}`));
      w.append(line);
    }
    body.append(w);
  }
  if (row.source_doc) {
    const w = el("section", "sec");
    w.append(el("h4", null, "Nguồn trong repo"));
    w.append(el("code", "src", row.source_doc));
    body.append(w);
  }
  back.hidden = false;
  panel.classList.add("is-open");
  panel.focus();
}

function closeDrawer() {
  $("#drawer-back").hidden = true;
  $("#drawer").classList.remove("is-open");
}

/* ---------- sự kiện ---------- */
function wire(D) {
  for (const btn of document.querySelectorAll(".tab")) {
    btn.addEventListener("click", () => {
      for (const b of document.querySelectorAll(".tab")) b.classList.toggle("is-active", b === btn);
      STATE.tab = btn.dataset.tab;
      renderBoard(D);
    });
  }
  for (const btn of document.querySelectorAll(".afilter")) {
    btn.addEventListener("click", () => {
      for (const b of document.querySelectorAll(".afilter")) b.classList.toggle("is-active", b === btn);
      STATE.adrFilter = btn.dataset.f;
      renderAdr(D);
    });
  }
  $("#q").addEventListener("input", (e) => { STATE.q = e.target.value; renderBoard(D); });
  $("#drawer-close").addEventListener("click", closeDrawer);
  $("#drawer-back").addEventListener("click", closeDrawer);
  document.addEventListener("keydown", (e) => { if (e.key === "Escape") closeDrawer(); });
}

/* ---------- khởi động ---------- */
async function boot() {
  try {
    const res = await fetch("./data.json", { cache: "no-store" });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const d = await res.json();
    STATE.data = d;
    PEOPLE = d.people || {};
    const D = derive(d);
    renderHeader(D, d);
    renderKpis(D);
    renderDecisionQueue(D);
    renderBoard(D);
    renderAdr(D);
    wire(D);
    $("#boot").hidden = true;
    $("#boot").textContent = "";   // ẩn thôi thì chữ "Đang đọc…" vẫn nằm trong DOM
    $("#app").hidden = false;
  } catch (err) {
    const box = $("#boot");
    box.classList.add("boot-err");
    box.textContent = `Không đọc được ./data.json (${err.message}). ` +
      "Nếu đang mở tệp bằng file://, hãy chạy: python3 -m http.server -d portal 8000";
  }
}
boot();
