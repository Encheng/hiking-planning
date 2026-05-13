#!/usr/bin/env tsx
/* eslint-disable no-console */
import { readFile } from 'node:fs/promises';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { validateRoute } from '../src/services/RouteValidator';
import type { Route, Hut, RoutesManifest, ValidationReport } from '../src/types';

const __dirname = dirname(fileURLToPath(import.meta.url));
const REPO_ROOT = join(__dirname, '..');

async function loadHuts(): Promise<Hut[]> {
  return JSON.parse(await readFile(join(REPO_ROOT, 'public/data/huts.json'), 'utf8'));
}

async function loadRoute(id: string): Promise<Route> {
  return JSON.parse(
    await readFile(join(REPO_ROOT, 'public/data/routes', `${id}.json`), 'utf8'),
  );
}

function printReport(report: ValidationReport, routeName: string): void {
  console.log(`\n${routeName}`);
  console.log('='.repeat(32));
  if (report.errors === 0 && report.warnings === 0) {
    console.log('✓ All checks pass');
    return;
  }
  if (report.warnings > 0) {
    console.log(`⚠ ${report.warnings} warnings:`);
    for (const i of report.issues.filter((x) => x.severity === 'warning')) {
      console.log(`  - ${i.type}: ${i.message}`);
    }
  }
  if (report.errors > 0) {
    console.log(`✗ ${report.errors} errors:`);
    for (const i of report.issues.filter((x) => x.severity === 'error')) {
      console.log(`  - ${i.type}: ${i.message}`);
    }
  }
}

async function main(): Promise<void> {
  const args = process.argv.slice(2);
  const skipErrors = args.includes('--skip-errors');
  const huts = await loadHuts();
  const manifest: RoutesManifest = JSON.parse(
    await readFile(join(REPO_ROOT, 'public/data/routes-manifest.json'), 'utf8'),
  );

  let routeIds: string[];
  if (args.includes('--all')) {
    routeIds = manifest.routes.filter((r) => r.status === 'done').map((r) => r.id);
  } else {
    const idx = args.indexOf('--route');
    if (idx === -1) {
      console.error('Usage: tsx scripts/validate-routes.ts --all | --route <id> [--skip-errors]');
      process.exit(1);
    }
    routeIds = [args[idx + 1]];
  }

  let totalErrors = 0;
  for (const id of routeIds) {
    try {
      const route = await loadRoute(id);
      const report = validateRoute({ route, huts });
      const entry = manifest.routes.find((r) => r.id === id);
      printReport(report, `${id} (${entry?.name ?? '?'})`);
      totalErrors += report.errors;
    } catch (e) {
      console.error(`${id} load failed:`, e);
      totalErrors++;
    }
  }

  if (totalErrors > 0 && !skipErrors) {
    process.exit(1);
  }
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});
