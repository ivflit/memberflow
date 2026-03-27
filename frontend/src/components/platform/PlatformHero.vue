<template>
  <section class="hero is-fullheight platform-hero">
    <div class="hero-body">
      <div class="container has-text-centered">
        <div data-aos="fade-up">
          <h1 class="title is-1 hero-title">
            Membership management, built for clubs.
          </h1>
          <p class="subtitle is-4 hero-subtitle">
            Stop chasing spreadsheets. MemberFlow handles registration, payments,
            and renewals — so you can focus on your club.
          </p>
          <a
            class="button is-large hero-cta"
            @click.prevent="scrollToContact"
          >
            Get Started
          </a>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
function scrollToContact() {
  const el = document.querySelector('#contact')
  if (el) el.scrollIntoView({ behavior: 'smooth' })
}
</script>

<style scoped>
.platform-hero {
  background: linear-gradient(135deg, var(--mf-navy) 0%, var(--mf-teal) 100%);
}

.hero-title {
  color: #ffffff;
  font-size: 3rem;
  font-weight: 800;
  line-height: 1.15;
  margin-bottom: 1.5rem;
}

.hero-subtitle {
  color: rgba(255, 255, 255, 0.9);
  margin-bottom: 2.5rem;
  max-width: 600px;
  margin-left: auto;
  margin-right: auto;
}

.hero-cta {
  background: #ffffff;
  color: var(--mf-navy);
  font-weight: 700;
  padding: 1rem 2.5rem;
  border-radius: 8px;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
  border: none;
}

.hero-cta:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.2);
  color: var(--mf-navy);
}

@media (max-width: 768px) {
  .hero-title {
    font-size: 2rem;
  }
}
</style>
