"use strict";

const state = {
  questionType: null,
  dataset: null,
  model: "",
  queries: [],
  activeQueryName: null,
};

const modalState = {
  dataset: null,
  table: null,
  offset: 0,
  total: 0,
  loading: false,
};

const el = {
  questionType: document.getElementById("questionType"),
  dataset: document.getElementById("dataset"),
  model: document.getElementById("model"),
  search: document.getElementById("search"),
  queryList: document.getElementById("queryList"),
  queryCount: document.getElementById("queryCount"),
  detail: document.getElementById("detail"),
  modal: document.getElementById("tableModal"),
  modalTitle: document.getElementById("modalTitle"),
  modalTable: document.getElementById("modalTable"),
  modalStatus: document.getElementById("modalStatus"),
  modalSentinel: document.getElementById("modalSentinel"),
  modalCodebook: document.getElementById("modalCodebook"),
  modalClose: document.getElementById("modalClose"),
};

async function fetchJSON(url) {
  const res = await fetch(url);
  if (!res.ok) {
    throw new Error(`${url} -> ${res.status}`);
  }
  return res.json();
}

function escapeHtml(value) {
  return String(value ?? "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

function populateSelect(selectEl, items, { keepSelection = true } = {}) {
  const previous = selectEl.value;
  selectEl.innerHTML = "";

  for (const item of items) {
    const opt = document.createElement("option");
    opt.value = item.value;
    opt.textContent = item.label;
    selectEl.appendChild(opt);
  }

  if (keepSelection && items.some((i) => i.value === previous)) {
    selectEl.value = previous;
  } else if (items.length) {
    selectEl.value = items[0].value;
  }
}

// ==================================================
// bootstrap
// ==================================================

async function init() {
  const config = await fetchJSON("/api/config");

  if (!config.question_types.length || !config.source_datasets.length) {
    el.detail.innerHTML = `<div class="empty-state">No data found under raw_data/ or processed/.</div>`;
    return;
  }

  populateSelect(
    el.questionType,
    config.question_types.map((qt) => ({ value: qt, label: qt })),
  );
  populateSelect(
    el.dataset,
    config.source_datasets.map((d) => ({ value: d, label: d })),
  );

  state.questionType = el.questionType.value;
  state.dataset = el.dataset.value;

  el.questionType.addEventListener("change", onSelectionChanged);
  el.dataset.addEventListener("change", onSelectionChanged);
  el.model.addEventListener("change", onModelChanged);
  el.modalClose.addEventListener("click", closeModal);
  el.modal.addEventListener("click", (e) => {
    if (e.target === el.modal) closeModal();
  });

  let searchTimer = null;
  el.search.addEventListener("input", () => {
    clearTimeout(searchTimer);
    searchTimer = setTimeout(() => renderSidebar(), 120);
  });

  await refreshModels();
  await refreshQueries();
}

async function onSelectionChanged() {
  state.questionType = el.questionType.value;
  state.dataset = el.dataset.value;
  await refreshModels();
  await refreshQueries();
}

async function onModelChanged() {
  state.model = el.model.value;
  await refreshQueries();
}

async function refreshModels() {
  const models = await fetchJSON(
    `/api/models?question_type=${encodeURIComponent(state.questionType)}&dataset=${encodeURIComponent(state.dataset)}`,
  );

  const options = [{ value: "", label: "— benchmark only —" }].concat(
    models.map((m) => ({ value: m, label: m })),
  );
  populateSelect(el.model, options);
  state.model = el.model.value;
}

async function refreshQueries() {
  const url = `/api/queries?question_type=${encodeURIComponent(state.questionType)}&dataset=${encodeURIComponent(state.dataset)}${state.model ? `&model=${encodeURIComponent(state.model)}` : ""}`;
  state.queries = await fetchJSON(url);

  const stillPresent = state.queries.some((q) => q.query_name === state.activeQueryName);
  if (!stillPresent) {
    state.activeQueryName = state.queries.length ? state.queries[0].query_name : null;
  }

  renderSidebar();

  if (state.activeQueryName) {
    selectQuery(state.activeQueryName);
  } else {
    el.detail.innerHTML = `<div class="empty-state">No queries found for this selection.</div>`;
  }
}

// ==================================================
// sidebar
// ==================================================

function evalBadgeMeta(evalInfo) {
  if (!evalInfo || !evalInfo.comparison_status) {
    return { cls: "pending", label: "—" };
  }
  if (evalInfo.comparison_status !== "success") {
    return { cls: "failed", label: "failed" };
  }
  return evalInfo.answer === "yes"
    ? { cls: "correct", label: "correct" }
    : { cls: "incorrect", label: "incorrect" };
}

function renderSidebar() {
  const filter = el.search.value.trim().toLowerCase();

  const filtered = state.queries.filter((q) => {
    if (!filter) return true;
    return (
      q.query_name.toLowerCase().includes(filter) ||
      (q.question || "").toLowerCase().includes(filter)
    );
  });

  el.queryCount.textContent = `${filtered.length} / ${state.queries.length} queries`;

  el.queryList.innerHTML = filtered
    .map((q) => {
      const dotCls = q.check_if_code_works === "yes" ? "yes" : q.check_if_code_works === "no" ? "no" : "unknown";
      const active = q.query_name === state.activeQueryName ? "active" : "";
      const badge = state.model ? evalBadgeMeta(q.eval) : null;

      return `
        <li class="query-item ${active}" data-query="${escapeHtml(q.query_name)}">
          <div class="query-item-top">
            <span class="dot ${dotCls}" title="check_if_code_works: ${escapeHtml(q.check_if_code_works || "unknown")}"></span>
            <span class="query-name">${escapeHtml(q.query_name)}</span>
            ${badge ? `<span class="badge ${badge.cls}">${badge.label}</span>` : ""}
          </div>
          <div class="query-question">${escapeHtml(q.question || "(no question text)")}</div>
        </li>`;
    })
    .join("");

  el.queryList.querySelectorAll(".query-item").forEach((node) => {
    node.addEventListener("click", () => {
      state.activeQueryName = node.dataset.query;
      renderSidebar();
      selectQuery(state.activeQueryName);
    });
  });
}

// ==================================================
// detail panel
// ==================================================

async function selectQuery(queryName) {
  const url = `/api/query_detail?question_type=${encodeURIComponent(state.questionType)}&dataset=${encodeURIComponent(state.dataset)}&query_name=${encodeURIComponent(queryName)}${state.model ? `&model=${encodeURIComponent(state.model)}` : ""}`;

  el.detail.innerHTML = `<div class="empty-state">Loading…</div>`;
  const data = await fetchJSON(url);
  renderDetail(queryName, data);
}

function renderMiniTable(preview) {
  if (!preview) {
    return `<div class="muted">No answer file found.</div>`;
  }
  if (!preview.rows.length) {
    return `<div class="muted">Empty result (0 rows).</div>`;
  }

  const head = preview.columns.map((c) => `<th>${escapeHtml(c)}</th>`).join("");
  const body = preview.rows
    .map((row) => `<tr>${preview.columns.map((c) => `<td>${escapeHtml(row[c])}</td>`).join("")}</tr>`)
    .join("");

  const note = preview.truncated
    ? `<div class="muted">Showing first ${preview.rows.length} of ${preview.total_rows} rows.</div>`
    : "";

  return `<div class="table-wrap"><table><thead><tr>${head}</tr></thead><tbody>${body}</tbody></table></div>${note}`;
}

function renderBenchmarkCard(benchmark) {
  const tablesChips = benchmark.tables
    .map((t) => `<span class="chip" data-table="${escapeHtml(t)}">${escapeHtml(t)}</span>`)
    .join("");

  return `
    <div class="card">
      <div class="card-header">
        <span class="card-title">Benchmark (ground truth)</span>
      </div>
      <div class="card-body">
        <div class="section-label">Tables engaged</div>
        <div class="chip-row">${tablesChips || '<span class="muted">none</span>'}</div>

        <div class="section-label">Generated pandas code</div>
        ${benchmark.gold_script ? `<pre class="code">${escapeHtml(benchmark.gold_script)}</pre>` : `<div class="muted">Script not found (${escapeHtml(benchmark.gold_script_path)}).</div>`}

        <div class="section-label">Gold answer</div>
        ${renderMiniTable(benchmark.gold_answer)}
      </div>
    </div>`;
}

function renderModelCard(model) {
  if (!model) {
    return `
      <div class="card">
        <div class="card-header"><span class="card-title">Model</span></div>
        <div class="card-body"><div class="muted">Select a model above to compare its output.</div></div>
      </div>`;
  }

  const badge = evalBadgeMeta(model.eval);

  return `
    <div class="card">
      <div class="card-header">
        <span class="card-title">Model: ${escapeHtml(model.model)}</span>
        <span class="badge ${badge.cls}" style="margin-left:auto">${badge.label}</span>
      </div>
      <div class="card-body">
        <div class="section-label">Generated pandas code</div>
        ${model.predicted_script ? `<pre class="code">${escapeHtml(model.predicted_script)}</pre>` : `<div class="muted">No script produced by this model for this query.</div>`}

        <div class="section-label">Predicted answer</div>
        ${renderMiniTable(model.predicted_answer)}

        <div class="section-label">Judge explanation</div>
        ${
          model.explanation
            ? `<div class="explanation-block">${escapeHtml(model.explanation)}</div>`
            : model.eval && model.eval.comparison_status === "success" && model.eval.answer === "yes"
              ? `<div class="muted">Marked correct — no explanation needed.</div>`
              : `<div class="muted">No explanation available.</div>`
        }

        ${
          model.raw_response
            ? `<details class="collapsible"><summary>Raw judge response</summary><div class="explanation-block">${escapeHtml(model.raw_response)}</div></details>`
            : ""
        }
        ${
          model.debug
            ? `<details class="collapsible"><summary>Failure debug log</summary><div class="explanation-block">${escapeHtml(model.debug)}</div></details>`
            : ""
        }
      </div>
    </div>`;
}

function renderDetail(queryName, data) {
  const b = data.benchmark;

  el.detail.innerHTML = `
    <div class="detail-header">
      <div class="query-name">${escapeHtml(queryName)}</div>
      <div class="detail-question">${escapeHtml(b.natural_question || "(no question)")}</div>
      ${b.question_from_llm ? `<div class="detail-question-draft">Draft question: ${escapeHtml(b.question_from_llm)}</div>` : ""}
    </div>
    <div class="columns">
      ${renderBenchmarkCard(b)}
      ${renderModelCard(data.model)}
    </div>
  `;

  el.detail.querySelectorAll(".chip[data-table]").forEach((chip) => {
    chip.addEventListener("click", () => openTableModal(chip.dataset.table));
  });
}

// ==================================================
// table modal (raw dataset tables, paginated / infinite scroll)
// ==================================================

let sentinelObserver = null;

async function openTableModal(table) {
  modalState.dataset = state.dataset;
  modalState.table = table;
  modalState.offset = 0;
  modalState.total = 0;
  modalState.loading = false;

  el.modalTitle.textContent = `${state.dataset} / ${table}.dta`;
  el.modalTable.querySelector("thead tr").innerHTML = "";
  el.modalTable.querySelector("tbody").innerHTML = "";
  el.modalStatus.textContent = "";
  el.modalCodebook.textContent = "Loading metadata…";
  el.modal.classList.remove("hidden");

  loadCodebook(table);
  await loadMoreRows();

  if (sentinelObserver) sentinelObserver.disconnect();
  sentinelObserver = new IntersectionObserver((entries) => {
    if (entries[0].isIntersecting) loadMoreRows();
  });
  sentinelObserver.observe(el.modalSentinel);
}

function closeModal() {
  el.modal.classList.add("hidden");
  if (sentinelObserver) sentinelObserver.disconnect();
}

async function loadCodebook(table) {
  try {
    const data = await fetchJSON(
      `/api/codebook?dataset=${encodeURIComponent(state.dataset)}&table=${encodeURIComponent(table)}`,
    );
    el.modalCodebook.textContent = data.text || "No metadata description available for this table.";
  } catch {
    el.modalCodebook.textContent = "No metadata description available for this table.";
  }
}

async function loadMoreRows() {
  if (modalState.loading) return;
  if (modalState.total && modalState.offset >= modalState.total) return;

  modalState.loading = true;
  el.modalStatus.textContent = "Loading…";

  try {
    const data = await fetchJSON(
      `/api/table?dataset=${encodeURIComponent(modalState.dataset)}&table=${encodeURIComponent(modalState.table)}&offset=${modalState.offset}&limit=200`,
    );

    if (modalState.offset === 0) {
      el.modalTable.querySelector("thead tr").innerHTML = data.columns
        .map((c) => `<th>${escapeHtml(c)}</th>`)
        .join("");
    }

    const tbody = el.modalTable.querySelector("tbody");
    const fragment = document.createDocumentFragment();

    for (const row of data.rows) {
      const tr = document.createElement("tr");
      tr.innerHTML = data.columns.map((c) => `<td>${escapeHtml(row[c])}</td>`).join("");
      fragment.appendChild(tr);
    }
    tbody.appendChild(fragment);

    modalState.offset += data.rows.length;
    modalState.total = data.total_rows;

    el.modalStatus.textContent =
      modalState.offset >= modalState.total
        ? `All ${modalState.total} rows loaded.`
        : `${modalState.offset} / ${modalState.total} rows loaded — scroll for more.`;
  } catch (err) {
    el.modalStatus.textContent = `Failed to load table: ${err.message}`;
  } finally {
    modalState.loading = false;
  }
}

init();
