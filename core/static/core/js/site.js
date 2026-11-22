/* Interacciones pequeñas: carrusel, imágenes de respaldo y aparición progresiva. */
document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll(".service-carousel").forEach((carousel) => {
    const track = carousel.querySelector("[data-carousel-track]");
    const cards = Array.from(track.querySelectorAll(".service-card"));
    const range = carousel.querySelector("[data-carousel-range]");
    const progress = carousel.querySelector("[data-carousel-progress]");
    const previous = carousel.querySelector("[data-carousel-prev]");
    const next = carousel.querySelector("[data-carousel-next]");

    if (!cards.length) {
      range.textContent = "0–0";
      previous.disabled = true;
      next.disabled = true;
      return;
    }

    const step = () => cards[0].getBoundingClientRect().width + parseFloat(getComputedStyle(track).gap || 0);
    const visibleCards = () => Math.max(1, Math.ceil(track.clientWidth / step()));

    const update = () => {
      const maxScroll = Math.max(0, track.scrollWidth - track.clientWidth);
      const firstIndex = Math.min(cards.length - 1, Math.round(track.scrollLeft / step()));
      const lastIndex = Math.min(cards.length, firstIndex + visibleCards());
      range.textContent = `${firstIndex + 1}–${lastIndex}`;
      progress.style.width = `${maxScroll ? (track.scrollLeft / maxScroll) * 100 : 100}%`;
      carousel.querySelector(".carousel-progress").setAttribute(
        "aria-valuenow",
        String(Math.round(maxScroll ? (track.scrollLeft / maxScroll) * 100 : 100))
      );
      previous.disabled = track.scrollLeft <= 2;
      next.disabled = track.scrollLeft >= maxScroll - 2;
    };

    previous.addEventListener("click", () => track.scrollBy({ left: -step() * visibleCards(), behavior: "smooth" }));
    next.addEventListener("click", () => track.scrollBy({ left: step() * visibleCards(), behavior: "smooth" }));
    track.addEventListener("scroll", update, { passive: true });
    track.addEventListener("keydown", (event) => {
      if (event.key === "ArrowRight") {
        event.preventDefault();
        track.scrollBy({ left: step(), behavior: "smooth" });
      } else if (event.key === "ArrowLeft") {
        event.preventDefault();
        track.scrollBy({ left: -step(), behavior: "smooth" });
      }
    });
    window.addEventListener("resize", update);
    update();
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
