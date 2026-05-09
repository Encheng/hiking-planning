import Dexie, { type Table } from 'dexie';
import type { Plan, GearChecklist, CustomItem, CachedTile } from './schemas';

export class HikingDB extends Dexie {
  // Declare tables with explicit key type (number) so that add() returns number, not number|undefined.
  // The insert type (third generic) omits 'id' so callers don't need to supply it.
  plans!: Table<Plan, number, Omit<Plan, 'id'>>;
  gearChecklists!: Table<GearChecklist, number, Omit<GearChecklist, 'id'>>;
  customItems!: Table<CustomItem, number, Omit<CustomItem, 'id'>>;
  tileCache!: Table<CachedTile, string>;

  constructor() {
    super('HikingPlanningDB');
    this.version(1).stores({
      plans: '++id, name, routeId, startDate, createdAt',
      gearChecklists: '++id, planId',
      customItems: '++id, name, lastUsedInPlanId',
      tileCache: 'url, expiresAt',
    });

    // Cascade delete: override plans.delete so that removing a plan also
    // removes all associated gearChecklists within the same transaction.
    // This is needed because Dexie's 'deleting' hook fires inside a
    // single-table transaction and cannot access other object stores.
    this._overridePlanDelete();
  }

  private _overridePlanDelete() {
    const originalDelete = this.plans.delete.bind(this.plans);
    this.plans.delete = (planId: number) => {
      return this.transaction('rw', this.plans, this.gearChecklists, async () => {
        await this.gearChecklists.where('planId').equals(planId).delete();
        await originalDelete(planId);
      });
    };
  }
}

export const db = new HikingDB();

export async function resetDb(): Promise<void> {
  await db.plans.clear();
  await db.gearChecklists.clear();
  await db.customItems.clear();
  await db.tileCache.clear();
}
