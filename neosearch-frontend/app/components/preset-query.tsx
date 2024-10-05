import { getAISearchUrl } from "@/app/utils/get-search-url";
import { nanoid } from "nanoid";
import Link from "next/link";
import React, { FC, useMemo } from "react";

export const PresetQuery: FC<{ query: string }> = ({ query }) => {
  const rid = useMemo(() => nanoid(), [query]);

  return (
    <Link
      prefetch={false}
      title={query}
      href={getAISearchUrl(query, rid)}
      className="border border-blue-300/50 text-ellipsis overflow-hidden text-nowrap items-center rounded-lg bg-blue-300 hover:bg-blue-950/80 hover:text-blue-200 px-2 py-1 text-xs font-medium text-blue-600"
    >
      {query}
    </Link>
  );
};
