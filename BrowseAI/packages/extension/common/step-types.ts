// step-types.ts — re-export shared constants to keep single source of truth
export { STEP_TYPES } from '@nexusai/shared';
export type StepTypeConst =
  (typeof import('@nexusai/shared'))['STEP_TYPES'][keyof (typeof import('@nexusai/shared'))['STEP_TYPES']];
