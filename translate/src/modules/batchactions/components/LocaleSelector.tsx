import React, { useState, useRef, useEffect } from 'react';
import { LocaleOption } from '~/api/other-locales';

type Props = {
  locales: LocaleOption[];
  currentLocale: string;
  selected: string;
  onSelect: (code: string) => void;
};

export default function LocaleSelector({
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
    <div className='locale-selector' ref={ref}>
      <button
        type='button'
        className={`locale-selector-trigger ${selectedLocale ? 'has-selection' : ''} ${isOpen ? 'is-open' : ''}`}
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
        {!selectedLocale && <span className='locale-selector-arrow' />}
      </button>

      {isOpen && (
        <div className='locale-selector-dropdown'>
          <div className='locale-selector-search'>
            <i className='icon fas fa-search'></i>
            <input
              type='search'
              autoFocus
              placeholder=''
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
          </div>
          <div className='locale-selector-list'>
            <ul>
              <li
                key='source'
                className={selected === '' ? 'selected' : ''}
                onClick={() => {
                  onSelect('');
                  setIsOpen(false);
                  setSearch('');
                }}
              >
                <span className='locale-name'>Source Locale</span>
              </li>
              {filtered.map(({ code, name }) => (
                <li
                  key={code}
                  className={code === selected ? 'selected' : ''}
                  onClick={() => {
                    onSelect(code);
                    setIsOpen(false);
                    setSearch('');
                  }}
                >
                  <span className='locale-name'>{name}</span>
                  <span className='locale-code'>{code}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>
      )}
    </div>
  );
}
