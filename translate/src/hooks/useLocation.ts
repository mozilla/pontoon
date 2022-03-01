import { useMemo } from 'react';
import { useAppSelector } from '~/hooks';

export type Location = {
  locale: string;
  project: string;
  resource: string;
  entity: number;
  search: string | null;
  status: string | null;
  extra: string | null;
  tag: string | null;
  author: string | null;
  time: string | null;
};

export function useLocation(): Location {
  const location = useAppSelector((state) => state.router.location);
  return useMemo(() => {
    const { pathname, search } = location;
    const [locale, project, ...resource] = pathname.split('/').filter(Boolean);
    const params = new URLSearchParams(search);
    return {
      locale: locale ?? '',
      project: project ?? '',
      resource: resource.join('/'),
      entity: Number(params.get('string')),
      search: params.get('search'),
      status: params.get('status'),
      extra: params.get('extra'),
      tag: params.get('tag'),
      author: params.get('author'),
      time: params.get('time'),
    };
  }, [location]);
}
