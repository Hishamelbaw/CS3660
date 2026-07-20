const API_BASE = window.API_BASE_URL || "";

let lastGenerated = null; // { job_description, candidate_profile, backend_used, resume_text, cover_letter_text, infographic_svg, resume_pdf_base64, cover_letter_pdf_base64 }

function base64ToBlobUrl(base64, mimeType) {
  const bytes = atob(base64);
  const buffer = new Uint8Array(bytes.length);
  for (let i = 0; i < bytes.length; i++) {
    buffer[i] = bytes.charCodeAt(i);
  }
  const blob = new Blob([buffer], { type: mimeType });
  return URL.createObjectURL(blob);
}

function setStatus(elementId, message, isError = false) {
  const el = document.getElementById(elementId);
  el.textContent = message;
  el.style.color = isError ? "#dc2626" : "";
}

async function handleGenerateSubmit(event) {
  event.preventDefault();

  const jobDescription = document.getElementById("job-description").value;
  const candidateProfile = document.getElementById("candidate-profile").value;
  const button = document.getElementById("generate-button");

  button.disabled = true;
  setStatus("generate-status", "Generating... this can take a while.");

  try {
    const response = await fetch(`${API_BASE}/api/generate`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        job_description: jobDescription,
        candidate_profile: candidateProfile,
      }),
    });

    if (!response.ok) {
      const detail = await response.json().catch(() => ({}));
      throw new Error(detail.detail || `Request failed (${response.status})`);
    }

    const data = await response.json();
    lastGenerated = {
      job_description: jobDescription,
      candidate_profile: candidateProfile,
      ...data,
    };

    renderResults(data);
    setStatus("generate-status", "Done.");
  } catch (err) {
    setStatus("generate-status", err.message, true);
  } finally {
    button.disabled = false;
  }
}

function renderResults(data) {
  document.getElementById("results-section").classList.remove("hidden");
  document.getElementById("results-backend").textContent = data.backend_used;
  document.getElementById("resume-text").textContent = data.resume_text;
  document.getElementById("cover-letter-text").textContent = data.cover_letter_text;
  document.getElementById("infographic").innerHTML = data.infographic_svg;

  const resumeUrl = base64ToBlobUrl(data.resume_pdf_base64, "application/pdf");
  const coverLetterUrl = base64ToBlobUrl(data.cover_letter_pdf_base64, "application/pdf");
  document.getElementById("download-resume").href = resumeUrl;
  document.getElementById("download-cover-letter").href = coverLetterUrl;
}

async function handleSaveDraft() {
  if (!lastGenerated) {
    return;
  }
  const title = document.getElementById("draft-title").value.trim();
  if (!title) {
    setStatus("save-status", "Give the draft a title first.", true);
    return;
  }

  setStatus("save-status", "Saving...");
  try {
    const response = await fetch(`${API_BASE}/api/drafts`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        title,
        job_description: lastGenerated.job_description,
        candidate_profile: lastGenerated.candidate_profile,
        backend_used: lastGenerated.backend_used,
        resume_text: lastGenerated.resume_text,
        cover_letter_text: lastGenerated.cover_letter_text,
        infographic_svg: lastGenerated.infographic_svg,
      }),
    });

    if (!response.ok) {
      throw new Error(`Save failed (${response.status})`);
    }

    document.getElementById("draft-title").value = "";
    setStatus("save-status", "Saved.");
    await loadDrafts();
  } catch (err) {
    setStatus("save-status", err.message, true);
  }
}

