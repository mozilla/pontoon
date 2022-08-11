import React from 'react';

import { CSRFToken } from '~/core/utils';

type Props = {
  children?: React.ReactNode;
  url: string;
};

/*
 * Render a link to the Sign In process.
 */
export function SignInForm({ children, url }: Props): React.ReactElement<'a'> {
  const { origin, pathname, search } = window.location;

  const parsedUrl = new URL(url, origin);
  parsedUrl.searchParams.set('next', pathname + search);

  return (
    <form action={parsedUrl.toString()} method='post'>
      <CSRFToken />
      <button type='submit'>{children}</button>
    </form>
  );
}
