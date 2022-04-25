import type History from 'history';
import React, {
  createContext,
  useContext,
  useLayoutEffect,
  useState,
} from 'react';

export type LocationType = {
  push(location: string | Partial<LocationType>): void;
  replace(location: string | Partial<LocationType>): void;
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

const emptyParams = {
  entity: 0,
  search: null,
  status: null,
  extra: null,
  tag: null,
  author: null,
  time: null,
};

export const Location = createContext<LocationType>({
  push: () => {},
  replace: () => {},
  locale: '',
  project: '',
  resource: '',
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
): LocationType {
  const [locale, project, ...resource] = pathname.split('/').filter(Boolean);
  const params = new URLSearchParams(search);
  const location: LocationType = {
    push: (next) => history.push(stringify(location, next)),
    replace: (next) => history.replace(stringify(location, next)),
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
  return location;
}

function stringify(prev: LocationType, next: string | Partial<LocationType>) {
  if (typeof next === 'string') {
    return next;
  }

  const locale = next.locale || prev.locale;
  const project = next.project || prev.project;
  const resource = next.resource || prev.resource;
  const pathname = `/${locale}/${project}/${resource}/`;

  const params = new URLSearchParams();
  for (const key of [
    'search',
    'status',
    'extra',
    'tag',
    'author',
    'time',
    'entity',
  ] as const) {
    const value = key in next ? next[key] : prev[key];
    if (value) {
      params.set(key === 'entity' ? 'string' : key, String(value));
    }
  }

  const ps = params.toString();
  return ps ? `${pathname}?${ps}` : pathname;
}

type LinkProps = Omit<
  React.AnchorHTMLAttributes<HTMLAnchorElement>,
  'href' | 'onClick'
> & {
  to: Partial<LocationType>;
};

export function Link({
  to,
  ...props
}: LinkProps): React.ReactElement<HTMLAnchorElement> {
  const location = useContext(Location);
  const { push, locale, project, resource } = location;
  const next: Partial<LocationType> = {
    locale,
    project,
    resource,
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
