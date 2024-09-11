import type History from 'history';
import React, {
  createContext,
  useContext,
  useLayoutEffect,
  useState,
} from 'react';

export type Location = {
  push(location: string | Partial<Location>): void;
  replace(location: string | Partial<Location>): void;
  locale: string;
  project: string;
  resource: string;
  entity: number;

  /** If set, other optional query parameters are ignored.  */
  list: number[] | null;

  search: string | null;
  status: string | null;
  extra: string | null;
  search_identifiers: boolean;
  search_translations_only: boolean;
  search_rejected_translations: boolean;
  search_match_case: boolean;
  search_match_whole_word: boolean;
  tag: string | null;
  author: string | null;
  time: string | null;
  reviewer: string | null;
  review_time: string | null;
  exclude_self_reviewed: boolean;
};

const emptyParams = {
  list: null,
  search: null,
  status: null,
  extra: null,
  search_identifiers: false,
  search_translations_only: false,
  search_rejected_translations: false,
  search_match_case: false,
  search_match_whole_word: false,
  tag: null,
  author: null,
  time: null,
  reviewer: null,
  review_time: null,
  exclude_self_reviewed: false,
};

export const Location = createContext<Location>({
  push: () => {},
  replace: () => {},
  locale: '',
  project: '',
  resource: '',
  entity: 0,
  ...emptyParams,
});

export function LocationProvider({
  children,
  history,
}: {
  children: React.ReactElement;
  history: History.History;
}) {
  const [state, setState] = useState(() => parse(history, history.location));

  useLayoutEffect(() => {
    // TODO: API changes in history@5
    history.listen((location) => setState(parse(history, location)));
  }, [history]);

  return <Location.Provider value={state}>{children}</Location.Provider>;
}

function parse(
  history: History.History,
  { pathname, search }: History.Location,
): Location {
  const [locale, project, ...resource] = pathname.split('/').filter(Boolean);
  const params = new URLSearchParams(search);
  const common = {
    push: (next: string | Partial<Location>) =>
      history.push(stringify(location, next)),
    replace: (next: string | Partial<Location>) =>
      history.replace(stringify(location, next)),
    locale: locale ?? '',
    project: project ?? '',
    resource: resource.join('/'),
    entity: Number(params.get('string')),
  };
  const list = params.get('list');
  const location: Location = list
    ? { ...common, ...emptyParams, list: list.split(',').map(Number) }
    : {
        ...common,
        search: params.get('search'),
        status: params.get('status'),
        extra: params.get('extra'),
        search_identifiers: params.has('search_identifiers'),
        search_translations_only: params.has('search_translations_only'),
        search_rejected_translations: params.has(
          'search_rejected_translations',
        ),
        search_match_case: params.has('search_match_case'),
        search_match_whole_word: params.has('search_match_whole_word'),
        tag: params.get('tag'),
        author: params.get('author'),
        time: params.get('time'),
        reviewer: params.get('reviewer'),
        review_time: params.get('review_time'),
        exclude_self_reviewed: params.has('exclude_self_reviewed'),
        list: null,
      };
  return location;
}

function stringify(prev: Location, next: string | Partial<Location>) {
  if (typeof next === 'string') {
    return next;
  }

  const locale = next.locale || prev.locale;
  const project = next.project || prev.project;
  const resource = next.resource || prev.resource;
  const pathname = `/${locale}/${project}/${resource}/`;

  const params = new URLSearchParams();
  if (next.list) {
    params.set('list', next.list.join(','));
  } else {
    let keepList = !('list' in next);
    for (const key of [
      'search',
      'status',
      'extra',
      'search_identifiers',
      'search_translations_only',
      'search_rejected_translations',
      'search_match_case',
      'search_match_whole_word',
      'tag',
      'author',
      'time',
      'reviewer',
      'review_time',
      'exclude_self_reviewed',
    ] as const) {
      const value = key in next ? next[key] : prev[key];
      if (value) {
        params.set(key, String(value));
        keepList &&= false;
      }
    }
    if (keepList && prev.list) {
      params.set('list', prev.list.join(','));
    }
  }
  const entity = 'entity' in next ? next.entity : prev.entity;
  if (entity) {
    params.set('string', String(entity));
  }

  const ps = String(params).replace(/%2C/g, ',');
  return ps ? `${pathname}?${ps}` : pathname;
}

type LinkProps = Omit<
  React.AnchorHTMLAttributes<HTMLAnchorElement>,
  'href' | 'onClick'
> & {
  to: Partial<Location>;
};

export function Link({
  to,
  ...props
}: LinkProps): React.ReactElement<HTMLAnchorElement> {
  const location = useContext(Location);
  const { push, locale, project, resource } = location;
  const next: Partial<Location> = {
    locale,
    project,
    resource,
    entity: 0,
    ...emptyParams,
    ...to,
  };
  return (
    <a
      {...props}
      href={stringify(location, next)}
      onClick={(ev) => {
        ev.preventDefault();
        push(next);
      }}
    />
  );
}
