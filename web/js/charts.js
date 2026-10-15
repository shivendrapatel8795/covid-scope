/* CovidScope — Interactive Chart.js visualisations with animations */

const COLORS = {
  India: "#0F766E",
  "United States": "#6366F1",
  Brazil: "#F59E0B",
  "United Kingdom": "#EF4444",
};

const LABELS = ["Jan 2021", "Feb 2021", "Mar 2021", "Apr 2021", "May 2021", "Jun 2021"];

const DATA = {
  cases: {
    India: [18000, 12000, 53000, 386000, 392000, 46000],
    "United States": [205000, 85000, 68000, 52000, 26000, 14000],
    Brazil: [58000, 52000, 78000, 72000, 64000, 46000],
    "United Kingdom": [53000, 11000, 5000, 2500, 3500, 9500],
  },
  deaths: {
    India: [250, 100, 350, 3400, 3700, 900],
    "United States": [3300, 1900, 1100, 700, 500, 350],
    Brazil: [1100, 1150, 2200, 3000, 2100, 1700],
    "United Kingdom": [900, 500, 150, 30, 15, 20],
  },
  vaccinated: {
    India: [0.2, 0.9, 4.5, 8.0, 12.5, 20.0],
    "United States": [1.8, 10.4, 28.8, 43.0, 50.1, 55.4],
    Brazil: [0.1, 1.6, 6.0, 12.4, 21.7, 30.5],
    "United Kingdom": [1.4, 17.8, 42.2, 51.1, 57.5, 62.0],
  },
};

// Totals for bar charts
const TOTAL_DEATHS = {
  India: 8700,
  "United States": 7850,
  Brazil: 11250,
  "United Kingdom": 1615,
};

const LATEST_CASES = {
  India: 46000,
  "United States": 14000,
  Brazil: 46000,
  "United Kingdom": 9500,
};

const TOTAL_CASES = {
  India: 907000,
  "United States": 450000,
  Brazil: 370000,
  "United Kingdom": 84500,
};

const CFR = {
  India: 0.96,
  "United States": 1.74,
  Brazil: 3.04,
  "United Kingdom": 1.91,
};

// Shared animation & style defaults
const ANIMATION = {
  duration: 1400,
  easing: "easeOutQuart",
};

const commonOptions = {
  responsive: true,
  maintainAspectRatio: true,
  animation: ANIMATION,
  plugins: {
    legend: {
      position: "top",
      labels: {
        usePointStyle: true,
        padding: 16,
        font: { family: "Inter, sans-serif", size: 12 },
      },
    },
    tooltip: {
      backgroundColor: "#0F172A",
      titleFont: { family: "Inter, sans-serif", size: 13 },
      bodyFont: { family: "Inter, sans-serif", size: 12 },
      padding: 12,
      cornerRadius: 8,
      displayColors: true,
    },
  },
  scales: {
    x: {
      grid: { color: "rgba(148,163,184,0.15)" },
      ticks: { font: { family: "Inter, sans-serif", size: 11 } },
    },
    y: {
      grid: { color: "rgba(148,163,184,0.15)" },
      ticks: { font: { family: "Inter, sans-serif", size: 11 } },
      beginAtZero: true,
    },
  },
};

function lineDatasets(metric) {
  return Object.keys(DATA[metric]).map((country) => ({
    label: country,
    data: DATA[metric][country],
    borderColor: COLORS[country],
    backgroundColor: COLORS[country] + "22",
    borderWidth: 2.5,
    pointRadius: 5,
    pointHoverRadius: 7,
    pointBackgroundColor: COLORS[country],
    tension: 0.35,
    fill: false,
  }));
}

function createCasesTrend(canvasId) {
  const ctx = document.getElementById(canvasId);
  if (!ctx) return;
  new Chart(ctx, {
    type: "line",
    data: { labels: LABELS, datasets: lineDatasets("cases") },
    options: {
      ...commonOptions,
      plugins: {
        ...commonOptions.plugins,
        title: { display: false },
      },
    },
  });
}

function createVaccination(canvasId) {
  const ctx = document.getElementById(canvasId);
  if (!ctx) return;
  new Chart(ctx, {
    type: "line",
    data: { labels: LABELS, datasets: lineDatasets("vaccinated") },
    options: {
      ...commonOptions,
      scales: {
        ...commonOptions.scales,
        y: {
          ...commonOptions.scales.y,
          max: 70,
          title: { display: true, text: "% vaccinated" },
        },
      },
    },
  });
}

function createDeathsBar(canvasId) {
  const ctx = document.getElementById(canvasId);
  if (!ctx) return;
  const countries = Object.keys(TOTAL_DEATHS);
  new Chart(ctx, {
    type: "bar",
    data: {
      labels: countries,
      datasets: [
        {
          label: "Total Deaths",
          data: countries.map((c) => TOTAL_DEATHS[c]),
          backgroundColor: countries.map((c) => COLORS[c] + "CC"),
          borderColor: countries.map((c) => COLORS[c]),
          borderWidth: 1.5,
          borderRadius: 8,
          borderSkipped: false,
        },
      ],
    },
    options: {
      ...commonOptions,
      plugins: {
        ...commonOptions.plugins,
        legend: { display: false },
      },
      animation: {
        ...ANIMATION,
        delay: (ctx) => ctx.dataIndex * 120,
      },
    },
  });
}

