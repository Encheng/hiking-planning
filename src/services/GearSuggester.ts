import type {
  GearTemplates, GearTemplateCategory, CustomItem, GearChecklist,
  ResolvedGearItem, TripType,
} from '@/types';

export interface SuggestInput {
  templates: GearTemplates;
  totalHours: number;
  hasOvernight: boolean;
  hasCamping: boolean;
  customItems: CustomItem[];
  lastChecklist?: GearChecklist;
}

export interface SuggestOutput {
  tripType: TripType;
  categories: Array<{
    id: TripType;
    name: string;
    items: ResolvedGearItem[];
  }>;
}

export function classifyTripType(input: {
  totalHours: number;
  hasOvernight: boolean;
  hasCamping: boolean;
}): TripType {
  if (input.hasCamping) return 'overnight_camp';
  if (input.hasOvernight) return 'overnight_hut';
  if (input.totalHours > 4) return 'long_day';
  return 'light_summit';
}

function categoryMatches(cat: GearTemplateCategory, ctx: SuggestInput): boolean {
  const c = cat.matchCondition;

  // Apply maxHours only when the trip itself is NOT an overnight trip.
  // For overnight trips, day-categories are always included (their gear applies
  // during the day-walks of the multi-day trip).
  if (c.maxHours !== undefined && !ctx.hasOvernight && ctx.totalHours > c.maxHours) {
    return false;
  }

  // overnight:false categories — include for any trip (day gear is always needed)
  // overnight:true (or minNights set) — only include for overnight trips
  if (c.minNights !== undefined && !ctx.hasOvernight) return false;

  // camping flag: include camping-only categories only when actually camping
  if (c.camping === true && !ctx.hasCamping) return false;

  // hut categories (camping: false) — include for any overnight trip (hut OR camp)
  // because camping trips often combine hut and camp nights, so hut gear applies.

  return true;
}

export function suggestGear(input: SuggestInput): SuggestOutput {
  const tripType = classifyTripType(input);
  const matchingCats = input.templates.categories.filter((c) => categoryMatches(c, input));
  const lastChecked = new Set(input.lastChecklist?.checkedItemIds ?? []);

  const categories = matchingCats.map((cat) => {
    const items: ResolvedGearItem[] = [];
    for (const item of cat.items) {
      items.push({
        ...item,
        categoryId: cat.id,
        source: lastChecked.has(item.id) ? 'last_trip' : 'template',
      });
    }
    for (const c of input.customItems) {
      if (!c.defaultCategories.includes(cat.id)) continue;
      const id = `custom_${c.id}`;
      items.push({
        id,
        name: c.name,
        weight_g: c.weightGrams,
        categoryId: cat.id,
        source: 'custom',
      });
    }
    return { id: cat.id, name: cat.name, items };
  });

  return { tripType, categories };
}
