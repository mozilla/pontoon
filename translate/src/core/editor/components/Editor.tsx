import React, { useContext, useEffect } from 'react';

import './Editor.css';

import { FluentEditor } from '~/modules/fluenteditor';
import { GenericEditor } from '~/modules/genericeditor';
import { useAppSelector } from '~/hooks';
import { UnsavedChanges } from '~/context/UnsavedChanges';

type Props = {
  fileFormat: string;
};

export function Editor({ fileFormat }: Props): React.ReactElement<'div'> {
  const { initialTranslation, translation } = useAppSelector(
    (state) => state.editor,
  );
  const { exist, show, set } = useContext(UnsavedChanges);

  // Changes in `translation` need to be reflected in `UnsavedChanges`,
  // but the latter needs to be defined at a higher level to make it
  // available in `EntitiesList`. Therefore, that state is managed here.
  useEffect(() => {
    let next: boolean;
    if (typeof translation === 'string') {
      next = translation !== initialTranslation;
    } else if (typeof initialTranslation === 'string') {
      next = false;
    } else {
      next = !translation.equals(initialTranslation);
    }

    if (next !== exist) {
      set({ exist: next, ignore: false });
    }
  }, [translation, initialTranslation, exist]);
  useEffect(() => {
    if (show) {
      set(null);
    }
  }, [translation]);

  return (
    <div className='editor'>
      {fileFormat === 'ftl' ? <FluentEditor /> : <GenericEditor />}
    </div>
  );
}
