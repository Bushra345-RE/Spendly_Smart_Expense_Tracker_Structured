const modal = document.getElementById("expenseModal");
function openModal(){ if(modal) modal.classList.add("show"); }
function closeModal(){ if(modal) modal.classList.remove("show"); }
if(modal) modal.addEventListener("click", e => { if(e.target === modal) closeModal(); });
document.addEventListener("keydown", e => { if(e.key === "Escape") closeModal(); });

const chart = document.getElementById("categoryChart");
if(chart) {
  fetch("/api/summary").then(r => r.json()).then(data => {
    if (!data.labels.length) return;
    new Chart(chart, {
      type: "doughnut",
      data: { labels: data.labels, datasets: [{ data: data.values, borderWidth: 0 }] },
      options: {
        responsive: true, maintainAspectRatio: false,
        cutout: "72%",
        plugins: { legend: { position: "bottom", labels: { usePointStyle: true, padding: 18, font: { family: "DM Sans" } } } }
      }
    });
  });
}
setTimeout(() => document.querySelectorAll(".flash").forEach(x => x.remove()), 4000);
