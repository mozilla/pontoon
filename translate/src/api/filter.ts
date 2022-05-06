import { GET } from './_base';

export type Author = {
  email: string;
  display_name: string;
  id: number;
  gravatar_url: string;
  translation_count: number;
  role: string;
};

export type FilterData = {
  readonly authors: Author[];
  readonly counts_per_minute: number[][];
};

/** Return data needed for filtering strings. */
export const fetchFilterData = (
  locale: string,
  project: string,
  resource: string,
): Promise<FilterData> =>
  GET(`/${locale}/${project}/${resource}/authors-and-time-range/`);
