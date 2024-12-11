import classNames from 'classnames';
import React, { useCallback, useContext, useRef } from 'react';
import { Localized } from '@fluent/react';
import Pride from 'react-canvas-confetti/dist/presets/pride';

import { BadgeTooltipMessage, ShowBadgeTooltip } from '~/context/BadgeTooltip';
import { useAppSelector } from '~/hooks';
import { useOnDiscard } from '~/utils';

import './BadgeTooltip.css';

export function BadgeTooltip(): React.ReactElement<'div'> | null {
  const user = useAppSelector((state) => state.user.username);
  const tooltip = useContext(BadgeTooltipMessage);
  const showBadgeTooltip = useContext(ShowBadgeTooltip);
  const ref = useRef<HTMLDivElement>(null);
  const style = getComputedStyle(document.body);

  const hide = useCallback(() => {
    showBadgeTooltip(null);
  }, [showBadgeTooltip]);

  useOnDiscard(ref, hide);

  if (!tooltip) return null;

  const { badgeName, badgeLevel } = tooltip;
  const className = classNames('badge-tooltip', tooltip && 'showing');

  let imagePath: string;
  let confettiColor: string;
  switch (badgeName) {
    case 'Review Master':
      imagePath = '/static/img/review_master_badge.svg';
      confettiColor = style.getPropertyValue('--status-unreviewed');
      break;
    case 'Translation Champion':
      imagePath = '/static/img/translation_champion_badge.svg';
      confettiColor = style.getPropertyValue('--status-translated');
      break;
    default:
      return null;
  }

  const decorateOptions = (defaultOptions: any) => {
    return {
      ...defaultOptions,
      disableForReducedMotion: true,
      colors: [confettiColor, style.getPropertyValue('--tooltip-background')],
      particleCount: 10,
      spread: 55,
      zIndex: 100,
    };
  };

  return (
    <div ref={ref} className={className}>
      <Pride
        autorun={{ speed: 30, duration: 5000 }}
        decorateOptions={decorateOptions}
      />

      <Localized id='editor-BadgeTooltip--intro'>
        <p className='title'>Achievement unlocked</p>
      </Localized>

      <img className='badge' src={imagePath} />

      <p className='badge-name'>{badgeName}</p>

      <Localized
        id='editor-BadgeTooltip--level'
        vars={{ badgeLevel: badgeLevel ?? 0 }}
      >
        <p className='badge-level'>Level {badgeLevel}</p>
      </Localized>

      <Localized
        id='editor-BadgeTooltip--profile'
        elems={{ a: <a href={`/contributors/${user}`} /> }}
      >
        <p className='notice'>
          {'View your new badge in your <a>profile</a>.'}
        </p>
      </Localized>

      <Localized id='editor-BadgeTooltip--continue'>
        <button className='continue' onClick={hide}>
          Continue
        </button>
      </Localized>
    </div>
  );
}
