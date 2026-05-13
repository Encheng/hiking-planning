export type ValidationSeverity = 'error' | 'warning';

export interface ValidationIssue {
  severity: ValidationSeverity;
  route: string;
  type: string;
  message: string;
  ref?: string;
}

export interface ValidationReport {
  errors: number;
  warnings: number;
  issues: ValidationIssue[];
}
