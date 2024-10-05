export const getAISearchUrl = (query: string, search_uuid: string) => {
  const prefix =
    process.env.NODE_ENV === "production" ? "/aisearch.html" : "/aisearch";
  return `${prefix}?q=${encodeURIComponent(query)}&rid=${search_uuid}`;
};
