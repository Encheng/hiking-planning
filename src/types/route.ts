export type NodeCategory = 'trailhead' | 'hut' | 'peak' | 'junction' | 'waypoint' | 'water';

export interface RouteNode {
  id: string;
  name: string;
  lat: number;
  lng: number;
  elevation: number;
  category: NodeCategory;
  hutId?: string | null;
  tags?: string[];
}

export interface RouteEdge {
  from: string;
  to: string;
  minutes_forward: number;
  minutes_backward: number;
  source: string;
}

export interface RoutePreset {
  id: string;
  name: string;
  startNodeId: string;
  endNodeId: string;
  viaNodeIds?: string[];
  suggestedDayBreaks?: Array<{ atNodeId: string; type: 'hut' | 'shelter' | 'camp' }>;
}

export interface Route {
  id: string;
  name: string;
  version: string;
  source: string;
  nodes: RouteNode[];
  edges: RouteEdge[];
  presets: RoutePreset[];
}
