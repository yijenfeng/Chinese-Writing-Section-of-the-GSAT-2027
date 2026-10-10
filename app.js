/* 國寫學習地圖：互動功能（資料只存在這台裝置的瀏覽器） */
(function () {
  "use strict";
  var P = "gsat2027:";
  var PAGE = document.body.getAttribute("data-page") || "page";

  function get(k) { try { return localStorage.getItem(P + k); } catch (e) { return null; } }
  function set(k, v) {
    try {
      if (v === "" || v === null || v === undefined) localStorage.removeItem(P + k);
      else localStorage.setItem(P + k, v);
    } catch (e) {}
  }
  function allKeys() {
    var out = [];
    try { for (var i = 0; i < localStorage.length; i++) { var k = localStorage.key(i); if (k && k.indexOf(P) === 0) out.push(k); } } catch (e) {}
    return out;
  }
  function keyOf(el) {
    var k = el.getAttribute("data-save");
    return el.hasAttribute("data-global") ? k : PAGE + ":" + k;
  }
  function today() {
    var d = new Date();
    return d.getFullYear() + "-" + String(d.getMonth() + 1).padStart(2, "0") + "-" + String(d.getDate()).padStart(2, "0");
  }
  function download(name, text, type) {
    var blob = new Blob([text], { type: type || "text/plain;charset=utf-8" });
    var a = document.createElement("a");
    a.href = URL.createObjectURL(blob); a.download = name;
    document.body.appendChild(a); a.click();
    setTimeout(function () { URL.revokeObjectURL(a.href); a.remove(); }, 500);
  }
  function toast(msg) {
    var t = document.getElementById("toast");
    if (!t) { t = document.createElement("div"); t.id = "toast"; t.setAttribute("role", "status"); document.body.appendChild(t); }
    t.textContent = msg; t.classList.add("show");
    clearTimeout(t._h); t._h = setTimeout(function () { t.classList.remove("show"); }, 1800);
  }

  /* 1. 模板裡的空格變成可填寫的欄位 */
  document.querySelectorAll(".tpl").forEach(function (tpl, ti) {
    tpl.querySelectorAll(".blank").forEach(function (b, bi) {
      var inp = document.createElement("input");
      inp.type = "text"; inp.className = "blank-in";
      inp.setAttribute("data-save", "tpl" + ti + "-" + bi);
      inp.setAttribute("aria-label", "模板空格");
      b.replaceWith(inp);
    });
  });

  /* 2. 自動儲存所有 data-save 欄位 */
  function fit(el) {
    if (el.classList.contains("blank-in")) {
      el.style.width = Math.max(3.2, Math.min(18, (el.value.length || 0) * 1.05 + 1.2)) + "em";
    }
  }
  document.querySelectorAll("[data-save]").forEach(function (el) {
    var k = keyOf(el), v = get(k);
    if (el.type === "checkbox") {
      el.checked = v === "1";
      el.addEventListener("change", function () { set(k, el.checked ? "1" : ""); refresh(); });
    } else {
      if (v !== null) el.value = v;
      fit(el);
      var h;
      el.addEventListener("input", function () {
        fit(el);
        clearTimeout(h);
        h = setTimeout(function () { set(k, el.value.trim() ? el.value : ""); refresh(); flashSaved(el); }, 300);
      });
    }
  });
  function flashSaved(el) {
    var s = el.closest(".save-wrap");
    if (!s) return;
    var tag = s.querySelector(".saved");
    if (tag) { tag.classList.add("on"); clearTimeout(tag._h); tag._h = setTimeout(function () { tag.classList.remove("on"); }, 1200); }
  }

  /* 3. 題型判斷測驗 */
  document.querySelectorAll(".quiz").forEach(function (q, qi) {
    var ans = q.getAttribute("data-answer");
    var key = PAGE + ":quiz" + qi;
    var fb = q.querySelector(".quiz-fb");
    function show(choice) {
      q.querySelectorAll("button.opt").forEach(function (b) {
        b.classList.remove("right", "wrong");
        if (b.getAttribute("data-opt") === ans) b.classList.add("right");
        else if (b.getAttribute("data-opt") === choice) b.classList.add("wrong");
        b.setAttribute("aria-pressed", b.getAttribute("data-opt") === choice ? "true" : "false");
      });
      fb.hidden = false;
      fb.querySelector(".verdict").textContent = choice === ans ? "答對了。" : "再想想：正解是「" + ans + "」。";
      fb.classList.toggle("ok", choice === ans);
    }
    q.querySelectorAll("button.opt").forEach(function (b) {
      b.addEventListener("click", function () {
        var c = b.getAttribute("data-opt");
        set(key, c); show(c); refresh();
      });
    });
    var saved = get(key);
    if (saved) show(saved);
    var reset = q.querySelector(".quiz-reset");
    if (reset) reset.addEventListener("click", function () {
      set(key, ""); fb.hidden = true;
      q.querySelectorAll("button.opt").forEach(function (b) { b.classList.remove("right", "wrong"); b.setAttribute("aria-pressed", "false"); });
      refresh();
    });
  });

  /* 4. 素材卡進度 */
  var FIELDS = ["scene", "line", "me", "other", "turn", "now", "keys"];
  var FIELD_NAMES = ["場景（五感）", "關鍵一句話", "當時的我", "對方可能的想法", "轉折", "現在的我怎麼看", "可用關鍵詞"];
  function cardFilled(n) {
    var c = 0;
    FIELDS.forEach(function (f) { if (get("card:" + n + ":" + f)) c++; });
    return c;
  }
  function cardsDone() {
    var d = 0;
    for (var n = 1; n <= 12; n++) if (cardFilled(n) >= 5) d++;
    return d;
  }

  /* 5. 練習紀錄 */
  function loadLog() { try { return JSON.parse(get("log") || "[]"); } catch (e) { return []; } }
  function saveLog(a) { set("log", a.length ? JSON.stringify(a) : ""); }
  var logForm = document.getElementById("log-form");
  function renderLog() {
    var body = document.getElementById("log-body");
    if (!body) return;
    var a = loadLog();
    body.innerHTML = "";
    if (!a.length) {
      body.innerHTML = '<tr><td colspan="6" class="empty">還沒有紀錄。寫完一篇練習後，在上方填寫並按「加入紀錄」。</td></tr>';
      return;
    }
    a.slice().reverse().forEach(function (r, ri) {
      var idx = a.length - 1 - ri;
      var tr = document.createElement("tr");
      [r.date, r.title, r.type, r.grade, r.note].forEach(function (v) {
        var td = document.createElement("td"); td.textContent = v || ""; tr.appendChild(td);
      });
      var td = document.createElement("td");
      var del = document.createElement("button");
      del.type = "button"; del.className = "btn ghost small"; del.textContent = "刪除";
      del.addEventListener("click", function () {
        if (!confirm("刪除這筆紀錄？")) return;
        var b = loadLog(); b.splice(idx, 1); saveLog(b); renderLog(); refresh();
      });
      td.appendChild(del); tr.appendChild(td);
      body.appendChild(tr);
    });
  }
  if (logForm) {
    var dateIn = logForm.querySelector("[name=date]");
    if (dateIn && !dateIn.value) dateIn.value = today();
    logForm.addEventListener("submit", function (e) {
      e.preventDefault();
      var f = new FormData(logForm);
      var r = { date: f.get("date"), title: (f.get("title") || "").trim(), type: f.get("type"), grade: f.get("grade"), note: (f.get("note") || "").trim() };
      if (!r.title) { toast("請先填寫題目"); return; }
      var a = loadLog(); a.push(r); saveLog(a);
      logForm.querySelector("[name=title]").value = ""; logForm.querySelector("[name=note]").value = "";
      renderLog(); refresh(); toast("已加入練習紀錄");
    });
    renderLog();
  }

  /* 6. 進度數字 */
  function quizStats() {
    var right = 0, done = 0;
    allKeys().forEach(function (k) {
      var m = k.match(/:quiz(\d+)$/);
      if (!m) return;
      done++;
      var el = document.querySelectorAll(".quiz")[+m[1]];
      if (el && el.getAttribute("data-answer") === localStorage.getItem(k)) right++;
    });
    return { done: done, right: right };
  }
  function answered() {
    return allKeys().filter(function (k) { return /:q\d+$/.test(k); }).length;
  }
  function refresh() {
    var set_ = function (id, v) { var e = document.getElementById(id); if (e) e.textContent = v; };
    set_("p-cards", cardsDone());
    set_("p-log", loadLog().length);
    set_("p-answers", answered());
    var qd = allKeys().filter(function (k) { return /^gsat2027:看題判斷題型:quiz\d+$/.test(k); }).length;
    set_("p-quiz", qd);
    for (var n = 1; n <= 12; n++) {
      var b = document.getElementById("card-badge-" + n);
      if (b) {
        var c = cardFilled(n);
        b.textContent = c >= 5 ? "已完成 " + c + "/7" : "已填 " + c + "/7";
        b.classList.toggle("done", c >= 5);
      }
    }
    var bar = document.getElementById("cards-bar");
    if (bar) bar.style.width = (cardsDone() / 12 * 100) + "%";
    var qs = document.getElementById("quiz-score");
    if (qs) { var s = quizStats(); qs.textContent = s.done ? "已作答 " + s.done + " 題，答對 " + s.right + " 題" : "尚未作答"; }
  }
  refresh();

  /* 7. 匯出／匯入／下載素材卡 */
  function exportAll() {
    var data = {};
    allKeys().forEach(function (k) { data[k] = localStorage.getItem(k); });
    download("國寫學習資料-" + today() + ".json", JSON.stringify({ site: "gsat2027", saved: new Date().toISOString(), data: data }, null, 2), "application/json");
    toast("已下載備份檔");
  }
  function importAll(file) {
    var r = new FileReader();
    r.onload = function () {
      try {
        var o = JSON.parse(r.result);
        var d = o && o.data;
        if (!d || o.site !== "gsat2027") throw new Error("bad");
        if (!confirm("匯入會覆蓋這台裝置上相同欄位的內容，確定嗎？")) return;
        Object.keys(d).forEach(function (k) { if (k.indexOf(P) === 0) localStorage.setItem(k, d[k]); });
        toast("匯入完成"); setTimeout(function () { location.reload(); }, 600);
      } catch (e) { toast("這不是本站的備份檔"); }
    };
    r.readAsText(file);
  }
  function cardsText() {
    var titles = [];
    document.querySelectorAll(".mcard").forEach(function (c) { titles[+c.getAttribute("data-n")] = c.getAttribute("data-title"); });
    var out = "筱葳的經驗素材卡（匯出於 " + today() + "）\n\n";
    for (var n = 1; n <= 12; n++) {
      out += "【素材 #" + n + "】" + (titles[n] || "") + "\n";
      FIELDS.forEach(function (f, i) { out += FIELD_NAMES[i] + "：" + (get("card:" + n + ":" + f) || "") + "\n"; });
      out += "\n";
    }
    return out;
  }
  document.querySelectorAll("[data-action]").forEach(function (b) {
    var act = b.getAttribute("data-action");
    if (act === "export") b.addEventListener("click", exportAll);
    if (act === "import") {
      var fi = document.createElement("input");
      fi.type = "file"; fi.accept = "application/json,.json"; fi.hidden = true;
      fi.addEventListener("change", function () { if (fi.files[0]) importAll(fi.files[0]); fi.value = ""; });
      document.body.appendChild(fi);
      b.addEventListener("click", function () { fi.click(); });
    }
    if (act === "cards-txt") b.addEventListener("click", function () { download("經驗素材卡-" + today() + ".txt", cardsText()); toast("已下載素材卡文字檔"); });
    if (act === "print") b.addEventListener("click", function () { window.print(); });
    if (act === "uncheck") b.addEventListener("click", function () {
      var box = document.getElementById(b.getAttribute("data-target"));
      if (!box) return;
      box.querySelectorAll("input[type=checkbox]").forEach(function (c) { c.checked = false; set(keyOf(c), ""); });
      toast("已清除勾選");
    });
    if (act === "clear") b.addEventListener("click", function () {
      if (!confirm("清除這台裝置上本站所有填寫內容？建議先匯出備份。")) return;
      allKeys().forEach(function (k) { localStorage.removeItem(k); });
      toast("已清除"); setTimeout(function () { location.reload(); }, 600);
    });
  });

  /* 儲存不可用時提醒 */
  try { localStorage.setItem(P + "_t", "1"); localStorage.removeItem(P + "_t"); }
  catch (e) {
    var w = document.createElement("p");
    w.className = "store-warn";
    w.textContent = "這個瀏覽器目前無法儲存填寫內容（可能是無痕模式）。可以照常閱讀，但關閉後填寫的內容不會保留。";
    var pg = document.querySelector(".page");
    if (pg) pg.insertBefore(w, pg.firstChild);
  }
})();
