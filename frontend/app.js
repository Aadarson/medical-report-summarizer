const uploadBtn = document.getElementById("uploadBtn");
const fileInput = document.getElementById("fileInput");
const rawEl = document.getElementById("raw");
const valuesEl = document.getElementById("values");
const summaryEl = document.getElementById("summary");

uploadBtn.addEventListener("click", async () => {
  const file = fileInput.files[0];
  if (!file) {
    alert("Please select a file first.");
    return;
  }

  const formData = new FormData();
  formData.append("file", file);

  rawEl.textContent = "Processing...";
  valuesEl.innerHTML = "";
  summaryEl.textContent = "";

  try {
    const res = await fetch("http://127.0.0.1:8000/upload", {
      method: "POST",
      body: formData
    });

    if (!res.ok) throw new Error("Server error");

    const data = await res.json();

    rawEl.textContent = data.raw_text || "No text extracted.";
    displayInterpretedValues(data.interpreted || {});
    summaryEl.textContent = data.summary || "No summary available.";
  } catch (err) {
    rawEl.textContent = "Error: " + err.message;
  }
});

function displayInterpretedValues(interpreted) {
  if (!valuesEl) return;
  valuesEl.innerHTML = "";

  for (const [test, info] of Object.entries(interpreted)) {
    // row
    const collapsible = document.createElement('div');
    collapsible.className = 'collapsible';

    // left: badge + name
    const left = document.createElement('div');
    left.className = 'left';

    const badge = document.createElement('span');
    const status = info.status || 'normal';
    badge.className = 'badge ' + (status === 'high' ? 'high' : status === 'low' ? 'low' : 'normal');
    badge.textContent = status === 'high' ? '❌' : status === 'low' ? '⚠️' : '✅';

    const name = document.createElement('span');
    name.className = 'test-name';
    name.textContent = test;

    left.appendChild(badge);
    left.appendChild(name);

    // right: small preview value
    const preview = document.createElement('div');
    preview.className = 'value-preview';
    preview.textContent = (info.value !== undefined && info.value !== null) ? info.value : '—';

    collapsible.appendChild(left);
    collapsible.appendChild(preview);

    // content panel
    const content = document.createElement('div');
    content.className = 'content';
    const rng = info.range ? `${info.range.low ?? ''}-${info.range.high ?? ''} ${info.range.units ?? ''}`.trim() : "N/A";
    content.innerHTML = `
      <p style="margin:6px 0;">Value: ${info.value ?? '—'} (Ref: ${rng})</p>
      <p style="margin:6px 0;">Status: <strong style="color:${status==='high'?'red':status==='low'?'orange':'green'}">${status}</strong></p>
      ${info.note ? `<p style="margin:6px 0;">Note: ${info.note}</p>` : ''}
    `;

    // toggle
    collapsible.addEventListener('click', () => {
      content.classList.toggle('active');
    });

    // append to container
    valuesEl.appendChild(collapsible);
    valuesEl.appendChild(content);
  }
}
