export type HutType = 'hut' | 'shelter' | 'campsite';

export interface Hut {
  id: string;
  name: string;
  lat: number;
  lng: number;
  elevation: number;
  capacity?: number;
  type: HutType;
  needPermit?: boolean;
  operator?: string;
}
