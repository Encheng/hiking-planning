#!/usr/bin/env tsx
/* eslint-disable no-console */
import { readFile, writeFile } from 'node:fs/promises';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import type { Route, OsmPoisFile } from '../src/types';
import { matchPoisToNode } from '../src/services/OsmPoiMatcher';

const __dirname = dirname(fileURLToPath(import.meta.url));
const REPO_ROOT = join(__dirname, '..');

const STRONG_THRESHOLD = 0.85;
const SOFT_THRESHOLD = 0.5;

async function align(routeId: string): Promise<void> {
  const routePath = join(REPO_ROOT, 'public/data/routes', `${routeId}.json`);
  const poisPath = join(REPO_ROOT, 'public/data/osm-pois', `${routeId}.json`);

  const route: Route = JSON.parse(await readFile(routePath, 'utf8'));
  const poisFile: OsmPoisFile = JSON.parse(await readFile(poisPath, 'utf8'));

  let aligned = 0;
  let manual = 0;
  let unmatched = 0;

  for (const node of route.nodes) {
    const candidates = matchPoisToNode(node.name, poisFile.pois);
    if (candidates.length === 0) {
      unmatched++;
      continue;
    }
    const top = candidates[0];
    if (top.similarity >= STRONG_THRESHOLD) {
      node.lat = top.poi.lat;
      node.lng = top.poi.lon;
      if (top.poi.elevation !== null) node.elevation = top.poi.elevation;
      if (!node.tags) node.tags = [];
      if (!node.tags.includes('osm-aligned')) node.tags.push('osm-aligned');
      aligned++;
      console.log(`✓ ${node.id} = ${top.poi.name} (${(top.similarity * 100).toFixed(0)}%)`);
    } else if (top.similarity >= SOFT_THRESHOLD) {
      manual++;
      console.log(`? ${node.id} ↔ ${top.poi.name} (${(top.similarity * 100).toFixed(0)}%) — needs manual review`);
    } else {
      unmatched++;
    }
  }

  await writeFile(routePath, JSON.stringify(route, null, 2) + '\n');
  console.log(`\n${routeId}: ${aligned} aligned · ${manual} soft matches · ${unmatched} unmatched (kept as-is)`);
}

async function main(): Promise<void> {
  const args = process.argv.slice(2);
  const routeId = args[args.indexOf('--route') + 1];
  if (!routeId) {
    console.error('Usage: tsx scripts/align-osm.ts --route G02');
    process.exit(1);
  }
  await align(routeId);
}

main().catch((e) => { console.error(e); process.exit(1); });
