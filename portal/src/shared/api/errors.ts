import axios from "axios";
import type { ApiErrorBody } from "@/shared/types/api";

export class ApiError extends Error {
  readonly status: number;
  readonly code: string;
  readonly details?: unknown[];

  constructor(params: {
    status: number;
    code: string;
    message: string;
    details?: unknown[];
  }) {
    super(params.message);
    this.name = "ApiError";
    this.status = params.status;
    this.code = params.code;
    this.details = params.details;
  }
}

/** Turns anything thrown (axios, network, unknown) into an ApiError. */
export function toApiError(error: unknown): ApiError {
  if (error instanceof ApiError) return error;

  if (axios.isAxiosError<ApiErrorBody>(error)) {
    if (error.response) {
      const body = error.response.data?.error;
      return new ApiError({
        status: error.response.status,
        code: body?.code ?? "HTTP_ERROR",
        message: body?.message ?? "Request failed. Please try again.",
        details: body?.details,
      });
    }
    return new ApiError({
      status: 0,
      code: "NETWORK_ERROR",
      message: "Cannot reach the server. Please try again.",
    });
  }

  return new ApiError({
    status: 0,
    code: "UNKNOWN_ERROR",
    message: error instanceof Error ? error.message : "Something went wrong.",
  });
}
