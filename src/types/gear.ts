import type { TripType } from './plan';

export interface GearItem {
  id: string;
  name: string;
  essential?: boolean;
  weight_g?: number;
}

export interface GearTemplateCategory {
  id: TripType;
  name: string;
  matchCondition: {
    maxHours?: number;
    minNights?: number;
    overnight?: boolean;
    camping?: boolean;
  };
  items: GearItem[];
}

export interface GearTemplates {
  categories: GearTemplateCategory[];
}

export interface GearChecklist {
  id?: number;
  planId: number;
  checkedItemIds: string[];
  removedTemplateIds: string[];
}

export interface CustomItem {
  id?: number;
  name: string;
  weightGrams?: number;
  defaultCategories: TripType[];
  lastUsedInPlanId?: number;
}

export interface ResolvedGearItem extends GearItem {
  source: 'template' | 'custom' | 'last_trip';
  categoryId: TripType;
}
