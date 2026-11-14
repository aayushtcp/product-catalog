"use client";

import Image from "next/image";
import { useState } from "react";
import { PLACEHOLDER_IMAGE, resolveImageUrl } from "@/shared/utils";

type ProductImageProps = {
  src: string | null | undefined;
  alt: string;
  className?: string;
  sizes?: string;
  priority?: boolean;
};

export default function ProductImage({
  src,
  alt,
  className = "object-cover",
  sizes,
  priority = false,
}: ProductImageProps) {
  const resolved = resolveImageUrl(src);
  const [failedSrc, setFailedSrc] = useState<string | null>(null);

  const current = failedSrc === resolved ? PLACEHOLDER_IMAGE : resolved;

  return (
    <Image
      src={current}
      alt={alt}
      fill
      unoptimized
      sizes={sizes}
      priority={priority}
      className={className}
      onError={() => setFailedSrc(resolved)}
    />
  );
}
