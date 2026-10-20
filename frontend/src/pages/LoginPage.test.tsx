import { render, screen, fireEvent } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import { LoginPage } from '../pages/LoginPage'
import { authApi } from '../api/client'
import { useAppStore } from '../hooks/useAppStore'

// Mock the API
vi.mock('../api/client', () => ({
  authApi: {
    login: vi.fn(),
  },
}))

// Mock the store
vi.mock('../hooks/useAppStore', () => ({
  useAppStore: vi.fn(),
}))

describe('LoginPage', () => {
  const mockSetUser = vi.fn()
  const mockNavigate = vi.fn()

  beforeEach(() => {
    vi.clearAllMocks()
    ;(useAppStore as any).mockReturnValue({
      setUser: mockSetUser,
    })
  })

  it('renders login form', () => {
    render(
      <BrowserRouter>
        <LoginPage />
      </BrowserRouter>
    )
    expect(screen.getByText('Orbit Engine')).toBeInTheDocument()
    expect(screen.getByText('Sign in with Keycloak')).toBeInTheDocument()
  })

  it('calls authApi.login on button click', async () => {
    ;(authApi.login as any).mockResolvedValue({ data: { url: '/demo-login' } })

    render(
      <BrowserRouter>
        <LoginPage />
      </BrowserRouter>
    )

    fireEvent.click(screen.getByText('Sign in with Keycloak'))

    await vi.waitFor(() => {
      expect(authApi.login).toHaveBeenCalled()
    })
  })

  it('sets user and navigates on demo login', async () => {
    ;(authApi.login as any).mockResolvedValue({ data: { url: '/demo-login' } })

    render(
      <BrowserRouter>
        <LoginPage />
      </BrowserRouter>
    )

    fireEvent.click(screen.getByText('Sign in with Keycloak'))

    await vi.waitFor(() => {
      expect(mockSetUser).toHaveBeenCalledWith({
        sub: 'demo-user',
        email: 'demo@example.com',
        name: 'Demo User',
        roles: ['viewer', 'operator'],
      })
    })
  })

  it('shows error on login failure', async () => {
    ;(authApi.login as any).mockRejectedValue(new Error('Network error'))

    render(
      <BrowserRouter>
        <LoginPage />
      </BrowserRouter>
    )

    fireEvent.click(screen.getByText('Sign in with Keycloak'))

    await vi.waitFor(() => {
      expect(screen.getByText('Failed to initiate login')).toBeInTheDocument()
    })
  })
})