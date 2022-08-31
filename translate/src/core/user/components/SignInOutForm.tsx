import React from 'react';

import { CSRFToken } from '~/core/utils';

type Props = {
  children?: React.ReactNode;
  url: string;
};

/*
 * Render a form for the Sign In and Sign Out process.
 */
export function SignInOutForm({
  children,
  url,
}: Props): React.ReactElement<'form'> {
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
