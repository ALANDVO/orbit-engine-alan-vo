import React from 'react';
import { Concept } from '../types';

interface ConceptPanelProps {
  concept: Concept | null;
  progressState: Concept['state'];
  onStateChange: (state: Concept['state'], evidenceNotes?: string) => void;
  evidenceNotes: string;
  onEvidenceNotesChange: (notes: string) => void;
}

const STATE_LABELS: Record<string, string> = {
  not_started: 'Not Started',
  learning: 'Learning',
  known: 'Known',
  assessed: 'Assessed',
};

const STATE_COLORS: Record<string, string> = {
  not_started: '#6c757d',
  learning: '#ffc107',
  known: '#28a745',
  assessed: '#1e7e34',
};

export const ConceptPanel: React.FC<ConceptPanelProps> = ({
  concept,
  progressState,
  onStateChange,
  evidenceNotes,
  onEvidenceNotesChange,
}) => {
  if (!concept) {
    return (
      <div className="concept-panel">
        <p className="text-muted">Click a concept to view details</p>
      </div>
    );
  }

  return (
    <div className="concept-panel" style={{ padding: '16px', maxHeight: '500px', overflow: 'auto' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '12px' }}>
        <h3 style={{ margin: 0, fontSize: '18px' }}>{concept.name}</h3>
        <span
          className="badge"
          style={{
            backgroundColor: STATE_COLORS[progressState],
            color: progressState === 'learning' ? '#212529' : '#fff',
            padding: '4px 10px',
            borderRadius: '12px',
            fontSize: '12px',
            fontWeight: 500,
          }}
        >
          {STATE_LABELS[progressState]}
        </span>
      </div>

      <div style={{ marginBottom: '12px', fontSize: '13px', color: '#6c757d' }}>
        <strong>ID:</strong> {concept.concept_id} | <strong>Subject:</strong> {concept.subject_id}
        {concept.difficulty && <span> | <strong>Difficulty:</strong> {concept.difficulty}</span>}
        {concept.age_min && concept.age_max && (
          <span> | <strong>Age:</strong> {concept.age_min}–{concept.age_max}</span>
        )}
      </div>

      {concept.description && (
        <div style={{ marginBottom: '16px', lineHeight: 1.5 }}>
          <strong>Description:</strong>
          <p style={{ margin: '8px 0 0 0' }}>{concept.description}</p>
        </div>
      )}

      <fieldset style={{ border: '1px solid #dee2e6', borderRadius: '6px', padding: '12px', marginBottom: '16px' }}>
        <legend style={{ fontWeight: 600, padding: '0 8px' }}>Progress</legend>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px', marginBottom: '12px' }}>
          {(['not_started', 'learning', 'known', 'assessed'] as const).map((state) => (
            <button
              key={state}
              type="button"
              onClick={() => onStateChange(state)}
              style={{
                padding: '8px 16px',
                borderRadius: '6px',
                border: `2px solid ${progressState === state ? STATE_COLORS[state] : '#dee2e6'}`,
                backgroundColor: progressState === state ? STATE_COLORS[state] : '#fff',
                color: progressState === state && state !== 'learning' ? '#fff' : '#212529',
                fontWeight: progressState === state ? 600 : 400,
                cursor: 'pointer',
                transition: 'all 0.2s',
              }}
            >
              {STATE_LABELS[state]}
            </button>
          ))}
        </div>

        <div>
          <label style={{ display: 'block', marginBottom: '6px', fontWeight: 500 }}>
            Evidence Notes
          </label>
          <textarea
            value={evidenceNotes}
            onChange={(e) => onEvidenceNotesChange(e.target.value)}
            rows={4}
            style={{
              width: '100%',
              padding: '8px',
              border: '1px solid #ced4da',
              borderRadius: '4px',
              fontSize: '13px',
              fontFamily: 'inherit',
              resize: 'vertical',
            }}
            placeholder="Record assessment evidence, observations, or notes..."
          />
        </div>
      </fieldset>

      {concept.evidence_criteria && (
        <details style={{ marginBottom: '12px' }}>
          <summary style={{ cursor: 'pointer', fontWeight: 500 }}>Evidence Criteria</summary>
          <div style={{ marginTop: '8px', padding: '12px', background: '#f8f9fa', borderRadius: '4px', fontSize: '13px' }}>
            {concept.evidence_criteria}
          </div>
        </details>
      )}

      {concept.assessment_prompt && (
        <details>
          <summary style={{ cursor: 'pointer', fontWeight: 500 }}>Assessment Prompt</summary>
          <div style={{ marginTop: '8px', padding: '12px', background: '#f8f9fa', borderRadius: '4px', fontSize: '13px' }}>
            {concept.assessment_prompt}
          </div>
        </details>
      )}
    </div>
  );
};