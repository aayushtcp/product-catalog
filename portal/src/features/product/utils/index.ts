import { useState } from "react";

export const PAGE_SIZE = 12;

export function useImageIndex() {
  const [index, setIndex] = useState(0);
  return { index, select: setIndex };
}

export function parsePage(raw: string | null): number {
  return Math.max(1, Number(raw ?? "1") || 1);
}

export function getPageNavigation(page: number, totalPages: number) {
  return {
    previous: page > 1 ? page - 1 : null,
    next: page < totalPages ? page + 1 : null,
  };
}

export function getPaginationLabel(
  page: number,
  totalPages: number,
  total: number,
): string {
  return `Page ${page} of ${totalPages} · ${total} products`;
}
