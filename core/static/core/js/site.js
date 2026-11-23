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
});
