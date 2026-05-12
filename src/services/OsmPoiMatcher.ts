import levenshtein from 'fast-levenshtein';
import type { OsmPoi } from '@/types';

export interface MatchCandidate {
  poi: OsmPoi;
  similarity: number;
}

const SUFFIXES_TO_STRIP = [
  '山莊', '山屋', '步道', '登山口', '岔路口', '岔路', '營地', '避難山屋', '山徑',
];

const CHINESE_DIGITS: Record<string, string> = {
  '零': '0', '〇': '0', '一': '1', '二': '2', '三': '3', '四': '4',
  '五': '5', '六': '6', '七': '7', '八': '8', '九': '9', '十': '10',
};

function fullWidthToHalfWidth(s: string): string {
  return s.replace(/[！-～]/g, (ch) =>
    String.fromCharCode(ch.charCodeAt(0) - 0xfee0),
  );
}

function normalizeChineseDigits(s: string): string {
  return s.replace(/[零〇一二三四五六七八九十]/g, (ch) => CHINESE_DIGITS[ch] ?? ch);
}

export function normalizeName(name: string): string {
  let s = name.trim();
  s = fullWidthToHalfWidth(s);
  s = normalizeChineseDigits(s);
  s = s.toLowerCase();
  for (const suf of SUFFIXES_TO_STRIP) {
    if (s.endsWith(suf)) {
      s = s.slice(0, -suf.length);
      break;
    }
  }
  return s.replace(/\s+/g, '');
}

function similarityRatio(a: string, b: string): number {
  if (a === b) return 1.0;
  const maxLen = Math.max(a.length, b.length);
  if (maxLen === 0) return 1.0;
  const dist = levenshtein.get(a, b);
  return 1 - dist / maxLen;
}

export function matchPoisToNode(nodeName: string, pois: OsmPoi[]): MatchCandidate[] {
  const normalized = normalizeName(nodeName);
  return pois
    .map((poi) => ({
      poi,
      similarity: similarityRatio(normalized, normalizeName(poi.name)),
    }))
    .filter((r) => r.similarity > 0.5)
    .sort((a, b) => b.similarity - a.similarity);
}
