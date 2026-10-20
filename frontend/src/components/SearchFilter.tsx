import React from 'react';
import { Subject } from '../types';
import { useAppStore } from '../hooks/useAppStore';

interface SearchFilterProps {
  subjects: Subject[];
}

export const SearchFilter: React.FC<SearchFilterProps> = ({ subjects }) => {
  const { graphFilter, setGraphFilter } = useAppStore();

  return (
    <div className="search-filter" style={{ padding: '16px', background: '#fff', borderRadius: '8px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)', marginBottom: '16px' }}>
      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '12px', alignItems: 'flex-end' }}>
        <div style={{ flex: 1, minWidth: '200px' }}>
          <label style={{ display: 'block', marginBottom: '4px', fontWeight: 500, fontSize: '13px' }}>Search Concepts</label>
          <input
            type="text"
            value={graphFilter.searchQuery}
            onChange={(e) => setGraphFilter({ searchQuery: e.target.value })}
            placeholder="Search by name or ID..."
            style={{
              width: '100%',
              padding: '8px 12px',
              border: '1px solid #ced4da',
              borderRadius: '6px',
              fontSize: '14px',
            }}
          />
        </div>

        <div style={{ minWidth: '180px' }}>
          <label style={{ display: 'block', marginBottom: '4px', fontWeight: 500, fontSize: '13px' }}>Subject</label>
          <select
            value={graphFilter.subjectFilter ?? ''}
            onChange={(e) => setGraphFilter({ subjectFilter: e.target.value ? parseInt(e.target.value, 10) : null })}
            style={{
              width: '100%',
              padding: '8px 12px',
              border: '1px solid #ced4da',
              borderRadius: '6px',
              fontSize: '14px',
              background: '#fff',
            }}
          >
            <option value="">All Subjects</option>
            {subjects.map((s) => (
              <option key={s.id} value={s.id}>
                {s.display_name}
              </option>
            ))}
          </select>
        </div>

        <div style={{ display: 'flex', gap: '8px', minWidth: '250px' }}>
          <div style={{ flex: 1 }}>
            <label style={{ display: 'block', marginBottom: '4px', fontWeight: 500, fontSize: '13px' }}>Min Age</label>
            <input
              type="number"
              value={graphFilter.ageFilter.min ?? ''}
              onChange={(e) => setGraphFilter({ ageFilter: { ...graphFilter.ageFilter, min: e.target.value ? parseInt(e.target.value, 10) : null } })}
              placeholder="Min"
              min="0"
              max="100"
              style={{
                width: '100%',
                padding: '8px 12px',
                border: '1px solid #ced4da',
                borderRadius: '6px',
                fontSize: '14px',
              }}
            />
          </div>
          <div style={{ flex: 1 }}>
            <label style={{ display: 'block', marginBottom: '4px', fontWeight: 500, fontSize: '13px' }}>Max Age</label>
            <input
              type="number"
              value={graphFilter.ageFilter.max ?? ''}
              onChange={(e) => setGraphFilter({ ageFilter: { ...graphFilter.ageFilter, max: e.target.value ? parseInt(e.target.value, 10) : null } })}
              placeholder="Max"
              min="0"
              max="100"
              style={{
                width: '100%',
                padding: '8px 12px',
                border: '1px solid #ced4da',
                borderRadius: '6px',
                fontSize: '14px',
              }}
            />
          </div>
        </div>

        <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
          <label style={{ display: 'flex', alignItems: 'center', gap: '6px', cursor: 'pointer' }}>
            <input
              type="checkbox"
              checked={graphFilter.dimKnown}
              onChange={(e) => setGraphFilter({ dimKnown: e.target.checked })}
            />
            <span style={{ fontSize: '13px' }}>Dim Known</span>
          </label>
          <label style={{ display: 'flex', alignItems: 'center', gap: '6px', cursor: 'pointer' }}>
            <input
              type="checkbox"
              checked={graphFilter.hideKnown}
              onChange={(e) => setGraphFilter({ hideKnown: e.target.checked, dimKnown: e.target.checked ? false : graphFilter.dimKnown })}
            />
            <span style={{ fontSize: '13px' }}>Hide Known</span>
          </label>
          <label style={{ display: 'flex', alignItems: 'center', gap: '6px', cursor: 'pointer' }}>
            <input
              type="checkbox"
              checked={graphFilter.showKnown}
              onChange={(e) => setGraphFilter({ showKnown: e.target.checked, hideKnown: e.target.checked ? false : graphFilter.hideKnown })}
            />
            <span style={{ fontSize: '13px' }}>Show Only Known</span>
          </label>
        </div>
      </div>
    </div>
  );
};