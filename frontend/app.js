let API_BASE = "https://stockdash-backend.onrender.com/";
const companiesEl = document.getElementById("companyList");
const high52El = document.getElementById("high52");
const low52El  = document.getElementById("low52");
const avgVolEl = document.getElementById("avgVol");
const predEl   = document.getElementById("pred");

const priceCtx = document.getElementById("priceChart").getContext("2d");
const rsiCtx   = document.getElementById("rsiChart").getContext("2d");
let priceChart, rsiChart;

document.getElementById("applyBase").addEventListener("click", () => {
  const val = document.getElementById("apiBase").value.trim();
  if (val) API_BASE = val;
  loadCompanies();
});

async function loadCompanies() {
  companiesEl.innerHTML = "Loading...";
  try {
    const res = await fetch(`${API_BASE}/api/companies`);
    const data = await res.json();
    companiesEl.innerHTML = "";

    data.forEach((c, idx) => {
      const div = document.createElement("div");
      div.className = "item" + (idx === 0 ? " active" : "");
      div.textContent = `${c.name} (${c.symbol})`;
      div.dataset.symbol = c.symbol;
      div.onclick = () => selectCompany(div, c.symbol);
      companiesEl.appendChild(div);
    });

    if (data.length) {
      await fetchAndRender(data[0].symbol);
    }
  } catch (e) {
    companiesEl.innerHTML = "Failed to load companies.";
  }
}

function selectCompany(el, symbol) {
  [...companiesEl.querySelectorAll(".item")].forEach(x => x.classList.remove("active"));
  el.classList.add("active");
  fetchAndRender(symbol);
}

async function fetchAndRender(symbol) {
  try {
    const [histRes, predRes] = await Promise.all([
      fetch(`${API_BASE}/api/history?symbol=${encodeURIComponent(symbol)}&period=1y&interval=1d`),
      fetch(`${API_BASE}/api/predict/next?symbol=${encodeURIComponent(symbol)}&period=6mo&interval=1d`)
    ]);
    const hist = await histRes.json();
    const pred = predRes.ok ? await predRes.json() : { next_close_prediction: null };

    // Metrics
    high52El.textContent = numberFmt(hist.metrics.high_52w);
    low52El.textContent  = numberFmt(hist.metrics.low_52w);
    avgVolEl.textContent = intFmt(hist.metrics.avg_volume);
    predEl.textContent   = pred.next_close_prediction ? numberFmt(pred.next_close_prediction) : "—";

    // Series
    const labels = hist.candles.map(c => c.date);
    const close  = hist.candles.map(c => c.close);
    const sma20  = hist.candles.map(c => c.sma20);
    const sma50  = hist.candles.map(c => c.sma50);
    const rsi14  = hist.candles.map(c => c.rsi14);

    // Price chart
    if (priceChart) priceChart.destroy();
    priceChart = new Chart(priceCtx, {
      type: "line",
      data: {
        labels,
        datasets: [
          { label: "Close", data: close, borderWidth: 2, pointRadius: 0 },
          { label: "SMA 20", data: sma20, borderWidth: 1, pointRadius: 0 },
          { label: "SMA 50", data: sma50, borderWidth: 1, pointRadius: 0 }
        ]
      },
      options: {
        responsive: true,
        interaction: { mode: "index", intersect: false },
        scales: { x: { display: true }, y: { display: true } },
        plugins: { legend: { display: true } }
      }
    });

    // RSI chart
    if (rsiChart) rsiChart.destroy();
    rsiChart = new Chart(rsiCtx, {
      type: "line",
      data: { labels, datasets: [{ label: "RSI 14", data: rsi14, borderWidth: 2, pointRadius: 0 }] },
      options: {
        responsive: true,
        scales: {
          y: { min: 0, max: 100 }
        },
        plugins: { legend: { display: true } }
      }
    });
  } catch (e) {
    console.error(e);
    alert("Failed to load data for " + symbol);
  }
}

function numberFmt(n) {
  return n?.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}
function intFmt(n) {
  return n?.toLocaleString();
}

// boot
loadCompanies();
