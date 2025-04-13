import { GET } from './utils/base';

type APIResource = {
  readonly title: string;
  readonly approved: number;
  readonly pretranslated: number;
  readonly warnings: number;
  readonly total: number;
};

export const fetchAllResources = (
  locale: string,
  project: string,
): Promise<APIResource[]> => GET(`/${locale}/${project}/parts/`);
