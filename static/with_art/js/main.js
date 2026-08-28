(function () {
  // ============================================================
  // Custom cursor
  // ============================================================
  var dot = document.getElementById("cursor-dot");

  if (!dot) {
    console.error("[cursor] #cursor-dot not found in DOM — cursor will not work.");
  } else {
    // Use passive listener for performance (60fps mousemove is expensive)
    document.addEventListener(
      "mousemove",
      function (e) {
        dot.style.left = e.clientX + "px";
        dot.style.top = e.clientY + "px";
      },
      { passive: true }
    );

    // Grow when hovering over interactive elements
    var interactives = 'a, button, input, textarea, select, [role="button"]';
    document.addEventListener("mouseover", function (e) {
      if (e.target.closest && e.target.closest(interactives)) {
        dot.classList.add("hovering");
      }
    });
    document.addEventListener("mouseout", function (e) {
      if (e.target.closest && e.target.closest(interactives)) {
        dot.classList.remove("hovering");
      }
    });
  }

  // ============================================================
  // Carousel
  // Stops at the first/last slide and hides the matching arrow.
  // ============================================================
  var carousels = document.querySelectorAll("[data-carousel]");

  carousels.forEach(function (carousel) {
    var track = carousel.querySelector("[data-carousel-track]");
    var prev = carousel.querySelector("[data-carousel-prev]");
    var next = carousel.querySelector("[data-carousel-next]");
    var cur = carousel.querySelector("[data-carousel-current]");
    var slides = track ? track.children : [];
    var index = 0;

    function getSlideWidth() {
      if (!track || slides.length === 0) return 0;
      return track.clientWidth;
    }

    function updateCounter(value) {
      if (cur) cur.textContent = value;
    }

    // Show/hide prev + next depending on the current slide.
    //   first slide  -> left arrow hidden + disabled
    //   last slide   -> right arrow hidden + disabled
    //   single image -> both arrows hidden + disabled
    function updateNavState() {
      var isFirst = index <= 0;
      var isLast  = index >= slides.length - 1;

      function apply(btn, disabled) {
        if (!btn) return;
        btn.classList.toggle("is-disabled", disabled);
        btn.disabled = disabled;
        if (disabled) btn.setAttribute("aria-disabled", "true");
        else          btn.removeAttribute("aria-disabled");
      }

      apply(next, isLast);
      apply(prev, isFirst);

      if (slides.length <= 1) {
        apply(next, true);
        apply(prev, true);
      }
    }

    function goTo(i) {
      if (slides.length === 0) return;
      if (i < 0) i = 0;                                  // clamp at start
      if (i >= slides.length) i = slides.length - 1;     // clamp at end
      index = i;
      var w = getSlideWidth();
      if (w > 0) {
        track.scrollTo({ left: i * w, behavior: "smooth" });
      }
      updateCounter(i + 1);
      updateNavState();
    }

    if (prev) {
      prev.addEventListener("click", function () {
        if (index <= 0) return;
        goTo(index - 1);
      });
    }

    if (next) {
      next.addEventListener("click", function () {
        if (index >= slides.length - 1) return;
        goTo(index + 1);
      });
    }

    carousel.addEventListener("keydown", function (e) {
      if (e.key === "ArrowLeft"  && index > 0)                 goTo(index - 1);
      if (e.key === "ArrowRight" && index < slides.length - 1) goTo(index + 1);
    });

    if (track) {
      var debounceTimer = null;
      track.addEventListener("scroll", function () {
        if (debounceTimer) clearTimeout(debounceTimer);
        debounceTimer = setTimeout(function () {
          var w = track.clientWidth;
          if (w > 0) {
            var i = Math.round(track.scrollLeft / w);
            if (i !== index) {
              index = i;
              updateCounter(i + 1);
              updateNavState();
            }
          }
        }, 100);
      });
    }

    // Initial state so first paint already shows correct arrows
    updateNavState();
  });
})();
