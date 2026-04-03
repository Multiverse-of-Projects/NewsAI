/* ============================================================
   NewsAI Dashboard — Application Logic
   Fetches via Netlify Functions, renders Chart.js & wordcloud2
   ============================================================ */

;(function () {
  'use strict';

  // ── Constants ──
  const API_BASE = '/api';
  const SENTIMENT_COLORS = {
    positive: { bg: 'rgba(16,185,129,.75)',  border: '#10b981' },
    negative: { bg: 'rgba(244,63,94,.75)',   border: '#f43f5e' },
    neutral:  { bg: 'rgba(245,158,11,.75)',  border: '#f59e0b' },
  };
  const SOURCE_PALETTE = [
    '#6366f1','#22d3ee','#8b5cf6','#f43f5e','#f59e0b',
    '#10b981','#ec4899','#14b8a6','#f97316','#a78bfa',
    '#38bdf8','#fb923c','#34d399','#e879f9','#facc15',
  ];

  // ── DOM refs ──
  const $  = (s) => document.querySelector(s);
  const $$ = (s) => document.querySelectorAll(s);

  const select        = $('#query-select');
  const analyzeBtn    = $('#analyze-btn');
  const btnLabel      = $('#btn-label');
  const errorBanner   = $('#error-banner');
  const errorText     = $('#error-text');
  const statsRibbon   = $('#stats-ribbon');
  const dashboard     = $('#dashboard');
  const articlesSection = $('#articles-section');
  const articlesGrid  = $('#articles-grid');
  const toast         = $('#toast');

  // Chart instances (for cleanup)
  let chartSentiment = null;
  let chartSources   = null;
  let chartTimeline  = null;
  let chartHeatmap   = null;

  // ── Init ──
  document.addEventListener('DOMContentLoaded', init);

  async function init() {
    setupIntersectionObserver();
    await loadQueries();
    select.addEventListener('change', onQueryChange);
    analyzeBtn.addEventListener('click', onAnalyze);
  }

  // ── API helpers ──
  async function apiFetch(path) {
    const res = await fetch(`${API_BASE}${path}`);
    if (!res.ok) {
      const body = await res.json().catch(() => ({}));
      throw new Error(body.error || `HTTP ${res.status}`);
    }
    return res.json();
  }

  // ── Load queries ──
  async function loadQueries() {
    try {
      const { queries } = await apiFetch('/get-queries');
      select.innerHTML = '<option value="">— Select a topic —</option>';
      queries.forEach((q) => {
        const opt = document.createElement('option');
        opt.value = q;
        opt.textContent = q;
        select.appendChild(opt);
      });
    } catch (err) {
      showError(`Failed to load queries: ${err.message}`);
      select.innerHTML = '<option value="">— Could not load —</option>';
    }
  }

  function onQueryChange() {
    analyzeBtn.disabled = !select.value;
  }

  // ── Analyze ──
  async function onAnalyze() {
    const query = select.value;
    if (!query) return;

    setLoading(true);
    hideError();

    try {
      const { articles } = await apiFetch(`/get-articles?query=${encodeURIComponent(query)}`);
      if (!articles || articles.length === 0) {
        showError('No articles found for this query.');
        setLoading(false);
        return;
      }
      renderDashboard(articles, query);
      showToast(`Loaded ${articles.length} articles`, 'success');
    } catch (err) {
      showError(`Analysis failed: ${err.message}`);
    } finally {
      setLoading(false);
    }
  }

  // ── Master render ──
  function renderDashboard(articles, query) {
    // Show sections
    statsRibbon.classList.remove('hidden');
    dashboard.classList.remove('hidden');
    articlesSection.classList.remove('hidden');

    renderStatsRibbon(articles);
    renderSentimentPie(articles);
    renderSourcesPolarArea(articles);
    renderTimeline(articles);
    renderWordCloud(articles);
    renderHeatmap(articles);
    renderArticleCards(articles);

    // Trigger scroll-reveal on cards
    requestAnimationFrame(() => {
      $$('.card, .article-card').forEach((el) => el.classList.add('visible'));
    });

    // Smooth scroll to stats
    statsRibbon.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }

  // ── Stats Ribbon ──
  function renderStatsRibbon(articles) {
    const total = articles.length;
    const sources = new Set(articles.map((a) => a.source)).size;
    const sentiments = {};
    articles.forEach((a) => {
      const s = (a.sentiment || 'neutral').toLowerCase();
      sentiments[s] = (sentiments[s] || 0) + 1;
    });
    const dominant = Object.entries(sentiments).sort((a, b) => b[1] - a[1])[0];

    // Date range
    const dates = articles
      .map((a) => new Date(a.publishedat))
      .filter((d) => !isNaN(d))
      .sort((a, b) => a - b);
    const dateRange = dates.length >= 2
      ? `${formatDate(dates[0])} — ${formatDate(dates[dates.length - 1])}`
      : dates.length === 1 ? formatDate(dates[0]) : 'N/A';

    statsRibbon.innerHTML = `
      <div class="stat-chip fade-in" style="animation-delay:.1s"><span class="icon">📄</span> <strong>${total}</strong> Articles</div>
      <div class="stat-chip fade-in" style="animation-delay:.2s"><span class="icon">🌐</span> <strong>${sources}</strong> Sources</div>
      <div class="stat-chip fade-in" style="animation-delay:.3s"><span class="icon">${sentimentIcon(dominant[0])}</span> Dominant: <strong>${capitalize(dominant[0])}</strong></div>
      <div class="stat-chip fade-in" style="animation-delay:.4s"><span class="icon">📅</span> ${dateRange}</div>
    `;
  }

  // ── Sentiment Doughnut ──
  function renderSentimentPie(articles) {
    const counts = {};
    articles.forEach((a) => {
      const s = (a.sentiment || 'neutral').toLowerCase();
      counts[s] = (counts[s] || 0) + 1;
    });

    const labels = Object.keys(counts).map(capitalize);
    const data   = Object.values(counts);
    const colors = Object.keys(counts).map((s) => (SENTIMENT_COLORS[s] || SENTIMENT_COLORS.neutral).bg);
    const borders= Object.keys(counts).map((s) => (SENTIMENT_COLORS[s] || SENTIMENT_COLORS.neutral).border);

    if (chartSentiment) chartSentiment.destroy();
    chartSentiment = new Chart($('#chart-sentiment'), {
      type: 'doughnut',
      data: {
        labels,
        datasets: [{
          data,
          backgroundColor: colors,
          borderColor: borders,
          borderWidth: 2,
          hoverOffset: 12,
        }],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        cutout: '60%',
        plugins: {
          legend: {
            position: 'bottom',
            labels: { color: '#94a3b8', font: { family: 'Inter', size: 13 }, padding: 16 },
          },
        },
      },
    });
  }

  // ── Source Polar Area ──
  function renderSourcesPolarArea(articles) {
    const counts = {};
    articles.forEach((a) => {
      const s = a.source || 'Unknown';
      counts[s] = (counts[s] || 0) + 1;
    });
    // Sort descending, keep top 12
    const sorted = Object.entries(counts).sort((a, b) => b[1] - a[1]).slice(0, 12);

    if (chartSources) chartSources.destroy();
    chartSources = new Chart($('#chart-sources'), {
      type: 'polarArea',
      data: {
        labels: sorted.map(([k]) => truncate(k, 22)),
        datasets: [{
          data: sorted.map(([, v]) => v),
          backgroundColor: SOURCE_PALETTE.slice(0, sorted.length).map((c) => c + 'cc'),
          borderColor: SOURCE_PALETTE.slice(0, sorted.length),
          borderWidth: 1,
        }],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          r: {
            ticks: { display: false },
            grid: { color: 'rgba(148,163,184,.08)' },
          },
        },
        plugins: {
          legend: {
            position: 'right',
            labels: { color: '#94a3b8', font: { family: 'Inter', size: 11 }, padding: 10, boxWidth: 14 },
          },
        },
      },
    });
  }

  // ── Sentiment Timeline ──
  function renderTimeline(articles) {
    // Group by date + sentiment
    const byDate = {};
    articles.forEach((a) => {
      const d = a.publishedat ? new Date(a.publishedat).toISOString().split('T')[0] : null;
      if (!d) return;
      const s = (a.sentiment || 'neutral').toLowerCase();
      if (!byDate[d]) byDate[d] = { positive: 0, negative: 0, neutral: 0 };
      byDate[d][s] = (byDate[d][s] || 0) + 1;
    });

    const dates = Object.keys(byDate).sort();
    const makeLine = (sentiment, color, borderColor) => ({
      label: capitalize(sentiment),
      data: dates.map((d) => byDate[d][sentiment] || 0),
      borderColor,
      backgroundColor: color,
      fill: true,
      tension: 0.4,
      pointRadius: 4,
      pointHoverRadius: 7,
      pointBackgroundColor: borderColor,
    });

    if (chartTimeline) chartTimeline.destroy();
    chartTimeline = new Chart($('#chart-timeline'), {
      type: 'line',
      data: {
        labels: dates.map((d) => {
          const dt = new Date(d);
          return dt.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
        }),
        datasets: [
          makeLine('positive', 'rgba(16,185,129,.12)', '#10b981'),
          makeLine('negative', 'rgba(244,63,94,.12)',  '#f43f5e'),
          makeLine('neutral',  'rgba(245,158,11,.12)', '#f59e0b'),
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        interaction: { mode: 'index', intersect: false },
        scales: {
          x: {
            ticks: { color: '#64748b', font: { size: 11 } },
            grid:  { color: 'rgba(148,163,184,.06)' },
          },
          y: {
            beginAtZero: true,
            ticks: { color: '#64748b', font: { size: 11 }, stepSize: 1 },
            grid:  { color: 'rgba(148,163,184,.06)' },
          },
        },
        plugins: {
          legend: {
            labels: { color: '#94a3b8', font: { family: 'Inter', size: 12 }, padding: 16, usePointStyle: true },
          },
        },
      },
    });
  }

  // ── Word Cloud ──
  function renderWordCloud(articles) {
    const freq = {};
    articles.forEach((a) => {
      if (Array.isArray(a.keywords)) {
        a.keywords.forEach((kw) => {
          if (typeof kw === 'string' && kw.trim()) {
            const word = kw.trim().toLowerCase();
            freq[word] = (freq[word] || 0) + 1;
          }
        });
      }
    });

    const list = Object.entries(freq)
      .sort((a, b) => b[1] - a[1])
      .slice(0, 80)
      .map(([word, count]) => [word, count * 10]);

    const canvas = $('#wordcloud-canvas');
    // Resize canvas for retina
    const rect = canvas.parentElement.getBoundingClientRect();
    canvas.width  = rect.width * 2;
    canvas.height = 700;

    if (list.length === 0) {
      const ctx = canvas.getContext('2d');
      ctx.fillStyle = '#64748b';
      ctx.font = '16px Inter';
      ctx.textAlign = 'center';
      ctx.fillText('No keywords available', canvas.width / 2, canvas.height / 2);
      return;
    }

    WordCloud(canvas, {
      list,
      gridSize: 8,
      weightFactor: 3,
      fontFamily: 'Outfit, Inter, sans-serif',
      color: function (word, weight) {
        const colors = ['#6366f1','#22d3ee','#8b5cf6','#f43f5e','#f59e0b','#10b981','#ec4899','#a78bfa','#38bdf8'];
        return colors[Math.floor(Math.random() * colors.length)];
      },
      rotateRatio: 0.3,
      rotationSteps: 2,
      backgroundColor: 'transparent',
      drawOutOfBound: false,
      shrinkToFit: true,
    });
  }

  // ── Heatmap (Bubble chart as approximation) ──
  function renderHeatmap(articles) {
    // Build matrix: source × date → count
    const sourceDates = {};
    const allDates  = new Set();
    const allSources = new Set();

    articles.forEach((a) => {
      const d = a.publishedat ? new Date(a.publishedat).toISOString().split('T')[0] : null;
      const s = a.source || 'Unknown';
      if (!d) return;
      allDates.add(d);
      allSources.add(s);
      const key = `${s}|${d}`;
      sourceDates[key] = (sourceDates[key] || 0) + 1;
    });

    const dates   = [...allDates].sort();
    const sources = [...allSources].sort();

    // Build bubble data
    const bubbleData = [];
    let maxCount = 1;
    sources.forEach((src, si) => {
      dates.forEach((dt, di) => {
        const v = sourceDates[`${src}|${dt}`] || 0;
        if (v > 0) {
          bubbleData.push({ x: di, y: si, r: Math.min(v * 6, 28), v });
          if (v > maxCount) maxCount = v;
        }
      });
    });

    if (chartHeatmap) chartHeatmap.destroy();
    chartHeatmap = new Chart($('#chart-heatmap'), {
      type: 'bubble',
      data: {
        datasets: [{
          label: 'Articles',
          data: bubbleData,
          backgroundColor: 'rgba(99,102,241,.45)',
          borderColor: '#6366f1',
          borderWidth: 1,
        }],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          x: {
            type: 'linear',
            min: -0.5,
            max: dates.length - 0.5,
            ticks: {
              stepSize: 1,
              color: '#64748b',
              font: { size: 10 },
              callback: (v) => {
                const idx = Math.round(v);
                if (idx >= 0 && idx < dates.length) {
                  const d = new Date(dates[idx]);
                  return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
                }
                return '';
              },
            },
            grid: { color: 'rgba(148,163,184,.06)' },
            title: { display: true, text: 'Date', color: '#64748b' },
          },
          y: {
            type: 'linear',
            min: -0.5,
            max: sources.length - 0.5,
            ticks: {
              stepSize: 1,
              color: '#94a3b8',
              font: { size: 10 },
              callback: (v) => {
                const idx = Math.round(v);
                return (idx >= 0 && idx < sources.length) ? truncate(sources[idx], 18) : '';
              },
            },
            grid: { color: 'rgba(148,163,184,.06)' },
            title: { display: true, text: 'Source', color: '#64748b' },
          },
        },
        plugins: {
          legend: { display: false },
          tooltip: {
            callbacks: {
              label: (ctx) => {
                const d = ctx.raw;
                const src = sources[d.y] || '?';
                const dt  = dates[d.x] || '?';
                return `${src} · ${dt}: ${d.v} article${d.v > 1 ? 's' : ''}`;
              },
            },
          },
        },
      },
    });
  }

  // ── Article Cards ──
  function renderArticleCards(articles) {
    articlesGrid.innerHTML = '';

    // Sort by date descending
    const sorted = [...articles].sort((a, b) => {
      return new Date(b.publishedat || 0) - new Date(a.publishedat || 0);
    });

    sorted.forEach((article, idx) => {
      const card = document.createElement('div');
      card.className = 'article-card';
      card.style.animationDelay = `${idx * 60}ms`;

      const sentiment  = (article.sentiment || 'neutral').toLowerCase();
      const badgeClass = `badge badge--${sentiment} badge--pulse`;
      const date       = article.publishedat ? formatDate(new Date(article.publishedat)) : '';
      const imgUrl     = article.urltoimage;
      const summaryHtml = article.summary ? marked.parse(article.summary) : '<em>No summary available.</em>';
      const keywords   = Array.isArray(article.keywords) ? article.keywords.slice(0, 6) : [];

      card.innerHTML = `
        ${imgUrl
          ? `<img class="article-card__image" src="${escapeHtml(imgUrl)}" alt="" loading="lazy" onerror="this.outerHTML='<div class=\\'article-card__image article-card__image--placeholder\\'>📰</div>'" />`
          : `<div class="article-card__image article-card__image--placeholder">📰</div>`
        }
        <div class="article-card__body">
          <div class="article-card__meta">
            <span class="article-card__source">${escapeHtml(article.source || 'Unknown')}</span>
            <span class="${badgeClass}">${sentimentIcon(sentiment)} ${capitalize(sentiment)}</span>
          </div>
          <div class="article-card__date">${date}</div>
          <h3 class="article-card__title">${escapeHtml(article.title || 'Untitled')}</h3>
          ${keywords.length ? `<div class="keywords-list">${keywords.map((k) => `<span class="keyword-pill">${escapeHtml(k)}</span>`).join('')}</div>` : ''}
          <div class="article-card__summary" id="summary-${idx}">${summaryHtml}</div>
          <div class="article-card__actions">
            <button class="btn-ghost" onclick="toggleSummary(${idx})">
              <span id="toggle-icon-${idx}">▼</span> Summary
            </button>
            ${article.url ? `<a class="btn-link" href="${escapeHtml(article.url)}" target="_blank" rel="noopener">Read full article ↗</a>` : ''}
          </div>
        </div>
      `;

      articlesGrid.appendChild(card);

      // Stagger visibility
      setTimeout(() => card.classList.add('visible'), 80 + idx * 60);
    });
  }

  // Global toggle for summary expand/collapse
  window.toggleSummary = function (idx) {
    const el = $(`#summary-${idx}`);
    const icon = $(`#toggle-icon-${idx}`);
    if (el) {
      el.classList.toggle('expanded');
      icon.textContent = el.classList.contains('expanded') ? '▲' : '▼';
    }
  };

  // ── Intersection Observer for scroll-reveal ──
  function setupIntersectionObserver() {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add('visible');
          }
        });
      },
      { threshold: 0.1, rootMargin: '0px 0px -40px 0px' }
    );

    // Re-observe whenever we render
    const mutObs = new MutationObserver(() => {
      $$('.card:not(.visible), .article-card:not(.visible)').forEach((el) => observer.observe(el));
    });
    mutObs.observe(document.body, { childList: true, subtree: true });
  }

  // ── UI helpers ──
  function setLoading(on) {
    analyzeBtn.disabled = on;
    if (on) {
      btnLabel.innerHTML = '<span class="spinner"></span> Analyzing…';
    } else {
      btnLabel.textContent = 'Analyze';
    }
  }

  function showError(msg) {
    errorText.textContent = msg;
    errorBanner.classList.remove('hidden');
  }
  function hideError() {
    errorBanner.classList.add('hidden');
  }

  function showToast(msg, type = 'success') {
    toast.textContent = msg;
    toast.className = `toast toast--${type} show`;
    setTimeout(() => toast.classList.remove('show'), 3000);
  }

  // ── Formatters ──
  function formatDate(d) {
    if (!(d instanceof Date)) d = new Date(d);
    return d.toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' });
  }

  function capitalize(s) {
    return s ? s.charAt(0).toUpperCase() + s.slice(1) : '';
  }

  function truncate(s, len) {
    return s.length > len ? s.slice(0, len - 1) + '…' : s;
  }

  function sentimentIcon(s) {
    switch ((s || '').toLowerCase()) {
      case 'positive': return '🟢';
      case 'negative': return '🔴';
      default:         return '🟡';
    }
  }

  function escapeHtml(str) {
    if (!str) return '';
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
  }

})();
