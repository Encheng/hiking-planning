import Dexie, { type Table } from 'dexie';
import type { Plan, GearChecklist, CustomItem, CachedTile } from './schemas';
import { deriveDailyPlansFromLegacy } from '@/services/DailyPlanMigration';

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

    this.version(2).stores({
      plans: '++id, name, routeId, startDate, createdAt',
      gearChecklists: '++id, planId',
      customItems: '++id, name, lastUsedInPlanId',
      tileCache: 'url, expiresAt',
    }).upgrade((tx) => {
      return tx.table('plans').toCollection().modify((plan: Plan) => {
        if ((plan as Plan & { dailyPlans?: unknown }).dailyPlans !== undefined) return;
        try {
          const migrated = deriveDailyPlansFromLegacy({
            startNodeId: plan.startNodeId,
            endNodeId: plan.endNodeId,
            nodeSequence: plan.nodeSequence,
            dayBreaks: plan.dayBreaks,
          });
          plan.dailyPlans = migrated.dailyPlans;
          plan.returnToStart = migrated.returnToStart;
        } catch (e) {
          console.error('[Dexie v2 upgrade] migration failed for plan', plan.id, e);
          plan.dailyPlans = [];
          plan.returnToStart = true;
        }
      });
    });

    // Cascade delete: override Table.delete so that removing a plan also
    // removes all associated gearChecklists within the same rw transaction.
    //
    // Why override instead of plans.hook('deleting'):
    //   The deleting hook fires per-record and would require every caller to
    //   pre-enlist both `plans` and `gearChecklists` in their own outer
    //   transaction (otherwise the cascade write throws). The override
    //   establishes the multi-table transaction internally, so callers don't
    //   need to know about the dependency.
    //
    // LIMITATION: This override covers `db.plans.delete(id)` only.
    // The following deletion paths bypass it and will leave orphaned gearChecklists:
    //   - db.plans.where(...).delete()      (Collection.delete)
    //   - db.plans.bulkDelete([...])        (Table.bulkDelete)
    //   - db.plans.clear()                  (Table.clear) — used in resetDb intentionally
    // For bulk deletions requiring cascade, write an explicit transaction.
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
