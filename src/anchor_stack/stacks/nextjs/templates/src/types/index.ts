/**
 * Common TypeScript type definitions
 */

/**
 * Make all properties of T optional and nullable
 */
export type Nullable<T> = {
  [P in keyof T]: T[P] | null;
};

/**
 * Extract the resolved type of a Promise
 */
export type Awaited<T> = T extends Promise<infer U> ? U : T;

/**
 * API Response wrapper type
 */
export interface ApiResponse<T> {
  data: T;
  success: boolean;
  message?: string;
}

/**
 * Pagination parameters
 */
export interface PaginationParams {
  page: number;
  limit: number;
}

/**
 * Paginated response
 */
export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  limit: number;
  totalPages: number;
}
