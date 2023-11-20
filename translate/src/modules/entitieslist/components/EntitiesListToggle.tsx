import React from 'react';

import './EntitiesListToggle.css';

/**
 * Render entities list toggle.
 *
 * Used in a single-column layout.
 */
export function EntitiesListToggle(): React.ReactElement<'div'> {
  const toggleEntitiesList = () => {
    document
      .querySelector('#app > .main-content')
      .classList.toggle('entities-list');
  };

  return (
    <div className='entities-list-toggle' onClick={() => toggleEntitiesList()}>
      <div className='icon fa fa-bars'></div>
    </div>
  );
}
