/* Interacciones pequeñas: carrusel, imágenes de respaldo y aparición progresiva. */
document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll(".service-carousel").forEach((carousel) => {
    const track = carousel.querySelector("[data-carousel-track]");
    const cards = Array.from(track.querySelectorAll(".service-card"));
    const range = carousel.querySelector("[data-carousel-range]");
    const progress = carousel.querySelector("[data-carousel-progress]");
    const previous = carousel.querySelector("[data-carousel-prev]");
    const next = carousel.querySelector("[data-carousel-next]");
    const toggle = carousel.querySelector("[data-carousel-toggle]");
    const motionPreference = window.matchMedia("(prefers-reduced-motion: reduce)");
    let direction = 1;
    let manualPaused = false;
    let pointerPaused = false;
    let focusPaused = false;
    let autoplayTimer = null;

    if (!cards.length) {
      range.textContent = "0–0";
      previous.disabled = true;
      next.disabled = true;
      toggle.hidden = true;
      return;
    }

    const step = () => cards[0].getBoundingClientRect().width + parseFloat(getComputedStyle(track).gap || 0);
    const visibleCards = () => Math.max(1, Math.ceil(track.clientWidth / step()));
    const maxScroll = () => Math.max(0, track.scrollWidth - track.clientWidth);

    const advance = () => {
      const max = maxScroll();
      if (max <= 2) return;

      if (direction > 0 && track.scrollLeft >= max - 2) direction = -1;
      else if (direction < 0 && track.scrollLeft <= 2) direction = 1;

      const target = Math.max(0, Math.min(max, track.scrollLeft + direction * step()));
      if (target >= max - 2) direction = -1;
      else if (target <= 2) direction = 1;
      track.scrollTo({ left: target, behavior: "smooth" });
    };

    const syncAutoplay = () => {
      const canAutoplay = maxScroll() > 2 && !motionPreference.matches;
      toggle.hidden = !canAutoplay;

      if (!canAutoplay || manualPaused || pointerPaused || focusPaused || document.hidden) {
        window.clearInterval(autoplayTimer);
        autoplayTimer = null;
      } else if (autoplayTimer === null) {
        autoplayTimer = window.setInterval(advance, 3000);
      }
    };

    const update = () => {
      const max = maxScroll();
      const firstIndex = Math.min(cards.length - 1, Math.round(track.scrollLeft / step()));
      const lastIndex = Math.min(cards.length, firstIndex + visibleCards());
      range.textContent = `${firstIndex + 1}–${lastIndex}`;
      progress.style.width = `${max ? (track.scrollLeft / max) * 100 : 100}%`;
      carousel.querySelector(".carousel-progress").setAttribute(
        "aria-valuenow",
        String(Math.round(max ? (track.scrollLeft / max) * 100 : 100))
      );
      previous.disabled = track.scrollLeft <= 2;
      next.disabled = track.scrollLeft >= max - 2;
    };

    previous.addEventListener("click", () => {
      direction = -1;
      track.scrollBy({ left: -step() * visibleCards(), behavior: "smooth" });
    });
    next.addEventListener("click", () => {
      direction = 1;
      track.scrollBy({ left: step() * visibleCards(), behavior: "smooth" });
    });
    toggle.addEventListener("click", () => {
      manualPaused = !manualPaused;
      toggle.textContent = manualPaused ? "▶" : "Ⅱ";
      const label = manualPaused ? "Reanudar movimiento automático" : "Pausar movimiento automático";
      toggle.setAttribute("aria-label", label);
      toggle.title = label;
      syncAutoplay();
    });
    track.addEventListener("scroll", update, { passive: true });
    track.addEventListener("keydown", (event) => {
      if (event.key === "ArrowRight") {
        event.preventDefault();
        direction = 1;
        track.scrollBy({ left: step(), behavior: "smooth" });
      } else if (event.key === "ArrowLeft") {
        event.preventDefault();
        direction = -1;
        track.scrollBy({ left: -step(), behavior: "smooth" });
      }
    });
    carousel.addEventListener("mouseenter", () => {
      pointerPaused = true;
      syncAutoplay();
    });
    carousel.addEventListener("mouseleave", () => {
      pointerPaused = false;
      syncAutoplay();
    });
    carousel.addEventListener("focusin", () => {
      focusPaused = true;
      syncAutoplay();
    });
    carousel.addEventListener("focusout", () => {
      window.setTimeout(() => {
        focusPaused = carousel.contains(document.activeElement);
        syncAutoplay();
      }, 0);
    });
    motionPreference.addEventListener("change", syncAutoplay);
    document.addEventListener("visibilitychange", syncAutoplay);
    window.addEventListener("resize", () => {
      update();
      syncAutoplay();
    });
    update();
    syncAutoplay();
  });

  document.querySelectorAll("img").forEach((image) => {
    const showFallback = () => {
      image.classList.add("image-unavailable");
      const fallback = image.parentElement.querySelector(".image-fallback");
      if (fallback) fallback.classList.add("is-visible");
    };
    image.addEventListener("error", showFallback);
    if (image.complete && image.naturalWidth === 0) showFallback();
  });

  const revealItems = document.querySelectorAll(".reveal");
  if ("IntersectionObserver" in window && !window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
    const observer = new IntersectionObserver((entries, currentObserver) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add("is-visible");
          currentObserver.unobserve(entry.target);
        }
      });
    }, { threshold: 0.12 });
    revealItems.forEach((item) => observer.observe(item));
  } else {
    revealItems.forEach((item) => item.classList.add("is-visible"));
  }

  const bookingForm = document.querySelector("#booking-form");
  if (bookingForm) {
    const serviceSelect = document.querySelector("#service");
    const dateInput = document.querySelector("#booking-date");
    const refreshButton = document.querySelector("#booking-refresh");
    const status = document.querySelector("#booking-status");
    const slotsContainer = document.querySelector("#booking-slots");
    const timeInput = document.querySelector("#booking-time");
    const confirmButton = document.querySelector("#booking-confirm");
    const today = new Date();
    const formatDate = (value) => {
      const year = value.getFullYear();
      const month = String(value.getMonth() + 1).padStart(2, "0");
      const day = String(value.getDate()).padStart(2, "0");
      return `${year}-${month}-${day}`;
    };
    const tomorrow = new Date(today);
    tomorrow.setDate(today.getDate() + 1);
    const maximum = new Date("2026-12-20T12:00:00");
    dateInput.min = formatDate(tomorrow);
    dateInput.max = formatDate(maximum);
    if (!dateInput.value) dateInput.value = formatDate(tomorrow);

    const loadAvailability = async () => {
      if (!serviceSelect.value || !dateInput.value) {
        status.textContent = "Selecciona un servicio y una fecha.";
        slotsContainer.innerHTML = "";
        timeInput.value = "";
        confirmButton.hidden = true;
        return;
      }

      status.textContent = "Consultando horarios...";
      slotsContainer.innerHTML = "";
      timeInput.value = "";
      try {
        const params = new URLSearchParams({
          date: dateInput.value,
          service: serviceSelect.value,
        });
        const response = await fetch(`/api/reservas-disponibilidad/?${params}`);
        const data = await response.json();
        if (!response.ok) throw new Error(data.error || "No se pudo cargar la disponibilidad.");

        if (!data.slots.length) {
          status.textContent = "El taller está cerrado esta fecha.";
          return;
        }

        const availableCount = data.slots.filter((slot) => slot.available).length;
        status.textContent = `${availableCount} horario${availableCount === 1 ? "" : "s"} disponible${availableCount === 1 ? "" : "s"} · Duración estimada: ${data.duration_minutes / 60} h`;
        data.slots.forEach((slot) => {
          const button = document.createElement("button");
          button.type = "button";
          button.className = `booking-slot ${slot.available ? "is-available" : "is-occupied"}`;
          button.textContent = slot.time;
          button.disabled = !slot.available;
          button.setAttribute("aria-label", slot.available ? `Reservar a las ${slot.time}` : `${slot.time}, ocupado`);
          if (slot.available) {
            button.addEventListener("click", () => {
              slotsContainer.querySelectorAll(".booking-slot").forEach((item) => item.classList.remove("is-selected"));
              button.classList.add("is-selected");
              timeInput.value = slot.time;
              status.textContent = `Horario seleccionado: ${slot.time}`;
              confirmButton.hidden = false;
            });
          }
          slotsContainer.appendChild(button);
        });
      } catch (error) {
        status.textContent = error.message;
      }
    };

    serviceSelect.addEventListener("change", loadAvailability);
    dateInput.addEventListener("change", loadAvailability);
    refreshButton.addEventListener("click", loadAvailability);
    confirmButton.addEventListener("click", async () => {
      const nameInput = document.querySelector("#name");
      const emailInput = document.querySelector("#email");
      if (!nameInput.value.trim() || !emailInput.value.trim()) {
        status.textContent = "Completa nombre y correo antes de confirmar la reserva.";
        (nameInput.value.trim() ? emailInput : nameInput).focus();
        return;
      }

      const formData = new URLSearchParams({
        date: dateInput.value,
        time: timeInput.value,
        service: serviceSelect.value,
        name: nameInput.value,
        email: emailInput.value,
      });
      confirmButton.disabled = true;
      status.textContent = "Confirmando reserva...";
      try {
        const csrfToken = document.querySelector("[name=csrfmiddlewaretoken]").value;
        const response = await fetch("/api/reservas-confirmar/", {
          method: "POST",
          headers: {
            "Content-Type": "application/x-www-form-urlencoded",
            "X-CSRFToken": csrfToken,
          },
          body: formData,
        });
        const data = await response.json();
        if (!response.ok) throw new Error(data.error || "No se pudo confirmar la reserva.");
        confirmButton.hidden = true;
        await loadAvailability();
        status.textContent = `Reserva confirmada: ${data.date} a las ${data.time} — ${data.service}`;
        document.querySelector("#receipt-code").textContent = data.code;
        document.querySelector("#receipt-name").textContent = nameInput.value.trim();
        document.querySelector("#receipt-service").textContent = data.service;
        document.querySelector("#receipt-date").textContent = data.date;
        document.querySelector("#receipt-time").textContent = data.time;
        document.querySelector("#booking-receipt-modal").hidden = false;
      } catch (error) {
        status.textContent = error.message;
      } finally {
        confirmButton.disabled = false;
      }
    });
    bookingForm.addEventListener("submit", (event) => {
      if (!timeInput.value) {
        event.preventDefault();
        status.textContent = "Debes seleccionar un horario disponible.";
        document.querySelector("#booking-slots").scrollIntoView({ behavior: "smooth", block: "center" });
      }
    });
    document.querySelector("#receipt-close").addEventListener("click", () => {
      document.querySelector("#booking-receipt-modal").hidden = true;
    });
    document.querySelector("#receipt-print").addEventListener("click", () => window.print());
    document.querySelector("#booking-receipt-modal").addEventListener("click", (event) => {
      if (event.target.id === "booking-receipt-modal") {
        event.currentTarget.hidden = true;
      }
    });
    document.addEventListener("keydown", (event) => {
      if (event.key === "Escape") {
        document.querySelector("#booking-receipt-modal").hidden = true;
      }
    });
    loadAvailability();
  }
});
