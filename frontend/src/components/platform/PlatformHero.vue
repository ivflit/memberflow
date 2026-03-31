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

