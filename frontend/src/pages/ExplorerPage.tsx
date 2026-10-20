import React, { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { domainsApi, conceptsApi, progressApi, authApi } from '../api/client';
import { useAppStore } from '../hooks/useAppStore';
import { GraphVisualization } from './GraphVisualization';
import { ConceptPanel } from './ConceptPanel';
import { SearchFilter } from './SearchFilter';
import { Domain, Concept, ChildProfile, ConceptProgress, GraphNode, GraphEdge } from '../types';

export const ExplorerPage: React.FC = () => {
  const navigate = useNavigate();
  const { currentDomain } = useParams<{ domainId: string }>();
  const domainId = currentDomain ? parseInt(currentDomain, 10) : null;

  const {
    domains,
    setDomains,
    currentDomain: storeDomain,
    setCurrentDomain,
    subjects,
    setSubjects,
    concepts,
    setConcepts,
    selectedConcept,
    setSelectedConcept,
    profiles,
    setProfiles,
    currentProfile,
    setCurrentProfile,
    progress,
    setProgress,
    updateProgress,
    graphFilter,
  } = useAppStore();

  const [graphData, setGraphData] = useState<{ nodes: GraphNode[]; edges: GraphEdge[] }>({ nodes: [], edges: [] });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [evidenceNotes, setEvidenceNotes] = useState('');

  // Load domains on mount
  useEffect(() => {
    const loadDomains = async () => {
      try {
        const res = await domainsApi.list({ limit: 100 });
        setDomains(res.data.domains);
        if (res.data.domains.length > 0) {
          const targetDomain = domainId
            ? res.data.domains.find((d) => d.id === domainId)
            : res.data.domains.find((d) => d.is_default) || res.data.domains[0];
          if (targetDomain) {
            setCurrentDomain(targetDomain);
          }
        }
      } catch (err) {
        setError('Failed to load domains');
      }
    };
    loadDomains();
  }, [domainId, setDomains, setCurrentDomain]);

  // Load subjects and concepts when domain changes
  useEffect(() => {
    if (!storeDomain) return;
    const loadData = async () => {
      setLoading(true);
      try {
        // Load concepts for this domain
        const conceptsRes = await conceptsApi.search({ domain_id: storeDomain.id, limit: 2000 });
        setConcepts(conceptsRes.data.concepts);

        // Extract unique subjects from concepts
        const subjectIds = [...new Set(conceptsRes.data.concepts.map((c: Concept) => c.subject_id))];
        const subjectRes = await Promise.all(
          subjectIds.map((id) => conceptsApi.search({ subject_id: id, limit: 1 }))
        );
        const uniqueSubjects = subjectRes.map((r) => r.data.concepts[0]?.subject_id).filter(Boolean);
        // We need subject details - for now create mock subjects
        setSubjects(
          [...new Set(conceptsRes.data.concepts.map((c: Concept) => c.subject_id))].map((id) => ({
            id,
            domain_id: storeDomain.id,
            name: `subject_${id}`,
            display_name: `Subject ${id}`,
            description: null,
            age_min: null,
            age_max: null,
            difficulty_min: null,
            difficulty_max: null,
            sort_order: 0,
            metadata: {},
            created_at: '',
            updated_at: '',
          }))
        );

        // Load graph for first concept or center
        if (conceptsRes.data.concepts.length > 0) {
          const centerId = conceptsRes.data.concepts[0].id;
          const graphRes = await conceptsApi.getGraph(centerId, 2);
          setGraphData(graphRes.data);
        }
      } catch (err) {
        setError('Failed to load concepts');
      } finally {
        setLoading(false);
      }
    };
    loadData();
  }, [storeDomain, setConcepts, setSubjects]);

  // Load profiles when authenticated
  useEffect(() => {
    const loadProfiles = async () => {
      try {
        const user = await authApi.me();
        if (user.data.sub) {
          const res = await progressApi.listProfiles(user.data.sub);
          setProfiles(res.data.profiles);
          if (res.data.profiles.length > 0 && !currentProfile) {
            setCurrentProfile(res.data.profiles[0]);
          }
        }
      } catch (err) {
        // Not authenticated, skip
      }
    };
    loadProfiles();
  }, [setProfiles, setCurrentProfile, currentProfile]);

  // Load progress when profile changes
  useEffect(() => {
    if (!currentProfile) return;
    const loadProgress = async () => {
      try {
        const res = await progressApi.getProgress(currentProfile.id, { limit: 500 });
        setProgress(res.data.progress);
      } catch (err) {
        setError('Failed to load progress');
      }
    };
    loadProgress();
  }, [currentProfile, setProgress]);

  // Handle concept selection
  const handleNodeClick = (node: GraphNode | null) => {
    if (!node) {
      setSelectedConcept(null);
      setEvidenceNotes('');
      return;
    }
    const concept = concepts.find((c) => c.id === node.id);
    if (concept) {
      setSelectedConcept(concept);
      const prog = progress.find((p) => p.concept_id === concept.id);
      setEvidenceNotes(prog?.evidence_notes || '');
    }
  };

  const handleStateChange = (state: Concept['state']) => {
    if (!selectedConcept || !currentProfile) return;
    updateProgress(selectedConcept.id, state, evidenceNotes);
    progressApi.upsertProgress(currentProfile.id, {
      concept_id: selectedConcept.id,
      state,
      evidence_notes: evidenceNotes,
    });
  };

  const progressMap = new Map(progress.map((p) => [p.concept_id, p.state]));

  if (loading) {
    return <div style={{ padding: '40px', textAlign: 'center' }}>Loading...</div>;
  }

  if (error) {
    return <div style={{ padding: '40px', textAlign: 'center', color: '#dc3545' }}>{error}</div>;
  }

  if (!storeDomain) {
    return <div style={{ padding: '40px', textAlign: 'center' }}>No domain selected</div>;
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100vh' }}>
      <header style={{ padding: '16px 24px', background: '#fff', borderBottom: '1px solid #dee2e6', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h1 style={{ margin: 0, fontSize: '24px' }}>Orbit Engine — {storeDomain.display_name}</h1>
        <div style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
          <select
            value={storeDomain.id}
            onChange={(e) => {
              const d = domains.find((d) => d.id === parseInt(e.target.value, 10));
              if (d) {
                setCurrentDomain(d);
                navigate(`/explorer/${d.id}`);
              }
            }}
            style={{ padding: '6px 12px', borderRadius: '6px', border: '1px solid #ced4da' }}
          >
            {domains.map((d) => (
              <option key={d.id} value={d.id}>
                {d.display_name}
              </option>
            ))}
          </select>
        </div>
      </header>

      <div style={{ display: 'flex', flex: 1, overflow: 'hidden' }}>
        <aside style={{ width: '380px', borderRight: '1px solid #dee2e6', background: '#fff', display: 'flex', flexDirection: 'column' }}>
          <SearchFilter subjects={subjects} />
          <div style={{ padding: '16px', flex: 1, overflow: 'auto' }}>
            <h3 style={{ margin: '0 0 12px', fontSize: '16px' }}>Child Profiles</h3>
            {profiles.length === 0 ? (
              <p style={{ color: '#6c757d', fontSize: '13px' }}>No profiles. Create one to track progress.</p>
            ) : (
              <select
                value={currentProfile?.id || ''}
                onChange={(e) => {
                  const p = profiles.find((pr) => pr.id === parseInt(e.target.value, 10));
                  if (p) setCurrentProfile(p);
                }}
                style={{ width: '100%', padding: '8px', borderRadius: '6px', border: '1px solid #ced4da', marginBottom: '12px' }}
              >
                {profiles.map((p) => (
                  <option key={p.id} value={p.id}>
                    {p.name}
                  </option>
                ))}
              </select>
            )}
          </div>
        </aside>

        <main style={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
          <GraphVisualization
            nodes={graphData.nodes}
            edges={graphData.edges}
            onNodeClick={handleNodeClick}
            selectedNodeId={selectedConcept?.id || null}
            progressMap={progressMap}
            style={{ flex: 1 }}
          />
        </main>

        <aside style={{ width: '380px', borderLeft: '1px solid #dee2e6', background: '#fff', overflow: 'auto' }}>
          <ConceptPanel
            concept={selectedConcept}
            progressState={selectedConcept ? progressMap.get(selectedConcept.id) || 'not_started' : 'not_started'}
            onStateChange={handleStateChange}
            evidenceNotes={evidenceNotes}
            onEvidenceNotesChange={setEvidenceNotes}
          />
        </aside>
      </div>
    </div>
  );
};