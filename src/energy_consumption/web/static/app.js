const fields = [
  {name: "speed_kmh", label: "평균 속도", unit: "km/h", min: 20, max: 130, step: 1, value: 70},
  {name: "payload_kg", label: "적재량", unit: "kg", min: 0, max: 500, step: 1, value: 180},
  {name: "ambient_temp_C", label: "외기 온도", unit: "°C", min: -10, max: 40, step: 0.1, value: 20},
  {name: "hvac_power_kw", label: "공조 전력", unit: "kW", min: 0, max: 5, step: 0.1, value: 1.5},
  {name: "road_grade_pct", label: "도로 경사도", unit: "%", min: -5, max: 8, step: 0.1, value: 0},
  {name: "battery_temp_C", label: "배터리 온도", unit: "°C", min: 15, max: 45, step: 0.1, value: 25},
  {name: "driving_style_index", label: "운전 성향 지수", unit: "0–1", min: 0, max: 1, step: 0.01, value: 0.5},
  {name: "tire_pressure_bar", label: "타이어 공기압", unit: "bar", min: 2, max: 2.8, step: 0.01, value: 2.4},
  {name: "trip_distance_km", label: "주행 거리", unit: "km", min: 5.1, max: 200, step: 0.1, value: 50},
];

function renderFields(container, overrides = {}) {
  container.innerHTML = fields.map(field => {
    const value = overrides[field.name] ?? field.value;
    return `<label class="field"><span>${field.label}<small>${field.unit}</small></span>
      <input name="${field.name}" type="number" step="any" value="${value}" required>
      <em>학습 관측 범위 ${field.min} – ${field.max}</em></label>`;
  }).join("");
}

renderFields(document.querySelector("#prediction-form"));
renderFields(document.querySelector("#current-form"));
renderFields(document.querySelector("#alternative-form"), {speed_kmh: 60, payload_kg: 120, hvac_power_kw: 1, driving_style_index: 0.35});

document.querySelectorAll(".tab").forEach(button => button.addEventListener("click", () => {
  document.querySelectorAll(".tab, .panel").forEach(item => item.classList.remove("active"));
  button.classList.add("active");
  document.querySelector(`#${button.dataset.tab}`).classList.add("active");
}));

function values(container) {
  return Object.fromEntries([...container.querySelectorAll("input")].map(input => [input.name, Number(input.value)]));
}

function showError(element, detail) {
  const messages = Array.isArray(detail)
    ? detail.map(item => `${item.loc.at(-1)}: ${item.msg}`).join(" · ")
    : detail;
  element.textContent = `입력값을 확인해주세요. ${messages}`;
  element.hidden = false;
}

function showWarnings(element, warnings, prefix = "") {
  element.hidden = warnings.length === 0;
  element.innerHTML = warnings.length
    ? `<strong>학습 범위 밖 입력 경고</strong><ul>${warnings.map(message => `<li>${prefix}${message}</li>`).join("")}</ul>`
    : "";
}

async function post(url, payload, errorElement) {
  errorElement.hidden = true;
  const response = await fetch(url, {method: "POST", headers: {"Content-Type": "application/json"}, body: JSON.stringify(payload)});
  const body = await response.json();
  if (!response.ok) { showError(errorElement, body.detail || "요청을 처리하지 못했습니다."); throw new Error("validation"); }
  return body;
}

document.querySelector("#prediction-form").addEventListener("submit", async event => {
  event.preventDefault();
  if (!event.currentTarget.reportValidity()) return;
  try {
    const result = await post("/api/predict", values(event.currentTarget), document.querySelector("#prediction-error"));
    document.querySelector("#prediction-consumption").textContent = result.consumption_kwh_per_100km.toFixed(2);
    document.querySelector("#prediction-total").textContent = result.total_energy_kwh.toFixed(2);
    document.querySelector("#prediction-result").hidden = false;
    showWarnings(document.querySelector("#prediction-warning"), result.warnings);
  } catch (error) { if (error.message !== "validation") showError(document.querySelector("#prediction-error"), "서버 연결을 확인해주세요."); }
});

document.querySelector("#simulation-form").addEventListener("submit", async event => {
  event.preventDefault();
  if (!event.currentTarget.reportValidity()) return;
  try {
    const result = await post("/api/simulate", {
      current: values(document.querySelector("#current-form")),
      alternative: values(document.querySelector("#alternative-form")),
    }, document.querySelector("#simulation-error"));
    document.querySelector("#current-consumption").textContent = result.current.consumption_kwh_per_100km.toFixed(2);
    document.querySelector("#current-total").textContent = result.current.total_energy_kwh.toFixed(2);
    document.querySelector("#alternative-consumption").textContent = result.alternative.consumption_kwh_per_100km.toFixed(2);
    document.querySelector("#alternative-total").textContent = result.alternative.total_energy_kwh.toFixed(2);
    document.querySelector("#difference").textContent = `${result.consumption_difference_kwh_per_100km >= 0 ? "+" : ""}${result.consumption_difference_kwh_per_100km.toFixed(2)}`;
    document.querySelector("#savings").textContent = result.savings_rate_pct === null ? "해당 없음" : `${result.savings_rate_pct.toFixed(2)}%`;
    document.querySelector("#simulation-message").textContent = result.message;
    document.querySelector("#simulation-result").hidden = false;
    const warnings = [
      ...result.current.warnings.map(message => `현재 계획: ${message}`),
      ...result.alternative.warnings.map(message => `대안 계획: ${message}`),
    ];
    showWarnings(document.querySelector("#simulation-warning"), warnings);
  } catch (error) { if (error.message !== "validation") showError(document.querySelector("#simulation-error"), "서버 연결을 확인해주세요."); }
});
