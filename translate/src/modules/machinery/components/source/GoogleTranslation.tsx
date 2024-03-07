import React, { useState, useRef } from 'react';
import { Localized } from '@fluent/react';
import './dropdown.css';

/**
 * Show the translation source from Google Translate.
 */

export function GoogleTranslation(): React.ReactElement<'li'> {
  const [isDropdownOpen, setDropdownOpen] = useState(false);
  const [selectedOption, setSelectedOption] = useState('');
  const dropdownRef = useRef<HTMLLIElement>(null); // Ref to the dropdown container

  const toggleDropdown = (ev: React.MouseEvent) => {
    ev.stopPropagation();
    setDropdownOpen((isDropdownOpen) => !isDropdownOpen);
  };

  const handleOptionClick = (ev: React.MouseEvent, option: string) => {
    ev.stopPropagation();
    setSelectedOption(option);
    console.log(option);
    setDropdownOpen(false); // Close the dropdown after selection
  };

  return (
    <li ref={dropdownRef} className='google-translation'>
      <Localized
        id='machinery-GoogleTranslation--visit-google'
        attrs={{ title: true }}
      >
        <a
          className='translation-source'
          title='Toggle dropdown'
          onClick={toggleDropdown}
        >
          <span>GOOGLE TRANSLATE</span>
          <span className='selected-option'>
            TEST {selectedOption.toUpperCase()}
          </span>
        </a>
      </Localized>
      <button
        onClick={toggleDropdown}
        className='dropdown-toggle'
        aria-haspopup='true'
        aria-expanded={isDropdownOpen}
      >
        {isDropdownOpen ? '▲' : '▼'}
      </button>
      {isDropdownOpen && (
        <ul className='dropdown-menu' style={{ display: 'block' }}>
          <li onClick={(ev) => handleOptionClick(ev, 'Rephrase')}>REPHRASE</li>
          <li onClick={(ev) => handleOptionClick(ev, 'Make formal')}>
            MAKE FORMAL
          </li>
          <li onClick={(ev) => handleOptionClick(ev, 'Make informal')}>
            MAKE INFORMAL
          </li>
        </ul>
      )}
    </li>
  );
}
