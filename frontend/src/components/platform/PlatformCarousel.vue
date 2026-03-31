<template>
  <section class="section carousel-section">
    <div class="container">
      <p
        class="carousel-heading has-text-centered"
        data-aos="fade-up"
      >
        Trusted by clubs &amp; organisations
      </p>
    </div>

    <div
      class="marquee-wrapper"
      aria-hidden="true"
    >
      <div class="marquee">
        <div class="logo-track">
          <span
            v-for="logo in logos"
            :key="logo.name"
            class="logo-item"
          >
            <svg
              :viewBox="`0 0 120 60`"
              width="120"
              height="60"
              xmlns="http://www.w3.org/2000/svg"
              role="img"
              :aria-label="logo.name"
            >
              <rect
                width="120"
                height="60"
                rx="8"
                fill="#edf2f7"
              />
              <text
                x="60"
                y="36"
                text-anchor="middle"
                font-family="system-ui, sans-serif"
                font-size="13"
                font-weight="600"
                fill="#94a3b8"
              >{{ logo.name }}</text>
            </svg>
          </span>
          <!-- Duplicate set for seamless loop -->
          <span
            v-for="logo in logos"
            :key="`dup-${logo.name}`"
            class="logo-item"
          >
            <svg
              :viewBox="`0 0 120 60`"
              width="120"
              height="60"
              xmlns="http://www.w3.org/2000/svg"
              aria-hidden="true"
            >
              <rect
                width="120"
                height="60"
                rx="8"
                fill="#edf2f7"
              />
              <text
                x="60"
                y="36"
                text-anchor="middle"
                font-family="system-ui, sans-serif"
                font-size="13"
                font-weight="600"
                fill="#94a3b8"
              >{{ logo.name }}</text>
            </svg>
          </span>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
const logos = [
  { name: 'City FC' },
  { name: 'Riverside CC' },
  { name: 'Valley RFC' },
  { name: 'Harrow HC' },
  { name: 'Eastside SC' },
  { name: 'Lakeside AC' },
  { name: 'Northern TC' },
  { name: 'Westbrook BC' },
]
</script>

