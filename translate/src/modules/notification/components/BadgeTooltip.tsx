import classNames from 'classnames';
import React, { useCallback, useContext } from 'react';
import {
  BadgeTooltipMessage,
  ShowBadgeTooltip,
} from '~/context/BadgeNotification';
import { useAppSelector } from '~/hooks';
import { Localized } from '@fluent/react';
import Fireworks from 'react-canvas-confetti/dist/presets/fireworks';

import './BadgeTooltip.css';

export function BadgeTooltip(): React.ReactElement<'div'> {
  const tooltip = useContext(BadgeTooltipMessage);
  if (!tooltip) return <></>;
  const { badgeName, badgeLevel } = tooltip;
  const showBadgeTooltip = useContext(ShowBadgeTooltip);

  const hide = useCallback(() => {
    showBadgeTooltip(null);
  }, []);

  const className = classNames('badge-tooltip', tooltip && 'showing');

  let imagePath;
  switch (badgeName) {
    case 'Review Master':
      imagePath = '../images/review_master_badge.svg';
      break;
    case 'Translation Champion':
      imagePath = '../images/translation_champion_badge.svg';
      break;
    default:
      imagePath = '';
  }

  const user = useAppSelector((state) => state.user);

  return (
    <>
      <Fireworks autorun={{ speed: 1, duration: 3000 }} />
      <div className={className}>
        <button onClick={hide}> X </button>

        <Localized id='editor-BadgeTooltip--intro'>
          <p>New badge level gained!</p>
        </Localized>

        <Localized
          id='editor-BadgeTooltip--info'
          vars={{ badgeLevel: badgeLevel ?? 0, badgeName: badgeName ?? '' }}
        >
          <p>
            {badgeName} Badge level gained: Level {badgeLevel}
          </p>
        </Localized>

        <img className='badge' src={imagePath}></img>

        <Localized
          id='editor-BadgeTooltip--profile'
          elems={{ a: <a href={`/contributors/${user}`} /> }}
        >
          <p>{'You can view your new badge on your <a>profile page</a>.'}</p>
        </Localized>
      </div>
    </>
  );
}
