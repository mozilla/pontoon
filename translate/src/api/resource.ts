import { GET } from './utils/base';

type APIResource = {
  readonly title: string;
  readonly approved_strings: number;
  readonly pretranslated_strings: number;
  readonly strings_with_warnings: number;
  readonly resource__total_strings: number;
};

export const fetchAllResources = (
  locale: string,
  project: string,
): Promise<APIResource[]> => GET(`/${locale}/${project}/parts/`);
