/** Error body returned by the FastAPI backend. */
export type ApiErrorBody = {
  error: {
    code: string;
    message: string;
    details?: unknown[];
  };
};

/** Paginated response used by every list endpoint. */
export type Page<T> = {
  items: T[];
  page: number;
  limit: number;
  total: number;
  totalPages: number;
};
