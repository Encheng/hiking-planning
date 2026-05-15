import type { DefineComponent } from 'vue';
import AppIconComponent from './components/common/AppIcon.vue';

declare module '@vue/runtime-core' {
  interface GlobalComponents {
    AppIcon: typeof AppIconComponent;
  }
}

declare module '*.vue' {
  const component: DefineComponent<Record<string, unknown>, Record<string, unknown>, unknown>;
  export default component;
}

export {};
