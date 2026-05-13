import { describe, it, expect } from 'vitest';
import { parseOsmRelation, buildGpx, extractRelevantTags } from '../../scripts/fetch-osm-route';

type OsmArg = Parameters<typeof parseOsmRelation>[0];

// eslint-disable-next-line @typescript-eslint/no-explicit-any
const MOCK_OSM: OsmArg = {
  elements: [
    {
      type: 'relation' as const,
      id: 100,
      members: [
        { type: 'way', ref: 200, role: '' },
        { type: 'way', ref: 201, role: '' },
      ],
      tags: { route: 'hiking', name: 'Test Route' },
    },
    { type: 'way' as const, id: 200, nodes: [301, 302, 303], tags: {} },
    { type: 'way' as const, id: 201, nodes: [303, 304], tags: {} },
    { type: 'node' as const, id: 301, lat: 23.5, lon: 121.0, tags: { name: 'Start', highway: 'trailhead' } },
    { type: 'node' as const, id: 302, lat: 23.51, lon: 121.01, tags: {} },
    { type: 'node' as const, id: 303, lat: 23.52, lon: 121.02, tags: { name: 'Hut', tourism: 'alpine_hut', ele: '3000' } },
    { type: 'node' as const, id: 304, lat: 23.53, lon: 121.03, tags: { name: 'Peak', natural: 'peak' } },
  ],
};

describe('parseOsmRelation', () => {
  it('extracts ordered way segments', () => {
    const result = parseOsmRelation(MOCK_OSM);
    expect(result.segments).toHaveLength(2);
    expect(result.segments[0]).toHaveLength(3);
    expect(result.segments[0][0]).toEqual({ lat: 23.5, lon: 121.0, ele: undefined });
  });

  it('extracts named POIs with category', () => {
    const result = parseOsmRelation(MOCK_OSM);
    expect(result.pois).toHaveLength(3);
    const start = result.pois.find((p) => p.name === 'Start');
    expect(start?.tags.category).toBe('trailhead');
    const hut = result.pois.find((p) => p.name === 'Hut');
    expect(hut?.tags.category).toBe('hut');
    expect(hut?.elevation).toBe(3000);
    const peak = result.pois.find((p) => p.name === 'Peak');
    expect(peak?.tags.category).toBe('peak');
  });

  it('excludes nodes without name', () => {
    const result = parseOsmRelation(MOCK_OSM);
    expect(result.pois.find((p) => p.id === 'osm_node_302')).toBeUndefined();
  });
});

describe('extractRelevantTags', () => {
  it('alpine_hut → hut', () => {
    expect(extractRelevantTags({ tourism: 'alpine_hut' }).category).toBe('hut');
  });
  it('natural=peak → peak', () => {
    expect(extractRelevantTags({ natural: 'peak' }).category).toBe('peak');
  });
  it('amenity=drinking_water → water', () => {
    expect(extractRelevantTags({ amenity: 'drinking_water' }).category).toBe('water');
  });
  it('no relevant tag → waypoint', () => {
    expect(extractRelevantTags({ name: 'something' }).category).toBe('waypoint');
  });
});

describe('buildGpx', () => {
  it('produces valid GPX XML with trksegs', () => {
    const xml = buildGpx('G02', [
      [{ lat: 23.5, lon: 121.0 }, { lat: 23.51, lon: 121.01 }],
      [{ lat: 23.52, lon: 121.02, ele: 3000 }],
    ]);
    expect(xml).toContain('<gpx');
    expect(xml).toContain('<trkseg>');
    expect(xml).toContain('lat="23.5"');
    expect(xml).toContain('<ele>3000</ele>');
    expect(xml.match(/<trkseg>/g)?.length).toBe(2);
  });
});
