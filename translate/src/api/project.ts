import { GET } from './utils/base';
import type { LocaleOption } from './other-locales';

export type Tag = {
  readonly slug: string;
  readonly name: string;
  readonly priority: number;
};

export type Project = {
  slug: string;
  name: string;
  info: string;
  tags: Tag[];
  locales: LocaleOption[];
};

export async function fetchProject(slug: string): Promise<Project> {
  const result = await GET(`/api/v2/projects/${slug}`);

  return {
    ...result,
    locales: (result?.localizations ?? []).map(
      (l: { locale: LocaleOption }) => l.locale,
    ),
  };
}
