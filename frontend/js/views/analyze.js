/**
 * Analyze View
 * Interactive text and image/meme OCR toxicity analysis workbench.
 */

import { api } from '../api.js';

export function renderAnalyze(container) {
  container.innerHTML = `
    <div style="margin-bottom: 24px;">
      <h2 style="font-size: 1.6rem; font-weight: 700;">Manual Content Toxicity Analyzer</h2>
      <p style="color: var(--text-secondary); font-size: 0.9rem;">
        Analyze text comments or upload meme images. Automatic language detection, OCR text extraction, and explainable AI scoring.
      </p>
    </div>

    <!-- Mode Selector Tabs (Mobile & Desktop Responsive) -->
    <div class="row g-2 mb-4">
      <div class="col-12 col-sm-6">
        <button id="tab-text-mode" class="btn btn-primary w-100">
          <i class="bi bi-chat-text-fill me-1"></i>
          Text Comment Analysis
        </button>
      </div>
      <div class="col-12 col-sm-6">
        <button id="tab-image-mode" class="btn btn-secondary w-100">
          <i class="bi bi-image me-1"></i>
          Image & Meme OCR Analysis
        </button>
      </div>
    </div>

    <!-- Main Analyzer Split Grid -->
    <div class="grid-2">
      <!-- Input Column -->
      <div class="card" id="input-card">
        <div class="card-header d-flex flex-wrap justify-content-between align-items-center gap-2">
          <div class="card-title mb-0">Content Input</div>
          <div class="d-flex align-items-center gap-2">
            <label for="select-lang" style="font-size:0.8rem; color:var(--text-secondary);" class="mb-0">Language:</label>
            <select id="select-lang" class="form-select form-select-sm" style="padding: 4px 10px; font-size: 0.82rem; min-width: 140px;">
              <option value="auto">Auto-Detect Language</option>
              <option value="hi">Hindi (Devanagari)</option>
              <option value="hinglish">Hinglish (Romanized Hindi)</option>
              <option value="en">English</option>
              <option value="kn">Kannada</option>
              <option value="ml">Malayalam</option>
              <option value="ta">Tamil</option>
              <option value="te">Telugu</option>
              <option value="mr">Marathi</option>
            </select>
          </div>
        </div>

        <!-- Text Input Form -->
        <div id="section-text-input">
          <div class="form-group">
            <textarea id="input-content-text" class="form-textarea" placeholder="Paste or type social media comment, tweet, or message here in Hindi, Hinglish, English, Tamil, Telugu, Kannada, Malayalam, or Marathi..." style="min-height: 140px; font-size: 0.95rem;"></textarea>
          </div>

          <!-- Quick Multilingual Test Prompts -->
          <div style="margin-bottom: 18px;">
            <div style="font-size: 0.78rem; font-weight: 600; color: var(--text-muted); margin-bottom: 8px; text-transform: uppercase;">Quick Test Samples:</div>
            <div style="display: flex; flex-wrap: wrap; gap: 6px;" id="quick-sample-chips">
              <button class="btn btn-secondary btn-sm sample-chip" data-lang="hi" data-text="भीड़ में बहुत हब्सी मिलेंगे साले बेवकूफ अपनी शक्ल देखी है?">Hindi Slur</button>
              <button class="btn btn-secondary btn-sm sample-chip" data-lang="hinglish" data-text="teri maa ki chut tu kutta hai saale kamine, video delete kar">Hinglish Vulgar</button>
              <button class="btn btn-secondary btn-sm sample-chip" data-lang="en" data-text="You are a filthy idiot and I will kill you, piece of shit">English Threat</button>
              <button class="btn btn-secondary btn-sm sample-chip" data-lang="ta" data-text="இப் புண்டா மவனே வீடியோ அளி டி தேவிடியா">Tamil Abuse</button>
              <button class="btn btn-secondary btn-sm sample-chip" data-lang="kn" data-text="ಸೂಳೆ ಮೂಡೆ ಅವ್ಳು ಕಾಂಗ್ರೆಸ್ ಸೂಪರ್ ಕಾಮಿಡಿ ಪೀಸಗಳು">Kannada Slur</button>
              <button class="btn btn-secondary btn-sm sample-chip" data-lang="te" data-text="విడు ఈపాటికి ఎంత మంది అమ్మయిలని దేగిండో వాడిని పట్టుకోండి">Telugu Abuse</button>
              <button class="btn btn-secondary btn-sm sample-chip" data-lang="hi" data-text="नमस्ते सर, आपका वीडियो देखकर बहुत कुछ सीखने को मिला। धन्यवाद!">Hindi Safe</button>
              <button class="btn btn-secondary btn-sm sample-chip" data-lang="hinglish" data-text="bhai thank you so much for this video really helpful">Hinglish Safe</button>
            </div>
          </div>
        </div>

        <!-- Image / Meme Input Form -->
        <div id="section-image-input" style="display: none;">
          <div id="drop-zone" style="border: 2px dashed var(--border-input); border-radius: var(--radius-md); padding: 30px; text-align: center; cursor: pointer; background: var(--drop-zone-bg); margin-bottom: 16px; transition: var(--transition);">
            <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="var(--primary)" stroke-width="1.5" style="margin-bottom: 8px;"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"/><circle cx="8.5" cy="8.5" r="1.5"/><polyline points="21 15 16 10 5 21"/></svg>
            <div style="font-weight: 600; margin-bottom: 4px;">Click to upload image or drag & drop</div>
            <div style="font-size: 0.8rem; color: var(--text-muted);">Supports PNG, JPEG, WEBP meme screenshots</div>
            <input type="file" id="file-image-input" accept="image/*" style="display: none;" />
          </div>

          <!-- Image Preview -->
          <div id="image-preview-container" style="display: none; margin-bottom: 16px; text-align: center;">
            <img id="image-preview" src="" style="max-height: 200px; border-radius: var(--radius-md); border: 1px solid var(--border-color); box-shadow: var(--shadow-sm);" />
          </div>

          <!-- Built-in Meme Preset Chips -->
          <div style="margin-bottom: 18px;">
            <div style="font-size: 0.78rem; font-weight: 600; color: var(--text-muted); margin-bottom: 8px; text-transform: uppercase;">Or Select Preset Meme Samples:</div>
            <div style="display: flex; gap: 8px; flex-wrap: wrap;">
              <button class="btn btn-secondary btn-sm meme-sample-btn" data-file="/static/assets/samples/sample_meme_threat.png">Threat Meme</button>
              <button class="btn btn-secondary btn-sm meme-sample-btn" data-file="/static/assets/samples/sample_meme_harassment.png">Cyberbullying Meme</button>
              <button class="btn btn-secondary btn-sm meme-sample-btn" data-file="/static/assets/samples/sample_meme_safe.png">Safe Community Meme</button>
            </div>
          </div>
        </div>

        <button id="btn-run-analysis" class="btn btn-primary" style="width: 100%;">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
          Run Multilingual Toxicity Analysis
        </button>
      </div>

      <!-- Results Column -->
      <div class="card" id="results-card">
        <div class="card-header">
          <div class="card-title">AI Evaluation Output</div>
          <span id="res-badge-status" class="badge badge-info">Awaiting Input</span>
        </div>

        <div id="results-placeholder" style="text-align: center; padding: 60px 20px; color: var(--text-muted);">
          <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" style="margin-bottom: 12px; opacity: 0.5;"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
          <div style="font-size: 1rem; font-weight: 500;">Ready to Analyze</div>
          <div style="font-size: 0.85rem; margin-top: 4px;">Submit a comment or meme on the left to see toxicity scores, detected categories, and AI explanations.</div>
        </div>

        <div id="results-body" style="display: none;">
          <!-- OCR Extracted Box (If Image) -->
          <div id="ocr-box" style="display: none; background: rgba(99, 102, 241, 0.08); border: 1px solid rgba(99, 102, 241, 0.25); border-radius: var(--radius-md); padding: 14px; margin-bottom: 16px;">
            <div style="display:flex; justify-content:space-between; font-size: 0.8rem; font-weight: 600; color: var(--primary-light); margin-bottom: 6px;">
              <span>OCR EXTRACTED TEXT</span>
              <span id="ocr-engine-tag" style="color: var(--text-muted);">Windows Media WinRT OCR</span>
            </div>
            <div id="ocr-text-display" style="font-size: 0.92rem; font-style: italic; color: var(--text-primary);"></div>
          </div>

          <!-- Top Metric Cards -->
          <div class="grid-2" style="margin-bottom: 16px;">
            <div style="background: var(--bg-input); padding: 14px; border-radius: var(--radius-md); border: 1px solid var(--border-color);">
              <div style="font-size: 0.78rem; color: var(--text-secondary); text-transform: uppercase; font-weight: 600;">Overall Toxicity</div>
              <div id="res-tox-score" style="font-size: 1.8rem; font-weight: 800; font-family: 'Outfit'; margin: 4px 0;">0%</div>
              <div class="category-bar-track" style="height: 6px;">
                <div id="res-tox-bar" class="category-bar-fill" style="width: 0%; background: var(--danger);"></div>
              </div>
            </div>

            <div style="background: var(--bg-input); padding: 14px; border-radius: var(--radius-md); border: 1px solid var(--border-color);">
              <div style="font-size: 0.78rem; color: var(--text-secondary); text-transform: uppercase; font-weight: 600;">Detected Language</div>
              <div id="res-lang-name" style="font-size: 1.25rem; font-weight: 700; font-family: 'Outfit'; margin: 4px 0;">English</div>
              <div id="res-lang-meta" style="font-size: 0.75rem; color: var(--text-secondary);">Script: Latin · 95% Confidence</div>
            </div>
          </div>

          <!-- Categories Detected -->
          <div style="margin-bottom: 16px;">
            <div style="font-size: 0.8rem; font-weight: 600; color: var(--text-secondary); margin-bottom: 8px;">CLASSIFIED CATEGORIES</div>
            <div id="res-category-tags" style="display: flex; flex-wrap: wrap; gap: 6px;"></div>
          </div>

          <!-- Highlighted Offending Content -->
          <div style="margin-bottom: 16px; background: var(--bg-card-subtle); border: 1px solid var(--border-color); border-radius: var(--radius-md); padding: 12px;">
            <div style="font-size: 0.78rem; font-weight: 600; color: var(--text-muted); margin-bottom: 6px; text-transform: uppercase;">Highlighted Offending Terms:</div>
            <div id="res-highlighted-text" style="font-size: 0.92rem; line-height: 1.6;"></div>
          </div>

          <!-- AI Explanation -->
          <div style="background: rgba(99, 102, 241, 0.08); border-left: 3px solid var(--primary); padding: 12px 14px; border-radius: 0 var(--radius-md) var(--radius-md) 0; margin-bottom: 16px;">
            <div style="font-weight: 600; font-size: 0.85rem; color: var(--primary-light); margin-bottom: 4px;">WHY THIS CONTENT WAS FLAGGED</div>
            <div id="res-explanation" style="font-size: 0.88rem; color: var(--text-primary); line-height: 1.5;"></div>
          </div>

          <!-- Recommended Action -->
          <div style="background: var(--bg-input); border: 1px solid var(--border-color); padding: 14px; border-radius: var(--radius-md); margin-bottom: 16px;">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom: 6px;">
              <span style="font-size: 0.8rem; font-weight: 600; color: var(--text-secondary);">RECOMMENDED ACTION</span>
              <span id="res-urgency-badge" class="badge badge-warning">High</span>
            </div>
            <div id="res-action-title" style="font-weight: 700; font-size: 0.95rem; margin-bottom: 6px;">Flag & Restrict Content</div>
            <ul id="res-action-steps" style="padding-left: 18px; font-size: 0.8rem; color: var(--text-secondary); line-height: 1.5;"></ul>
          </div>

          <!-- Human in the loop Actions & Disclaimer -->
          <div style="display:flex; gap: 10px; margin-bottom: 14px;">
            <button id="btn-add-to-queue" class="btn btn-primary" style="flex: 1;">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
              Send to Moderation Queue
            </button>
          </div>

          <div style="font-size: 0.72rem; color: var(--text-muted); font-style: italic; line-height: 1.4;">
            * AI-assisted detection. Predictions are probabilistic and subject to human oversight. Moderators maintain final override authority.
          </div>
        </div>
      </div>
    </div>
  `;

  // State
  let currentMode = 'text'; // 'text' or 'image'
  let selectedFile = null;
  let lastAnalysis = null;

  const tabText = container.querySelector('#tab-text-mode');
  const tabImage = container.querySelector('#tab-image-mode');
  const secText = container.querySelector('#section-text-input');
  const secImage = container.querySelector('#section-image-input');
  const runBtn = container.querySelector('#btn-run-analysis');
  const dropZone = container.querySelector('#drop-zone');
  const fileInput = container.querySelector('#file-image-input');
  const imgPreview = container.querySelector('#image-preview');
  const imgPreviewCont = container.querySelector('#image-preview-container');

  // Mode switching
  tabText.addEventListener('click', () => {
    currentMode = 'text';
    tabText.className = 'btn btn-primary';
    tabImage.className = 'btn btn-secondary';
    secText.style.display = 'block';
    secImage.style.display = 'none';
  });

  tabImage.addEventListener('click', () => {
    currentMode = 'image';
    tabImage.className = 'btn btn-primary';
    tabText.className = 'btn btn-secondary';
    secImage.style.display = 'block';
    secText.style.display = 'none';
  });

  // Sample Chips Click
  container.querySelectorAll('.sample-chip').forEach(btn => {
    btn.addEventListener('click', () => {
      container.querySelector('#input-content-text').value = btn.dataset.text;
      container.querySelector('#select-lang').value = btn.dataset.lang || 'auto';
    });
  });

  // Dropzone file handling
  dropZone.addEventListener('click', () => fileInput.click());
  fileInput.addEventListener('change', (e) => {
    if (e.target.files && e.target.files[0]) {
      selectedFile = e.target.files[0];
      const reader = new FileReader();
      reader.onload = (re) => {
        imgPreview.src = re.target.result;
        imgPreviewCont.style.display = 'block';
      };
      reader.readAsDataURL(selectedFile);
    }
  });

  // Meme sample buttons
  container.querySelectorAll('.meme-sample-btn').forEach(btn => {
    btn.addEventListener('click', async () => {
      const url = btn.dataset.file;
      try {
        const res = await fetch(url);
        const blob = await res.blob();
        selectedFile = new File([blob], url.split('/').pop(), { type: 'image/png' });
        imgPreview.src = url;
        imgPreviewCont.style.display = 'block';
        window.showToast("Loaded sample meme image!", "info");
      } catch (err) {
        window.showToast("Could not load meme file: " + err.message, "danger");
      }
    });
  });

  // Run Analysis Action
  runBtn.addEventListener('click', async () => {
    const lang = container.querySelector('#select-lang').value;
    runBtn.disabled = true;
    runBtn.innerHTML = `Analyzing with AI Models...`;

    try {
      let result;
      if (currentMode === 'text') {
        const text = container.querySelector('#input-content-text').value.trim();
        if (!text) {
          window.showToast("Please enter some text to analyze.", "warning");
          return;
        }
        result = await api.analyzeText(text, lang);
      } else {
        if (!selectedFile) {
          window.showToast("Please upload an image or choose a preset meme sample.", "warning");
          return;
        }
        result = await api.analyzeImage(selectedFile, lang);
      }

      lastAnalysis = result;
      displayAnalysisResults(result, container);
      window.showToast("Analysis complete!", "success");
    } catch (err) {
      window.showToast("Analysis failed: " + err.message, "danger");
      console.error(err);
    } finally {
      runBtn.disabled = false;
      runBtn.innerHTML = `
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
        Run Multilingual Toxicity Analysis
      `;
    }
  });

  // Add to Queue Action
  container.querySelector('#btn-add-to-queue')?.addEventListener('click', async () => {
    if (!lastAnalysis) return;
    try {
      await api.saveToQueue(lastAnalysis);
      window.showToast("Added item to Moderation Queue for review!", "success");
    } catch (err) {
      window.showToast("Failed to save: " + err.message, "danger");
    }
  });
}

