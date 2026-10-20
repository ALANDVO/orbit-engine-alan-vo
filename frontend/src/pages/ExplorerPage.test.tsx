import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import { ExplorerPage } from '../pages/ExplorerPage'
import { domainsApi, conceptsApi, progressApi, authApi } from '../api/client'
import { useAppStore } from '../hooks/useAppStore'

// Mock APIs
vi.mock('../api/client', () => ({
  domainsApi: {
    list: vi.fn(),
  },
  conceptsApi: {
    search: vi.fn(),
    getGraph: vi.fn(),
  },
  progressApi: {
    listProfiles: vi.fn(),
    getProgress: vi.fn(),
    upsertProgress: vi.fn(),
  },
  authApi: {
    me: vi.fn(),
  },
}))

// Mock store
vi.mock('../hooks/useAppStore', () => ({
  useAppStore: vi.fn(),
}))

describe('ExplorerPage', () => {
  const mockStore = {
    domains: [],
    setDomains: vi.fn(),
    currentDomain: null,
    setCurrentDomain: vi.fn(),
    subjects: [],
    setSubjects: vi.fn(),
    concepts: [],
    setConcepts: vi.fn(),
    selectedConcept: null,
    setSelectedConcept: vi.fn(),
    profiles: [],
    setProfiles: vi.fn(),
    currentProfile: null,
    setCurrentProfile: vi.fn(),
    progress: [],
    setProgress: vi.fn(),
    updateProgress: vi.fn(),
    graphFilter: {
      showKnown: false,
      dimKnown: false,
      hideKnown: false,
      subjectFilter: null,
      ageFilter: { min: null, max: null },
      searchQuery: '',
    },
    setGraphFilter: vi.fn(),
  }

  beforeEach(() => {
    vi.clearAllMocks()
    ;(useAppStore as any).mockReturnValue(mockStore)
    ;(authApi.me as any).mockResolvedValue({ data: { sub: 'test-user' } })
    ;(domainsApi.list as any).mockResolvedValue({
      data: {
        domains: [
          { id: 1, name: 'default', display_name: 'Default Domain', is_default: true },
        ],
      },
    })
    ;(conceptsApi.search as any).mockResolvedValue({
      data: { concepts: [], total: 0 },
    })
    ;(conceptsApi.getGraph as any).mockResolvedValue({
      data: { nodes: [], edges: [] },
    })
    ;(progressApi.listProfiles as any).mockResolvedValue({
      data: { profiles: [], total: 0 },
    })
  })

  it('renders loading state initially', () => {
    render(
      <BrowserRouter>
        <ExplorerPage />
      </BrowserRouter>
    )
    expect(screen.getByText('Loading...')).toBeInTheDocument()
  })

  it('renders domain selector after loading', async () => {
    render(
      <BrowserRouter>
        <ExplorerPage />
      </BrowserRouter>
    )

    await waitFor(() => {
      expect(screen.getByText('Default Domain')).toBeInTheDocument()
    })
  })
})