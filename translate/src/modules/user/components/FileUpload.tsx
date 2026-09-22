import { Localized } from '@fluent/react';
import NProgress from 'nprogress';
import React, { useContext } from 'react';

import { uploadTranslations } from '~/api/upload';
import type { UploadTranslationsResult } from '~/api/upload';
import { ShowBadgeTooltip } from '~/context/BadgeTooltip';
import type { Location } from '~/context/Location';
import type { NotificationMessage } from '~/context/Notification';
import { ShowNotification } from '~/context/Notification';
import { UnsavedActions, UnsavedChanges } from '~/context/UnsavedChanges';
import { useAppDispatch } from '~/hooks';
import { resetEntities } from '~/modules/entities/actions';

import './FileUpload.css';

type Props = {
  parameters: Location;
  uploading: boolean;
  setUploading: (uploading: boolean) => void;
};

/** Show upload summaries for longer than a standard status message (2s),
 * since they carry more information. */
const UPLOAD_MESSAGE_DURATION = 6000;

function summary(result: UploadTranslationsResult): NotificationMessage {
  const { updated, unchanged, undefined_keys_count: notFound } = result;
  const vars = { updated, unchanged, notFound };
  return {
    type: updated ? 'success' : 'info',
    duration: UPLOAD_MESSAGE_DURATION,
    content: notFound ? (
      <Localized id='user-FileUpload--upload-summary-not-found' vars={vars}>
        <span>
          {`Translations uploaded: ${updated} updated, ${unchanged} unchanged, ${notFound} not found in Pontoon.`}
        </span>
      </Localized>
    ) : (
      <Localized id='user-FileUpload--upload-summary' vars={vars}>
        <span>
          {`Translations uploaded: ${updated} updated, ${unchanged} unchanged.`}
        </span>
      </Localized>
    ),
  };
}

function failure(status: number, error: string | undefined) {
  let content: React.ReactElement;
  switch (status) {
    case 400:
      // Reported by the server with the detail of the issues found in the file.
      content = error ? (
        <span>{error}</span>
      ) : (
        <Localized id='user-FileUpload--upload-invalid'>
          <span>{'Upload failed: the file could not be used.'}</span>
        </Localized>
      );
      break;
    case 403:
      content = (
        <Localized id='user-FileUpload--upload-forbidden'>
          <span>{'You don’t have permission to upload files.'}</span>
        </Localized>
      );
      break;
    case 409:
      content = (
        <Localized id='user-FileUpload--upload-conflict'>
          <span>
            {
              'Upload failed: someone else changed the same translations. Please try again.'
            }
          </span>
        </Localized>
      );
      break;
    case 429:
      content = (
        <Localized id='user-FileUpload--upload-throttled'>
          <span>{'Too many uploads. Please wait a while and try again.'}</span>
        </Localized>
      );
      break;
    default:
      content = (
        <Localized id='user-FileUpload--upload-error'>
          <span>{'Upload failed. Please try again.'}</span>
        </Localized>
      );
  }
  return {
    type: 'error',
    duration: UPLOAD_MESSAGE_DURATION,
    content,
  } as const;
}

/*
 * Render a File Upload button.
 */
export function FileUpload({
  parameters,
  uploading,
  setUploading,
}: Props): React.ReactElement<'div'> {
  const dispatch = useAppDispatch();
  const showNotification = useContext(ShowNotification);
  const showBadgeTooltip = useContext(ShowBadgeTooltip);
  const { checkUnsavedChanges, setUnsavedChanges } = useContext(UnsavedActions);
  const { check } = useContext(UnsavedChanges);

  const uploadFile = async (file: File) => {
    setUploading(true);
    NProgress.start();
    try {
      const { status, result, error } = await uploadTranslations(
        parameters.locale,
        parameters.project,
        parameters.resource,
        file,
      );

      if (!result) {
        showNotification(failure(status, error));
        return;
      }

      showNotification(summary(result));

      const badge = result.badge_updates?.[0];
      if (badge) {
        showBadgeTooltip({ badgeName: badge.name, badgeLevel: badge.level });
      }

      if (result.updated) {
        // The list and the editor still show the translations from before
        // the upload, so start it over.
        dispatch(resetEntities());
      }
    } finally {
      setUploading(false);
      NProgress.done();
    }
  };

  const upload = (ev: React.ChangeEvent<HTMLInputElement>) => {
    const file = ev.currentTarget.files?.[0];
    // Let the same file be picked again, e.g. after fixing it.
    ev.currentTarget.value = '';
    if (!file || uploading) {
      return;
    }
    // Save this before confirmation clears the unsaved state.
    const hadUnsavedChanges = check();
    checkUnsavedChanges(() => {
      if (hadUnsavedChanges) {
        // The draft is still in the editor, so keep protecting it. Restored
        // here rather than after the upload, so that an edit mid-upload is
        // preserved.
        setUnsavedChanges(() => true);
      }
      void uploadFile(file);
    });
  };

  return (
    <div className='file-upload'>
      <label>
        <Localized
          id='user-UserMenu--upload-translations'
          elems={{
            glyph: <i className='fas fa-cloud-upload-alt fa-fw' />,
          }}
        >
          <span>{'<glyph></glyph>Upload Translations'}</span>
        </Localized>
        <input
          name='uploadfile'
          type='file'
          disabled={uploading}
          onChange={upload}
        />
      </label>
    </div>
  );
}
