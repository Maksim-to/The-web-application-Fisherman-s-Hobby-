(() => {
  const $ = (sel, root = document) => root.querySelector(sel);
  const $$ = (sel, root = document) => Array.from(root.querySelectorAll(sel));

  function debounce(fn, ms) {
    let t;
    return (...args) => {
      clearTimeout(t);
      t = setTimeout(() => fn(...args), ms);
    };
  }

  async function apiGet(url) {
    const res = await fetch(url, { headers: { "Accept": "application/json" } });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  }

  async function apiPost(url, payload = null) {
    const res = await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json", "Accept": "application/json" },
      body: payload ? JSON.stringify(payload) : "{}",
      credentials: "same-origin",
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  }

  // ============ Карточка водоёма: избранное + прогноз ============
  async function initWaterbody() {
    const wbId = document.body.getAttribute("data-waterbody-id");
    if (!wbId) return;
    const favBtn = $("#favBtn");
    const forecastBox = $("#forecastBox");

    async function updateFavState() {
      if (!favBtn) return;
      try {
        const st = await apiGet(`/api/favorites/status/${wbId}`);
        favBtn.classList.toggle("is-active", !!st.is_favorite);
        favBtn.textContent = st.is_favorite ? "В ИЗБРАННОМ" : "В ИЗБРАННОЕ";
      } catch (e) {}
    }

    if (favBtn) {
      favBtn.addEventListener("click", async () => {
        try {
          await apiPost(`/api/favorites/toggle/${wbId}`);
          await updateFavState();
        } catch (e) {}
      });
      updateFavState().catch(() => {});
    }

    if (forecastBox) {
      try {
        const data = await apiGet(`/api/waterbodies/${wbId}/forecast`);
        forecastBox.innerHTML = data.html || "<div style='color:var(--text-muted);'>Данные прогноза недоступны.</div>";
      } catch (e) {
        forecastBox.innerHTML = "<div style='color:var(--text-muted);'>Данные прогноза недоступны.</div>";
      }
    }
  }

  // ============ Копирование ссылки ============
  window.copyToClipboard = function(text) {
    if (navigator.clipboard) {
      navigator.clipboard.writeText(text).then(() => alert('Ссылка скопирована!'));
    } else {
      const ta = document.createElement('textarea');
      ta.value = text;
      ta.style.position = 'fixed';
      ta.style.opacity = '0';
      document.body.appendChild(ta);
      ta.select();
      document.execCommand('copy');
      document.body.removeChild(ta);
      alert('Ссылка скопирована!');
    }
  };

  document.addEventListener("DOMContentLoaded", () => {
    initWaterbody().catch(() => {});
  });
})();