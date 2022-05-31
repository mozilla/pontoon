import { Localized } from '@fluent/react';
import React, { useCallback, useRef } from 'react';

import type { Location } from '~/context/Location';

import './FileUpload.css';

type Props = {
  parameters: Location;
};

/*
 * Render a File Upload button.
 */
export function FileUpload({ parameters }: Props): React.ReactElement<'form'> {
  const uploadForm = useRef<HTMLFormElement>(null);

  const submitForm = useCallback(() => {
    uploadForm.current?.submit();
  }, []);

  /* TODO: Refactor core.api.base and reuse getCSRFToken() here */
  const rootElt = document.getElementById('root');
  const csrfToken = rootElt?.dataset.csrfToken ?? '';

  return (
    <form
      action='/upload/'
      className='file-upload'
      encType='multipart/form-data'
      method='POST'
      ref={uploadForm}
    >
      <input name='csrfmiddlewaretoken' type='hidden' value={csrfToken} />
      <input name='code' type='hidden' value={parameters.locale} />
      <input name='slug' type='hidden' value={parameters.project} />
      <input name='part' type='hidden' value={parameters.resource} />
      <label>
        <Localized
          id='user-UserMenu--upload-translations'
          elems={{
            glyph: <i className='fa fa-cloud-upload-alt fa-fw' />,
          }}
        >
          <span>{'<glyph></glyph>Upload Translations'}</span>
        </Localized>
        <input name='uploadfile' type='file' onChange={submitForm} />
      </label>
    </form>
  );
}
