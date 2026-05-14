export type OsmCategory = 'trailhead' | 'hut' | 'peak' | 'junction' | 'water' | 'waypoint' | 'shelter';

export interface OsmPoi {
  id: string;
  name: string;
  lat: number;
  lon: number;
  elevation: number | null;
  tags: {
    category: OsmCategory;
    raw: Record<string, string>;
  };
}

export interface OsmPoisFile {
  sourceRelation: number;
  fetchedAt: string;
  pois: OsmPoi[];
}

export type VerificationLevel = 'estimated' | 'sunriver_pending' | 'sunriver_verified' | 'n/a';

export interface RoutesManifestEntry {
  id: string;
  name: string;
  osmRelationId: number | null;
  sunriverImage: string;
  elevationImages: string[];
  status: 'pending' | 'in_progress' | 'done' | 'skipped' | 'failed';
  verification?: VerificationLevel;
  fetchedAt?: string;
}

export interface RoutesManifest {
  version: string;
  attribution: string;
  verificationLevels?: Record<string, string>;
  routes: RoutesManifestEntry[];
}
