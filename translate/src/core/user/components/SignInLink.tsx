import React from 'react';

type Props = {
  children?: React.ReactNode;
  url: string;
};

/*
 * Render a link to the Sign In process.
 */
export function SignInLink({ children, url }: Props): React.ReactElement<'a'> {
  const { origin, pathname, search } = window.location;
  const parsedUrl = new URL(url, origin);
  parsedUrl.searchParams.set('next', pathname + search);
  return <a href={parsedUrl.toString()}>{children}</a>;
}
