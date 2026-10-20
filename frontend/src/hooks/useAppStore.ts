import { create } from 'zustand';
import { Domain, Subject, Concept, ChildProfile, ConceptProgress, UserInfo } from '../types';

interface AppState {
  // Auth
  user: UserInfo | null;
  isAuthenticated: boolean;
  setUser: (user: UserInfo | null) => void;
  logout: () => void;

  // Domains
  domains: Domain[];
  currentDomain: Domain | null;
  setDomains: (domains: Domain[]) => void;
  setCurrentDomain: (domain: Domain | null) => void;

  // Subjects
  subjects: Subject[];
  setSubjects: (subjects: Subject[]) => void;

  // Concepts
  concepts: Concept[];
  selectedConcept: Concept | null;
  setConcepts: (concepts: Concept[]) => void;
  setSelectedConcept: (concept: Concept | null) => void;

  // Progress
  profiles: ChildProfile[];
  currentProfile: ChildProfile | null;
  progress: ConceptProgress[];
  setProfiles: (profiles: ChildProfile[]) => void;
  setCurrentProfile: (profile: ChildProfile | null) => void;
  setProgress: (progress: ConceptProgress[]) => void;
  updateProgress: (conceptId: number, state: ConceptProgress['state'], evidenceNotes?: string) => void;

  // UI
  graphFilter: {
    showKnown: boolean;
    dimKnown: boolean;
    hideKnown: boolean;
    subjectFilter: number | null;
    ageFilter: { min: number | null; max: number | null };
    searchQuery: string;
  };
  setGraphFilter: (filter: Partial<AppState['graphFilter']>) => void;
}

export const useAppStore = create<AppState>((set) => ({
  user: null,
  isAuthenticated: false,
  setUser: (user) => set({ user, isAuthenticated: !!user }),
  logout: () => set({ user: null, isAuthenticated: false }),

  domains: [],
  currentDomain: null,
  setDomains: (domains) => set({ domains }),
  setCurrentDomain: (domain) => set({ currentDomain: domain }),

  subjects: [],
  setSubjects: (subjects) => set({ subjects }),

  concepts: [],
  selectedConcept: null,
  setConcepts: (concepts) => set({ concepts }),
  setSelectedConcept: (concept) => set({ selectedConcept: concept }),

  profiles: [],
  currentProfile: null,
  progress: [],
  setProfiles: (profiles) => set({ profiles }),
  setCurrentProfile: (profile) => set({ currentProfile: profile }),
  setProgress: (progress) => set({ progress }),
  updateProgress: (conceptId, state, evidenceNotes) =>
    set((s) => ({
      progress: s.progress.map((p) =>
        p.concept_id === conceptId ? { ...p, state, evidence_notes: evidenceNotes ?? p.evidence_notes } : p
      ),
    })),

  graphFilter: {
    showKnown: false,
    dimKnown: false,
    hideKnown: false,
    subjectFilter: null,
    ageFilter: { min: null, max: null },
    searchQuery: '',
  },
  setGraphFilter: (filter) =>
    set((s) => ({
      graphFilter: { ...s.graphFilter, ...filter },
    })),
}));