function displayAnalysisResults(res, container) {
  container.querySelector('#results-placeholder').style.display = 'none';
  container.querySelector('#results-body').style.display = 'block';

  const tox = res.toxicity;
  const lang = res.language;
  const exp = res.explainability;
  const dec = res.decision;

  // Header status badge
  const statusBadge = container.querySelector('#res-badge-status');
  if (tox.is_toxic) {
    statusBadge.className = 'badge badge-danger';
    statusBadge.textContent = 'Flagged: Toxic Content';
  } else {
    statusBadge.className = 'badge badge-success';
    statusBadge.textContent = 'Safe / Compliant';
  }

  // OCR Box
  const ocrBox = container.querySelector('#ocr-box');
  if (res.content_type === 'image' && res.ocr) {
    ocrBox.style.display = 'block';
    container.querySelector('#ocr-engine-tag').textContent = res.ocr.engine || 'WinRT OCR';
    container.querySelector('#ocr-text-display').textContent = res.ocr.extracted_text || '(No text detected)';
  } else {
    ocrBox.style.display = 'none';
  }

  // Toxicity Score & Progress Bar
  const scoreElem = container.querySelector('#res-tox-score');
  const barElem = container.querySelector('#res-tox-bar');
  scoreElem.textContent = `${tox.percentage}%`;
  barElem.style.width = `${tox.percentage}%`;

  if (tox.percentage > 70) {
    scoreElem.style.color = 'var(--danger)';
    barElem.style.background = 'var(--danger)';
  } else if (tox.percentage > 30) {
    scoreElem.style.color = 'var(--warning)';
    barElem.style.background = 'var(--warning)';
  } else {
    scoreElem.style.color = 'var(--success)';
    barElem.style.background = 'var(--success)';
  }

  // Language Meta
  container.querySelector('#res-lang-name').textContent = lang.language_name;
  container.querySelector('#res-lang-meta').textContent = `Script: ${lang.script} · ${Math.round(lang.confidence * 100)}% Confidence ${lang.is_code_mixed ? '· Code-Mixed' : ''}`;

  // Categories
  const catCont = container.querySelector('#res-category-tags');
  catCont.innerHTML = tox.flagged_categories.map(c => {
    const isSafe = c === 'Non-toxic/Safe';
    return `<span class="badge ${isSafe ? 'badge-success' : 'badge-danger'}" style="font-size:0.8rem; padding: 4px 10px;">${c}</span>`;
  }).join(' ');

  // Highlighted Text
  container.querySelector('#res-highlighted-text').innerHTML = exp.highlighted_text || res.original_text;

  // Explanation
  container.querySelector('#res-explanation').textContent = exp.explanation;

  // Action & Urgency
  container.querySelector('#res-urgency-badge').textContent = dec.urgency_level;
  container.querySelector('#res-urgency-badge').className = `badge badge-${dec.severity_badge || 'warning'}`;
  container.querySelector('#res-action-title').textContent = dec.recommended_action;

  const stepsCont = container.querySelector('#res-action-steps');
  if (dec.next_steps) {
    stepsCont.innerHTML = dec.next_steps.map(s => `<li>${s}</li>`).join('');
  }
}
