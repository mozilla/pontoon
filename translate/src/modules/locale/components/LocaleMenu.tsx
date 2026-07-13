import React, { useState, useRef, useEffect } from 'react';
import './LocaleMenu.css';
import LocaleItem from './LocaleItem';
import { LocaleOption } from '~/api/other-locales';

type Props = {
  locales: LocaleOption[];
  currentLocale: string;
  selected: string;
  onSelect: (code: string) => void;
};

export default function LocaleMenu({
  locales,
  currentLocale,
  selected,
  onSelect,
}: Props) {
  const [isOpen, setIsOpen] = useState(false);
  const [search, setSearch] = useState('');
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (ref.current && !ref.current.contains(e.target as Node)) {
        setIsOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const filtered = locales
    .filter((locale) => locale.code !== currentLocale)
    .filter(
      (locale) =>
        locale.name.toLowerCase().includes(search.toLowerCase()) ||
        locale.code.toLowerCase().includes(search.toLowerCase()),
    )
    .sort((a, b) => a.name.localeCompare(b.name));

  const selectedLocale = locales.find((locale) => locale.code === selected);

  return (
    <div className='locale-menu' ref={ref}>
      <button
        type='button'
        className={`locale-menu-trigger ${selectedLocale ? 'has-selection' : ''} ${isOpen ? 'is-open' : ''}`}
        onClick={() => setIsOpen((o) => !o)}
        disabled={locales.length === 0}
      >
        {selectedLocale ? (
          <>
            <span className='locale-name'>{selectedLocale.name}</span>
            <span className='locale-code'>{selectedLocale.code}</span>
          </>
        ) : (
          <span className='locale-placeholder'>SOURCE LOCALE</span>
        )}
        {!selectedLocale && <span className='locale-menu-arrow' />}
      </button>
      {isOpen && (
        <div className='locale-menu-dropdown'>
          <div className='locale-menu-search'>
            <i className='icon fas fa-search'></i>
            <input
              type='search'
              autoFocus
              placeholder=''
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
          </div>
          <div className='locale-menu-list'>
            <ul>
              <li
                key='source'
                className={`locale-item ${selected === '' ? 'selected' : ''}`}
                onClick={() => {
                  onSelect('');
                  setIsOpen(false);
                  setSearch('');
                }}
              >
                <span className='locale-name'>Source Locale</span>
              </li>
              {filtered.map((locale) => (
                <LocaleItem
                  key='source'
                  locale={locale}
                  currentLocale={currentLocale}
                  selected={locale.code === currentLocale}
                  onClick={() => {
                    onSelect(locale.code);
                    setIsOpen(false);
                    setSearch('');
                  }}
                />
              ))}
            </ul>
          </div>
        </div>
      )}
    </div>
  );
}
