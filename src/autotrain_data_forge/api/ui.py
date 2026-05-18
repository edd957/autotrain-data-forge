from __future__ import annotations

# ruff: noqa: E501


def render_ui() -> str:
    return """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>AutoTrain Data Forge</title>
  <style>
    :root {
      color-scheme: light;
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      background: #f7f8fb;
      color: #17202a;
    }
    body { margin: 0; }
    header {
      border-bottom: 1px solid #d9dee8;
      background: #ffffff;
      padding: 20px 28px;
    }
    main {
      display: grid;
      gap: 18px;
      grid-template-columns: minmax(320px, 0.9fr) minmax(360px, 1.1fr);
      padding: 24px 28px 32px;
    }
    h1 { font-size: 24px; margin: 0; letter-spacing: 0; }
    h2 { font-size: 16px; margin: 0 0 12px; letter-spacing: 0; }
    section {
      background: #ffffff;
      border: 1px solid #d9dee8;
      border-radius: 8px;
      padding: 18px;
    }
    textarea, pre, input, select {
      box-sizing: border-box;
      width: 100%;
      border: 1px solid #c6ceda;
      border-radius: 6px;
      font: 14px ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
      line-height: 1.5;
    }
    textarea { min-height: 220px; padding: 12px; resize: vertical; }
    input, select { padding: 9px 10px; margin-bottom: 10px; }
    button {
      border: 0;
      border-radius: 6px;
      background: #1f6feb;
      color: #ffffff;
      cursor: pointer;
      font-weight: 650;
      min-height: 40px;
      padding: 0 14px;
    }
    button.secondary { background: #2d333b; }
    .actions { display: flex; gap: 10px; flex-wrap: wrap; margin-top: 12px; }
    pre {
      background: #0d1117;
      color: #d6e2ff;
      min-height: 420px;
      overflow: auto;
      padding: 14px;
      white-space: pre-wrap;
    }
    @media (max-width: 860px) {
      main { grid-template-columns: 1fr; padding: 18px; }
    }
  </style>
</head>
<body>
  <header><h1>AutoTrain Data Forge</h1></header>
  <main>
    <section>
      <h2>Plan</h2>
      <textarea id="prompt">Collect text from https://example.com/ mentioning "docs", train locally, then delete raw data after training.</textarea>
      <div class="actions">
        <button onclick="parsePrompt()">Parse</button>
        <button class="secondary" onclick="reviewJob()">Review</button>
      </div>
      <h2 style="margin-top:18px">Base model</h2>
      <select id="baseModel"></select>
      <h2 style="margin-top:18px">Query</h2>
      <input id="modelDir" value="data/jobs/llm-planned-job/model" />
      <input id="question" value="What is in this dataset?" />
      <button onclick="queryModel()">Query Local Model</button>
    </section>
    <section>
      <h2>Output</h2>
      <pre id="output">{}</pre>
    </section>
  </main>
  <script>
    let currentJob = null;
    let baseModels = [];
    const output = document.getElementById("output");
    function write(value) {
      output.textContent = JSON.stringify(value, null, 2);
    }
    async function loadBaseModels() {
      const response = await fetch("/v1/base-models");
      baseModels = await response.json();
      const select = document.getElementById("baseModel");
      select.innerHTML = "";
      for (const model of baseModels) {
        const option = document.createElement("option");
        option.value = model.model_id;
        option.textContent = `${model.display_name} (${model.provider})`;
        select.appendChild(option);
      }
    }
    async function parsePrompt() {
      const prompt = document.getElementById("prompt").value;
      const response = await fetch("/v1/parse-request", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ prompt })
      });
      const data = await response.json();
      currentJob = data.job;
      const selected = baseModels.find(
        (model) => model.model_id === document.getElementById("baseModel").value
      );
      if (selected) currentJob.base_model = selected;
      data.job = currentJob;
      write(data);
    }
    async function reviewJob() {
      if (!currentJob) await parsePrompt();
      const response = await fetch("/v1/review", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(currentJob)
      });
      write(await response.json());
    }
    async function queryModel() {
      const response = await fetch("/v1/query", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          model_dir: document.getElementById("modelDir").value,
          question: document.getElementById("question").value,
          top_k: 5
        })
      });
      write(await response.json());
    }
    loadBaseModels();
  </script>
</body>
</html>"""
