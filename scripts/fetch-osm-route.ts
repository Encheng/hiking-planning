#!/usr/bin/env tsx
/* eslint-disable no-console */
import { readFile, writeFile } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
import { join, dirname } from 'node:path';
import type { OsmCategory, OsmPoi, RoutesManifest } from '../src/types';

const __dirname = dirname(fileURLToPath(import.meta.url));
const REPO_ROOT = join(__dirname, '..');

type OsmTags = Record<string, string>;

interface OsmRelation {
  type: 'relation';
  id: number;
  members: Array<{ type: string; ref: number; role: string }>;
  tags?: OsmTags;
}

interface OsmWay {
  type: 'way';
  id: number;
  nodes: number[];
  tags?: OsmTags;
}

interface OsmNode {
  type: 'node';
  id: number;
  lat: number;
  lon: number;
  tags?: OsmTags;
}

interface OsmResponse {
  elements: Array<OsmRelation | OsmWay | OsmNode>;
}

export interface ParsedRoute {
  segments: Array<Array<{ lat: number; lon: number; ele?: number }>>;
  pois: OsmPoi[];
}

export function extractRelevantTags(tags: OsmTags): { category: OsmCategory; raw: OsmTags } {
  let category: OsmCategory = 'waypoint';
  if (tags.tourism === 'alpine_hut' || tags.tourism === 'wilderness_hut') category = 'hut';
  else if (tags.amenity === 'shelter') category = 'shelter';
  else if (tags.natural === 'peak' || tags.mountain_pass === 'yes') category = 'peak';
  else if (tags.highway === 'trailhead' || tags.tourism === 'information') category = 'trailhead';
  else if (tags.amenity === 'drinking_water' || tags.man_made === 'water_well') category = 'water';
  else if (tags.junction || tags.highway === 'milestone') category = 'junction';
  return { category, raw: tags };
}

export function parseOsmRelation(data: OsmResponse): ParsedRoute {
  const nodes = new Map<number, OsmNode>();
  const ways = new Map<number, OsmWay>();
  let relation: OsmRelation | null = null;
  for (const el of data.elements) {
    if (el.type === 'relation') relation = el;
    else if (el.type === 'way') ways.set(el.id, el);
    else if (el.type === 'node') nodes.set(el.id, el);
  }
  if (!relation) throw new Error('No relation in OSM response');

  const segments: Array<Array<{ lat: number; lon: number; ele?: number }>> = [];
  for (const m of relation.members) {
    if (m.type !== 'way') continue;
    const way = ways.get(m.ref);
    if (!way) {
      console.warn(`Way ${m.ref} not found, skipping`);
      continue;
    }
    const segment = way.nodes
      .map((nid) => nodes.get(nid))
      .filter((n): n is OsmNode => !!n)
      .map((n) => ({
        lat: n.lat,
        lon: n.lon,
        ele: n.tags?.ele ? Number(n.tags.ele) : undefined,
      }));
    if (segment.length >= 2) segments.push(segment);
  }

  const pois: OsmPoi[] = [];
  for (const node of nodes.values()) {
    if (!node.tags?.name) continue;
    pois.push({
      id: `osm_node_${node.id}`,
      name: node.tags.name,
      lat: node.lat,
      lon: node.lon,
      elevation: node.tags.ele ? Number(node.tags.ele) : null,
      tags: extractRelevantTags(node.tags),
    });
  }

  return { segments, pois };
}

export function buildGpx(
  routeId: string,
  segments: Array<Array<{ lat: number; lon: number; ele?: number }>>,
): string {
  const segXml = segments
    .map((seg) => {
      const pts = seg
        .map((p) => {
          const ele = p.ele !== undefined ? `<ele>${p.ele}</ele>` : '';
          return `      <trkpt lat="${p.lat}" lon="${p.lon}">${ele}</trkpt>`;
        })
        .join('\n');
      return `    <trkseg>\n${pts}\n    </trkseg>`;
    })
    .join('\n');
  return `<?xml version="1.0" encoding="UTF-8"?>
<gpx version="1.1" creator="hiking-planning/fetch-osm-route" xmlns="http://www.topografix.com/GPX/1/1">
  <trk>
    <name>${routeId}</name>
${segXml}
  </trk>
</gpx>
`;
}