function createLatestCasesBar(canvasId) {
  const ctx = document.getElementById(canvasId);
  if (!ctx) return;
  const countries = Object.keys(LATEST_CASES);
  new Chart(ctx, {
    type: "bar",
    data: {
      labels: countries,
      datasets: [
        {
          label: "Latest Cases (Jun 2021)",
          data: countries.map((c) => LATEST_CASES[c]),
          backgroundColor: countries.map((c) => COLORS[c] + "CC"),
          borderColor: countries.map((c) => COLORS[c]),
          borderWidth: 1.5,
          borderRadius: 8,
          borderSkipped: false,
        },
      ],
    },
    options: {
      ...commonOptions,
      plugins: {
        ...commonOptions.plugins,
        legend: { display: false },
      },
      animation: {
        ...ANIMATION,
        delay: (ctx) => ctx.dataIndex * 120,
      },
    },
  });
}

function createNewCasesTrend(canvasId) {
  const ctx = document.getElementById(canvasId);
  if (!ctx) return;

  // Month-over-month change
  const newCases = {};
  Object.keys(DATA.cases).forEach((country) => {
    const arr = DATA.cases[country];
    newCases[country] = arr.map((v, i) => (i === 0 ? v : v - arr[i - 1]));
  });

  const datasets = Object.keys(newCases).map((country) => ({
    label: country,
    data: newCases[country],
    borderColor: COLORS[country],
    backgroundColor: COLORS[country] + "22",
    borderWidth: 2.5,
    pointRadius: 5,
    pointHoverRadius: 7,
    tension: 0.3,
  }));

  new Chart(ctx, {
    type: "line",
    data: { labels: LABELS, datasets },
    options: {
      ...commonOptions,
      scales: {
        ...commonOptions.scales,
        y: {
          ...commonOptions.scales.y,
          title: { display: true, text: "Change in cases" },
        },
      },
    },
  });
}

function createCFRBar(canvasId) {
  const ctx = document.getElementById(canvasId);
  if (!ctx) return;
  const countries = Object.keys(CFR);
  new Chart(ctx, {
    type: "bar",
    data: {
      labels: countries,
      datasets: [
        {
          label: "Avg CFR (%)",
          data: countries.map((c) => CFR[c]),
          backgroundColor: ["#F59E0BCC", "#EF4444CC", "#0F766ECC", "#6366F1CC"],
          borderColor: ["#F59E0B", "#EF4444", "#0F766E", "#6366F1"],
          borderWidth: 1.5,
          borderRadius: 8,
          borderSkipped: false,
        },
      ],
    },
    options: {
      ...commonOptions,
      plugins: {
        ...commonOptions.plugins,
        legend: { display: false },
      },
      animation: {
        ...ANIMATION,
        delay: (ctx) => ctx.dataIndex * 120,
      },
      scales: {
        ...commonOptions.scales,
        y: {
          ...commonOptions.scales.y,
          title: { display: true, text: "CFR (%)" },
        },
      },
    },
  });
}

function createRanking(canvasId) {
  const ctx = document.getElementById(canvasId);
  if (!ctx) return;
  const sorted = Object.entries(TOTAL_CASES).sort((a, b) => a[1] - b[1]);
  new Chart(ctx, {
    type: "bar",
    data: {
      labels: sorted.map(([c]) => c),
      datasets: [
        {
          label: "Total Cases",
          data: sorted.map(([, v]) => v),
          backgroundColor: sorted.map(([c]) => COLORS[c] + "CC"),
          borderColor: sorted.map(([c]) => COLORS[c]),
          borderWidth: 1.5,
          borderRadius: 8,
          borderSkipped: false,
        },
      ],
    },
    options: {
      indexAxis: "y",
      ...commonOptions,
      plugins: {
        ...commonOptions.plugins,
        legend: { display: false },
      },
      animation: {
        ...ANIMATION,
        delay: (ctx) => ctx.dataIndex * 150,
      },
    },
  });
}

function createDeathsVsCases(canvasId) {
  const ctx = document.getElementById(canvasId);
  if (!ctx) return;

  // Flatten all points
  const datasets = Object.keys(DATA.cases).map((country) => ({
    label: country,
    data: DATA.cases[country].map((c, i) => ({
      x: c,
      y: DATA.deaths[country][i],
    })),
    backgroundColor: COLORS[country],
    borderColor: COLORS[country],
    pointRadius: 7,
    pointHoverRadius: 9,
  }));

  new Chart(ctx, {
    type: "scatter",
    data: { datasets },
    options: {
      ...commonOptions,
      scales: {
        x: {
          ...commonOptions.scales.x,
          title: { display: true, text: "Cases" },
        },
        y: {
          ...commonOptions.scales.y,
          title: { display: true, text: "Deaths" },
        },
      },
    },
  });
}

/* ---------- Init helpers ---------- */
function initHomeCharts() {
  createCasesTrend("chartCasesTrend");
  createVaccination("chartVaccination");
  createDeathsBar("chartDeathsBar");
  createLatestCasesBar("chartLatestCases");
}

function initAnalyticsCharts() {
  createCasesTrend("chartCasesTrend");
  createNewCasesTrend("chartNewCases");
  createVaccination("chartVaccination");
  createDeathsBar("chartDeathsBar");
  createLatestCasesBar("chartLatestCases");
  createCFRBar("chartCFR");
  createDeathsVsCases("chartDeathsVsCases");
  createRanking("chartRanking");
}

// Auto-detect page
document.addEventListener("DOMContentLoaded", () => {
  if (document.body.dataset.page === "home") initHomeCharts();
  if (document.body.dataset.page === "analytics") initAnalyticsCharts();
});