async function loadDrafts() {
  const response = await fetch(`${API_BASE}/api/drafts`);
  const drafts = await response.json();

  const list = document.getElementById("drafts-list");
  list.innerHTML = "";

  for (const draft of drafts) {
    const li = document.createElement("li");

    const checkbox = document.createElement("input");
    checkbox.type = "checkbox";
    checkbox.value = draft.id;
    checkbox.addEventListener("change", updateCompareButtonState);

    const title = document.createElement("span");
    title.className = "draft-title";
    title.textContent = draft.title;

    const meta = document.createElement("span");
    meta.className = "draft-meta";
    meta.textContent = `${draft.backend_used} - ${new Date(draft.created_at).toLocaleString()}`;

    const openButton = document.createElement("button");
    openButton.textContent = "Open";
    openButton.addEventListener("click", () => openDraft(draft.id));

    const deleteButton = document.createElement("button");
    deleteButton.textContent = "Delete";
    deleteButton.addEventListener("click", () => deleteDraft(draft.id));

    li.append(checkbox, title, meta, openButton, deleteButton);
    list.appendChild(li);
  }

  updateCompareButtonState();
}

async function openDraft(draftId) {
  const response = await fetch(`${API_BASE}/api/drafts/${draftId}`);
  if (!response.ok) {
    return;
  }
  const draft = await response.json();

  document.getElementById("job-description").value = draft.job_description;
  document.getElementById("candidate-profile").value = draft.candidate_profile;

  lastGenerated = {
    job_description: draft.job_description,
    candidate_profile: draft.candidate_profile,
    backend_used: draft.backend_used,
    resume_text: draft.resume_text,
    cover_letter_text: draft.cover_letter_text,
    infographic_svg: draft.infographic_svg,
    resume_pdf_base64: null,
    cover_letter_pdf_base64: null,
  };

  document.getElementById("results-section").classList.remove("hidden");
  document.getElementById("results-backend").textContent = draft.backend_used;
  document.getElementById("resume-text").textContent = draft.resume_text;
  document.getElementById("cover-letter-text").textContent = draft.cover_letter_text;
  document.getElementById("infographic").innerHTML = draft.infographic_svg;
  document.getElementById("download-resume").removeAttribute("href");
  document.getElementById("download-cover-letter").removeAttribute("href");
}

async function deleteDraft(draftId) {
  await fetch(`${API_BASE}/api/drafts/${draftId}`, { method: "DELETE" });
  await loadDrafts();
}

function updateCompareButtonState() {
  const checked = document.querySelectorAll("#drafts-list input[type=checkbox]:checked");
  document.getElementById("compare-button").disabled = checked.length !== 2;
}

async function handleCompare() {
  const checked = [...document.querySelectorAll("#drafts-list input[type=checkbox]:checked")];
  if (checked.length !== 2) {
    return;
  }

  const [draftA, draftB] = await Promise.all(
    checked.map((cb) => fetch(`${API_BASE}/api/drafts/${cb.value}`).then((r) => r.json()))
  );

  const view = document.getElementById("compare-view");
  view.innerHTML = "";
  for (const draft of [draftA, draftB]) {
    const col = document.createElement("div");
    col.className = "compare-col";

    const title = document.createElement("h3");
    title.textContent = draft.title;

    const meta = document.createElement("p");
    meta.className = "draft-meta";
    meta.textContent = `${draft.backend_used} - ${new Date(draft.created_at).toLocaleString()}`;

    const resumeHeading = document.createElement("h4");
    resumeHeading.textContent = "Resume";
    const resumePre = document.createElement("pre");
    resumePre.textContent = draft.resume_text;

    const coverHeading = document.createElement("h4");
    coverHeading.textContent = "Cover Letter";
    const coverPre = document.createElement("pre");
    coverPre.textContent = draft.cover_letter_text;

    const fitHeading = document.createElement("h4");
    fitHeading.textContent = "Company Fit";
    const fitDiv = document.createElement("div");
    fitDiv.innerHTML = draft.infographic_svg; // server-generated SVG; text fields are html-escaped there

    col.append(title, meta, resumeHeading, resumePre, coverHeading, coverPre, fitHeading, fitDiv);
    view.appendChild(col);
  }

  document.getElementById("compare-section").classList.remove("hidden");
}

document.getElementById("generate-form").addEventListener("submit", handleGenerateSubmit);
document.getElementById("save-draft-button").addEventListener("click", handleSaveDraft);
document.getElementById("compare-button").addEventListener("click", handleCompare);

loadDrafts();
