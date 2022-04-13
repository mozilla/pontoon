import { Localized } from '@fluent/react';
import React from 'react';

import './SignIn.css';
import { SignInLink } from './SignInLink';

type Props = {
  url: string;
};

/*
 * Render a Sign In link styled as a button.
 */
export function SignIn({ url }: Props): React.ReactElement<'span'> {
  return (
    <span className='user-signin'>
      <Localized id='user-SignIn--sign-in'>
        <SignInLink url={url}>Sign in</SignInLink>
      </Localized>
    </span>
  );
}
