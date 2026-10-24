const $ = (id) => document.getElementById(id);
const toast = (message) => {
  const el = $("toast");
  el.textContent = message;
  el.classList.add("show");
  clearTimeout(window.__toastTimer);
  window.__toastTimer = setTimeout(() => el.classList.remove("show"), 2800);
};
async function request(path, options = {}) {
  const response = await fetch(path, { ...options, headers: { "Content-Type": "application/json", ...(options.headers || {}) } });
  if (!response.ok) throw new Error(`${response.status} ${response.statusText}`);
  return response.json();
}
function renderFleet(vehicles) {
  $("vehicleCount").textContent = vehicles.length;
  $("fleetLabel").textContent = `${vehicles.length} vehicles`;
  $("fleetBody").innerHTML = vehicles.map(v => `
    <tr>
      <td>${escapeHtml(v.vehicle_id)}</td>
      <td>${Number(v.altitude_m)} m</td>
      <td>${Number(v.speed_mps)} m/s</td>
      <td><div class="battery"><span>${Number(v.battery_pct)}%</span><span class="battery-track"><span class="battery-fill" style="display:block;width:${Math.max(0,Math.min(100,Number(v.battery_pct)))}%"></span></span></div></td>
      <td><span class="badge">${escapeHtml(v.status)}</span></td>
    </tr>`).join("");
}
function renderIncidents(items) {
  $("incidentCount").textContent = items.length;
  if (!items.length) {
    $("incidentList").innerHTML = '<div class="empty">No events recorded yet. Simulate an event to test persistence.</div>';
    return;
  }
  $("incidentList").innerHTML = items.map(item => `
    <div class="incident"><div class="incident-icon">!</div><div>
      <strong>${escapeHtml(item.kind)} · ${escapeHtml(item.severity)}</strong>
      <p>${escapeHtml(item.message)}</p>
      <time>${item.created_at ? new Date(item.created_at).toLocaleString() : "Time unavailable"}</time>
    </div></div>`).join("");
}
function escapeHtml(value) {
  return String(value ?? "").replace(/[&<>"']/g, c => ({ "&":"&amp;", "<":"&lt;", ">":"&gt;", '"':"&quot;", "'":"&#39;" }[c]));
}
async function refresh() {
  $("apiStatus").textContent = "Checking";
  $("apiMessage").textContent = "Connecting to service";

  // Check the API and fleet independently from database-backed incident history.
  // A missing DATABASE_URL should not make the whole dashboard appear offline.
  const healthResult = await request("/health").then(
    value => ({ ok: true, value }),
    error => ({ ok: false, error })
  );
  const fleetResult = await request("/api/fleet").then(
    value => ({ ok: true, value }),
    error => ({ ok: false, error })
  );
  const incidentsResult = await request("/api/incidents").then(
    value => ({ ok: true, value }),
    error => ({ ok: false, error })
  );

  if (healthResult.ok) {
    $("apiStatus").textContent = healthResult.value.status === "ok" ? "Online" : "Issue";
    $("apiMessage").textContent = "FastAPI service reachable";
  } else {
    $("apiStatus").textContent = "Offline";
    $("apiMessage").textContent = `Health check failed: ${healthResult.error.message}`;
  }

  if (fleetResult.ok && Array.isArray(fleetResult.value)) {
    renderFleet(fleetResult.value);
  } else {
    $("fleetBody").innerHTML = `<tr><td colspan="5" class="empty">Could not load fleet data: ${escapeHtml(fleetResult.error?.message || "Unexpected API response")}</td></tr>`;
  }

  if (incidentsResult.ok && Array.isArray(incidentsResult.value)) {
    renderIncidents(incidentsResult.value);
  } else {
    $("incidentList").innerHTML = `<div class="empty">Incident history is unavailable (${escapeHtml(incidentsResult.error?.message || "Unexpected API response")}). Configure DATABASE_URL with a hosted PostgreSQL database to enable saved events.</div>`;
  }
}
$("refreshBtn").addEventListener("click", refresh);
$("simulateBtn").addEventListener("click", async () => {
  const button = $("simulateBtn");
  button.disabled = true;
  try {
    const result = await request("/api/simulate/tick", { method: "POST" });
    toast(result.message || "Simulation event recorded");
    await refresh();
  } catch (error) {
    toast(`Could not record event: ${error.message}`);
  } finally {
    button.disabled = false;
  }
});
refresh();
