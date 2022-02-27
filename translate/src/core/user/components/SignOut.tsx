import React from 'react';
import { Localized } from '@fluent/react';

type Props = {
  signOut: () => void;
};

/*
 * Render a Sign Out link.
 */
export function SignOut({ signOut }: Props): React.ReactElement {
  return (
    <Localized
      id='user-SignOut--sign-out'
      elems={{ glyph: <i className='fa fa-sign-out-alt fa-fw' /> }}
    >
      <button onClick={signOut}>{'<glyph></glyph>Sign out'}</button>
    </Localized>
  );
}
