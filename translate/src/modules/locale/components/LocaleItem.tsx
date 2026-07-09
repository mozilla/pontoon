import React from 'react';
import './LocaleItem.css';
import { LocaleOption } from '~/api/other-locales';

/**
 *
 * Render a locale item.
 */
type Props = {
  locale: LocaleOption;
  currentLocale: string;
  selected: boolean;
  onClick: () => void;
};

export default function LocaleItem({ locale, selected, onClick }: Props) {
  return (
    <li
      className={`locale-item ${selected ? 'selected' : ''}`}
      onClick={onClick}
    >
      <span className='locale-name'>{locale.name}</span>
      <span className='locale-code'>{locale.code}</span>
    </li>
  );
}
