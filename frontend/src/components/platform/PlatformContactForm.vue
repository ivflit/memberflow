<template>
  <section
    id="contact"
    class="section contact-section"
  >
    <div class="container">
      <div class="columns is-centered">
        <div class="column is-8-tablet is-6-desktop">
          <div
            class="has-text-centered mb-6"
            data-aos="fade-up"
          >
            <h2 class="title is-2 contact-heading">
              Get in touch
            </h2>
            <p class="subtitle is-5 contact-subheading">
              Ready to simplify your club's membership? We'd love to hear from you.
            </p>
          </div>

          <div
            data-aos="fade-up"
            data-aos-delay="100"
          >
            <!-- Success state -->
            <div
              v-if="submitted"
              class="success-message"
              role="alert"
            >
              <CheckCircleIcon class="success-icon" />
              <p class="success-text">
                Thanks! We'll be in touch soon.
              </p>
            </div>

            <!-- Rate limit banner -->
            <div
              v-if="rateLimited"
              class="notification is-warning rate-limit-banner"
              role="alert"
            >
              <button
                class="delete"
                aria-label="Dismiss"
                @click="rateLimited = false"
              />
              Too many requests. Please try again later.
            </div>

            <!-- Form -->
            <form
              v-if="!submitted"
              novalidate
              @submit.prevent="handleSubmit"
            >
              <!-- Honeypot -->
              <input
                v-model="form.website"
                type="text"
                name="website"
                tabindex="-1"
                autocomplete="off"
                class="honeypot-field"
                aria-hidden="true"
              >

              <div class="field">
                <label
                  class="label contact-label"
                  for="contact-name"
                >Name</label>
                <div class="control">
                  <input
                    id="contact-name"
                    v-model="form.name"
                    class="input"
                    :class="{ 'is-danger': errors.name }"
                    type="text"
                    placeholder="Your full name"
                    autocomplete="name"
                  >
                </div>
                <p
                  v-if="errors.name"
                  class="help is-danger"
                >
                  {{ errors.name }}
                </p>
              </div>

              <div class="field">
                <label
                  class="label contact-label"
                  for="contact-email"
                >Email</label>
                <div class="control">
                  <input
                    id="contact-email"
                    v-model="form.email"
                    class="input"
                    :class="{ 'is-danger': errors.email }"
                    type="email"
                    placeholder="you@yourclub.com"
                    autocomplete="email"
                  >
                </div>
                <p
                  v-if="errors.email"
                  class="help is-danger"
                >
                  {{ errors.email }}
                </p>
              </div>

              <div class="field">
                <label
                  class="label contact-label"
                  for="contact-message"
                >Message</label>
                <div class="control">
                  <textarea
                    id="contact-message"
                    v-model="form.message"
                    class="textarea"
                    :class="{ 'is-danger': errors.message }"
                    placeholder="Tell us about your club and what you need..."
                    rows="5"
                  />
                </div>
                <p
                  v-if="errors.message"
                  class="help is-danger"
                >
                  {{ errors.message }}
                </p>
              </div>

              <div class="field mt-5">
                <div class="control">
                  <button
                    type="submit"
                    class="button is-fullwidth contact-submit-btn"
                    :class="{ 'is-loading': submitting }"
                    :disabled="submitting"
                  >
                    Send Message
                  </button>
                </div>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { CheckCircleIcon } from '@heroicons/vue/24/outline'
import { submitContactForm } from '../../api/contact.js'

const form = reactive({ name: '', email: '', message: '', website: '' })
const errors = reactive({ name: '', email: '', message: '' })
const submitting = ref(false)
const submitted = ref(false)
const rateLimited = ref(false)

function clearErrors() {
  errors.name = ''
  errors.email = ''
  errors.message = ''
}

async function handleSubmit() {
  clearErrors()
  submitting.value = true
  rateLimited.value = false

  try {
    await submitContactForm({
      name: form.name,
      email: form.email,
      message: form.message,
      website: form.website,
    })
    submitted.value = true
  } catch (err) {
    if (err.response?.status === 429) {
      rateLimited.value = true
    } else if (err.response?.status === 400) {
      const data = err.response.data
      if (data.name) errors.name = Array.isArray(data.name) ? data.name[0] : data.name
      if (data.email) errors.email = Array.isArray(data.email) ? data.email[0] : data.email
      if (data.message) errors.message = Array.isArray(data.message) ? data.message[0] : data.message
    }
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped>
.contact-section {
  background: var(--mf-navy);
  padding: 5rem 1.5rem;
}

.contact-heading {
  color: #ffffff;
  font-weight: 800;
}

.contact-subheading {
  color: rgba(255, 255, 255, 0.8);
  max-width: 480px;
  margin-left: auto;
  margin-right: auto;
}

.contact-label {
  color: rgba(255, 255, 255, 0.9);
  font-weight: 600;
}

.input,
.textarea {
  background: rgba(255, 255, 255, 0.08);
  border-color: rgba(255, 255, 255, 0.2);
  color: #ffffff;
  transition: border-color 0.2s ease, background 0.2s ease;
}

.input::placeholder,
.textarea::placeholder {
  color: rgba(255, 255, 255, 0.4);
}

.input:focus,
.textarea:focus {
  background: rgba(255, 255, 255, 0.12);
  border-color: var(--mf-teal);
  box-shadow: 0 0 0 2px rgba(0, 201, 167, 0.2);
  color: #ffffff;
}

.input.is-danger,
.textarea.is-danger {
  border-color: #f87171;
}

.contact-submit-btn {
  background: var(--mf-teal);
  border-color: var(--mf-teal);
  color: #ffffff;
  font-weight: 700;
  font-size: 1rem;
  padding: 1.25rem;
  border-radius: 8px;
  transition: background 0.2s ease, transform 0.15s ease, box-shadow 0.15s ease;
}

.contact-submit-btn:hover:not(:disabled) {
  background: #00b396;
  border-color: #00b396;
  color: #ffffff;
  transform: translateY(-1px);
  box-shadow: 0 4px 16px rgba(0, 201, 167, 0.35);
}

.success-message {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
  padding: 3rem 2rem;
  text-align: center;
}

.success-icon {
  width: 3rem;
  height: 3rem;
  color: var(--mf-teal);
  stroke-width: 1.5;
}

.success-text {
  font-size: 1.25rem;
  font-weight: 600;
  color: #ffffff;
}

.rate-limit-banner {
  margin-bottom: 1.5rem;
}

.honeypot-field {
  position: absolute;
  left: -9999px;
  width: 1px;
  height: 1px;
  opacity: 0;
  pointer-events: none;
}
</style>
