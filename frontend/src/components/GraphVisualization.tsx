import React, { useEffect, useRef } from 'react';
import cytoscape from 'cytoscape';
import coseBilkent from 'cytoscape-cose-bilkent';
import { GraphNode, GraphEdge, Concept } from '../types';
import { useAppStore } from '../hooks/useAppStore';

cytoscape.use(coseBilkent);

interface GraphVisualizationProps {
  nodes: GraphNode[];
  edges: GraphEdge[];
  onNodeClick: (node: GraphNode) => void;
  selectedNodeId: number | null;
  progressMap: Map<number, Concept['state']>;
}

export const GraphVisualization: React.FC<GraphVisualizationProps> = ({
  nodes,
  edges,
  onNodeClick,
  selectedNodeId,
  progressMap,
}) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const cyRef = useRef<cytoscape.Core | null>(null);

  useEffect(() => {
    if (!containerRef.current) return;

    const cy = cytoscape({
      container: containerRef.current,
      elements: [
        ...nodes.map((node) => ({
          data: {
            id: String(node.id),
            label: node.name,
            conceptId: node.concept_id,
            difficulty: node.difficulty,
            subjectId: node.subject_id,
            state: progressMap.get(node.id) || 'not_started',
          },
          classes: `state-${progressMap.get(node.id) || 'not_started'}`,
        })),
        ...edges.map((edge) => ({
          data: {
            id: `e-${edge.source}-${edge.target}`,
            source: String(edge.source),
            target: String(edge.target),
            weight: edge.weight,
          },
        })),
      ],
      style: [
        {
          selector: 'node',
          style: {
            'label': 'data(label)',
            'text-valign': 'center',
            'text-halign': 'center',
            'font-size': '10px',
            'width': '40px',
            'height': '40px',
            'background-color': '#4a90d9',
            'color': '#fff',
            'border-width': '2px',
            'border-color': '#fff',
            'text-wrap': 'wrap',
            'text-max-width': '80px',
          },
        },
        {
          selector: 'node.state-known',
          style: {
            'background-color': '#28a745',
            'opacity': 0.7,
          },
        },
        {
          selector: 'node.state-assessed',
          style: {
            'background-color': '#1e7e34',
            'border-color': '#ffc107',
            'border-width': '3px',
          },
        },
        {
          selector: 'node.state-learning',
          style: {
            'background-color': '#ffc107',
            'color': '#212529',
          },
        },
        {
          selector: 'node:selected',
          style: {
            'border-color': '#ffc107',
            'border-width': '3px',
            'background-color': '#0056b3',
          },
        },
        {
          selector: 'edge',
          style: {
            'width': 1.5,
            'line-color': '#adb5bd',
            'target-arrow-shape': 'triangle',
            'target-arrow-color': '#adb5bd',
            'curve-style': 'bezier',
            'opacity': 0.6,
          },
        },
        {
          selector: 'edge:selected',
          style: {
            'line-color': '#ffc107',
            'target-arrow-color': '#ffc107',
            'width': 2.5,
          },
        },
      ],
      layout: {
        name: 'cose-bilkent',
        animate: true,
        animationDuration: 500,
        nodeDimensionsIncludeLabels: true,
        padding: 50,
        idealEdgeLength: 100,
        nodeRepulsion: 400000,
        edgeElasticity: 100,
        nestingFactor: 0.1,
        gravity: 1,
        numIter: 2500,
        tile: true,
        tilingPaddingVertical: 10,
        tilingPaddingHorizontal: 10,
      },
      minZoom: 0.1,
      maxZoom: 3,
      wheelSensitivity: 0.2,
    });

    cyRef.current = cy;

    cy.on('tap', 'node', (evt) => {
      const nodeId = parseInt(evt.target.id(), 10);
      const node = nodes.find((n) => n.id === nodeId);
      if (node) {
        onNodeClick(node);
      }
    });

    cy.on('tap', (evt) => {
      if (evt.target === cy) {
        onNodeClick(null as any);
      }
    });

    return () => {
      cy.destroy();
      cyRef.current = null;
    };
  }, []);

  useEffect(() => {
    if (!cyRef.current) return;
    const cy = cyRef.current;

    cy.elements().remove();
    cy.add([
      ...nodes.map((node) => ({
        data: {
          id: String(node.id),
          label: node.name,
          conceptId: node.concept_id,
          difficulty: node.difficulty,
          subjectId: node.subject_id,
          state: progressMap.get(node.id) || 'not_started',
        },
        classes: `state-${progressMap.get(node.id) || 'not_started'}`,
      })),
      ...edges.map((edge) => ({
        data: {
          id: `e-${edge.source}-${edge.target}`,
          source: String(edge.source),
          target: String(edge.target),
          weight: edge.weight,
        },
      })),
    ]);

    // Update selection
    cy.$(`#${selectedNodeId}`).select();
  }, [nodes, edges, selectedNodeId, progressMap]);

  return <div ref={containerRef} style={{ width: '100%', height: '100%', minHeight: '500px' }} />;
};