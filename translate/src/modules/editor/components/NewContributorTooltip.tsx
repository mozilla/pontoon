import React, { useCallback, useContext, useRef, useState } from 'react';
import { Localized } from '@fluent/react';

import { useAppSelector } from '~/hooks';
import { useOnDiscard } from '~/utils';
import { EntityView } from '~/context/EntityView';
import { Locale } from '~/context/Locale';

import './NewContributorTooltip.css';

export function NewContributorTooltip(): React.ReactElement<'div'> | null {
  const [visible, setVisible] = useState(true);
  const handleDiscard = useCallback(() => setVisible(false), []);
  const ref = useRef(null);
  const locale = useContext(Locale);
  const user = useAppSelector((state) => state.user);
  const { entity } = useContext(EntityView);

  useOnDiscard(ref, handleDiscard);

  const show =
    visible &&
    !entity.readonly &&
    user.isAuthenticated &&
    !user.contributorForLocales.includes(locale.code);

  return show ? (
    <div ref={ref} className='new-contributor-tooltip'>
      <p className='title'>👋</p>

      <Localized id='editor-NewContributorTooltip--intro'>
        <p>It looks like you haven’t contributed to this locale yet.</p>
      </Localized>

      {locale.teamDescription && (
        <Localized
          id='editor-NewContributorTooltip--team-info'
          elems={{ a: <a href={`/${locale.code}/info/`} /> }}
        >
          <p>
            {
              'Check the <a>team information</a> before starting, as it might contain important information and language resources.'
            }
          </p>
        </Localized>
      )}

      <Localized
        id='editor-NewContributorTooltip--team-managers'
        elems={{ a: <a href={`/${locale.code}/contributors/`} /> }}
      >
        <p>
          {
            'Reach out to <a>team managers</a> if you have questions or want to learn more about contributing.'
          }
        </p>
      </Localized>
    </div>
  ) : null;
}
