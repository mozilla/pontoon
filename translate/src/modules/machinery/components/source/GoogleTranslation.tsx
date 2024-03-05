import React, { useState, useRef, useEffect } from 'react';
import { Localized } from '@fluent/react';
import './dropdown.css'; 

export function GoogleTranslation(): React.ReactElement<'li'> {
  const [isDropdownOpen, setDropdownOpen] = useState(false);
  const [selectedOption, setSelectedOption] = useState('');
  const dropdownRef = useRef<HTMLLIElement>(null); // Ref to the dropdown container

  const toggleDropdown = () => {
    console.log("toggleDropdown called");
    setDropdownOpen(!isDropdownOpen);
    console.log(isDropdownOpen);
  };

  const handleOptionClick = (option: string) => {
    setSelectedOption(option);
    setDropdownOpen(false); // Close the dropdown after selection
  };

  // This effect handles closing the dropdown when clicking outside of it
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setDropdownOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [isDropdownOpen]);

  return (
    <li ref={dropdownRef} className="google-translation">
      <Localized id='machinery-GoogleTranslation--visit-google' attrs={{ title: true }}>
        <a
          className='translation-source'
          href='https://translate.google.com/'
          title='Visit Google Translate'
          target='_blank'
          rel='noopener noreferrer'
          onClick={(e: React.MouseEvent) => e.stopPropagation()}
        >
          <span>GOOGLE TRANSLATE</span>
          {selectedOption && <span className="selected-option"> {selectedOption.toUpperCase()}</span>}
        </a>
      </Localized>
      <button onClick={toggleDropdown} className="dropdown-toggle" aria-haspopup="true" aria-expanded={isDropdownOpen}>
        {isDropdownOpen ? '▲' : '▼'}
      </button>
      {isDropdownOpen && (
        <ul className="dropdown-menu">
          <li onClick={() => handleOptionClick('Rephrase')}>REPHRASE</li>
          <li onClick={() => handleOptionClick('Make formal')}>MAKE FORMAL</li>
          <li onClick={() => handleOptionClick('Make informal')}>MAKE INFORMAL</li>
        </ul>
      )}
    </li>
  );
}