const OVERPASS_URL = 'https://overpass-api.de/api/interpreter';

function query(relationId: number): string {
  return `[out:json][timeout:60];relation(${relationId});(._;>>;);out body;`;
}

async function fetchOsm(relationId: number): Promise<OsmResponse> {
  const body = `data=${encodeURIComponent(query(relationId))}`;
  for (let attempt = 1; attempt <= 2; attempt++) {
    const res = await fetch(OVERPASS_URL, {
      method: 'POST',
      body,
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    });
    if (res.ok) return res.json() as Promise<OsmResponse>;

    // Rate limited or transient server error → wait and retry once
    if (attempt === 1 && (res.status === 429 || res.status >= 500)) {
      const waitMs = res.status === 429 ? 30_000 : 60_000;
      console.warn(`Overpass HTTP ${res.status}, waiting ${waitMs / 1000}s before retry`);
      await sleep(waitMs);
      continue;
    }

    throw new Error(`Overpass HTTP ${res.status}`);
  }
  throw new Error('Overpass: unreachable');
}

async function fetchOsmRouteOnce(relationId: number, outputId: string): Promise<void> {
  console.log(`Fetching OSM relation ${relationId} for ${outputId}...`);
  const data = await fetchOsm(relationId);
  const parsed = parseOsmRelation(data);
  const gpxXml = buildGpx(outputId, parsed.segments);
  await writeFile(join(REPO_ROOT, 'public/data/gpx', `${outputId}.gpx`), gpxXml);
  await writeFile(
    join(REPO_ROOT, 'public/data/osm-pois', `${outputId}.json`),
    JSON.stringify(
      {
        sourceRelation: relationId,
        fetchedAt: new Date().toISOString(),
        pois: parsed.pois,
      },
      null,
      2,
    ),
  );
  console.log(`✓ ${outputId}: ${parsed.segments.length} segments, ${parsed.pois.length} POIs`);
}

function sleep(ms: number): Promise<void> {
  return new Promise((r) => setTimeout(r, ms));
}

async function batch(): Promise<void> {
  const manifestPath = join(REPO_ROOT, 'public/data/routes-manifest.json');
  const manifest: RoutesManifest = JSON.parse(await readFile(manifestPath, 'utf8'));
  for (const route of manifest.routes) {
    if (route.status === 'skipped' || !route.osmRelationId) continue;
    if (route.status === 'done') {
      console.log(`Skipping ${route.id} (already done)`);
      continue;
    }
    try {
      await fetchOsmRouteOnce(route.osmRelationId, route.id);
      route.status = 'done';
      route.fetchedAt = new Date().toISOString();
    } catch (e) {
      console.error(`${route.id} failed:`, e);
      route.status = 'failed';
    }
    await writeFile(manifestPath, JSON.stringify(manifest, null, 2));
    await sleep(5_000);
  }
}

async function main(): Promise<void> {
  const args = process.argv.slice(2);
  if (args.includes('--batch')) {
    await batch();
    return;
  }
  const relIdx = args.indexOf('--relation-id');
  const outIdx = args.indexOf('--output-id');
  if (relIdx === -1 || outIdx === -1) {
    console.error('Usage: tsx scripts/fetch-osm-route.ts --relation-id <id> --output-id <G02> | --batch');
    process.exit(1);
  }
  const relationId = Number(args[relIdx + 1]);
  const outputId = args[outIdx + 1];
  await fetchOsmRouteOnce(relationId, outputId);
}

if (import.meta.url === `file://${process.argv[1]}`) {
  main().catch((e) => {
    console.error(e);
    process.exit(1);
  });
}
