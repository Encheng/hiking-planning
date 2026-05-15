/**
 * Pre-trip checklist types.
 * Embedded inside Plan.preTripChecklist (no separate IndexedDB table).
 */

export type ChecklistCategory = 'legal' | 'safety' | 'gear' | 'external' | 'custom';

export interface ChecklistItem {
  /** Stable ID. System-suggested items use deterministic IDs like "legal_park_yushan". User items use UUID. */
  id: string;
  category: ChecklistCategory;
  title: string;
  description?: string;
  /** Optional URL (e.g. NP application site, weather, hut booking). */
  externalLink?: string;
  /** Optional internal app route (e.g. "/gear/123"). */
  internalRoute?: string;
  /** If true, listed as required. UI marks unchecked required items distinctly. */
  required: boolean;
  /** True for system-generated items; false for user-added. */
  systemSuggested: boolean;
  /** ISO datetime when user checked the item. Absent = unchecked. */
  checkedAt?: string;
}

export interface EmergencyContact {
  name: string;
  phone: string;
  relation?: string;
}

export interface PreTripChecklist {
  /** Combined list: system-suggested (refreshed on each load) + user-added (persisted as-is). */
  items: ChecklistItem[];
  /** 留守人 — single primary person to notify before departure and on safe return. */
  custodian?: EmergencyContact;
  /** Additional emergency contacts (family, team mates). */
  emergencyContacts?: EmergencyContact[];
  /** ISO datetime when user expects to report back / be back to civilization. */
  expectedReturnAt?: string;
  /** How custodian will be notified, e.g. ["LINE", "phone"]. */
  notifyMethods?: string[];
  /** Free-form notes (special weather concerns, member health, etc.). */
  notes?: string;
}
