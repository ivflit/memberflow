import { describe, it, expect, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import LoginView from '../../../src/views/LoginView.vue'

vi.mock('../../../src/stores/auth.js', () => ({
  useAuthStore: () => ({
    accessToken: null,
    user: null,
    isAuthenticated: false,
    login: vi.fn(),
  }),
}))

vi.mock('../../../src/router/index.js', () => ({
  default: { push: vi.fn() },
}))

vi.mock('vue-router', () => ({
  useRouter: () => ({ push: vi.fn() }),
  useRoute: () => ({ query: {} }),
  RouterLink: { template: '<a><slot /></a>' },
}))

describe('LoginView — regression', () => {
  it('login page renders email and password fields', () => {
    const wrapper = mount(LoginView)
    expect(wrapper.find('input[type="email"]').exists()).toBe(true)
    expect(wrapper.find('input[type="password"]').exists()).toBe(true)
  })

  it('login page renders Sign in heading', () => {
    const wrapper = mount(LoginView)
    expect(wrapper.text()).toContain('Sign in')
  })

  it('login form has submit button', () => {
    const wrapper = mount(LoginView)
    expect(wrapper.find('button[type="submit"]').exists()).toBe(true)
  })
})
