import React, { useState } from 'react';
import { fireEvent, render, waitFor } from '@testing-library/react';
import NProgress from 'nprogress';
import { Provider } from 'react-redux';
import { vi } from 'vitest';

import * as Upload from '~/api/upload';
import { ShowBadgeTooltip } from '~/context/BadgeTooltip';
import { ShowNotification } from '~/context/Notification';
import { UnsavedActions, UnsavedChanges } from '~/context/UnsavedChanges';
import { RESET_ENTITIES } from '~/modules/entities/actions';
import { createReduxStore } from '~/test/store';
import { MockLocalizationProvider } from '~/test/utils';

import { FileUpload } from './FileUpload';

const LOCATION = { locale: 'my', project: 'proj', resource: 'res.po' };

function StatefulFileUpload() {
  const [uploading, setUploading] = useState(false);
  return (
    <FileUpload
      parameters={LOCATION}
      uploading={uploading}
      setUploading={setUploading}
    />
  );
}

function mountFileUpload({ hasUnsavedChanges = false, confirm = true } = {}) {
  const showNotification = vi.fn();
  const showBadgeTooltip = vi.fn();
  const store = createReduxStore();
  const dispatch = vi.spyOn(store, 'dispatch');

  const setUnsavedChanges = vi.fn();
  const actions = {
    // Mimic the popup being confirmed or dismissed.
    checkUnsavedChanges: (callback) => {
      if (confirm) {
        callback();
      }
    },
    resetUnsavedChanges: () => {},
    setUnsavedChanges,
  };

  const { container } = render(
    <Provider store={store}>
      <MockLocalizationProvider>
        <ShowNotification.Provider value={showNotification}>
          <ShowBadgeTooltip.Provider value={showBadgeTooltip}>
            <UnsavedChanges.Provider
              value={{ check: () => hasUnsavedChanges, onIgnore: null }}
            >
              <UnsavedActions.Provider value={actions}>
                <StatefulFileUpload />
              </UnsavedActions.Provider>
            </UnsavedChanges.Provider>
          </ShowBadgeTooltip.Provider>
        </ShowNotification.Provider>
      </MockLocalizationProvider>
    </Provider>,
  );

  const input = container.querySelector('input[type="file"]');
  const select = () =>
    fireEvent.change(input, {
      target: { files: [new File(['msgid ""'], 'res.po')] },
    });

  return {
    dispatch,
    input,
    select,
    setUnsavedChanges,
    showBadgeTooltip,
    showNotification,
  };
}

/** Wait for the notification of a completed upload, and return it. */
async function notification(showNotification) {
  await waitFor(() => expect(showNotification).toHaveBeenCalled());
  return showNotification.mock.calls[0][0];
}

describe('<FileUpload>', () => {
  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('uploads the selected file for the current location', async () => {
    const uploadTranslations = vi
      .spyOn(Upload, 'uploadTranslations')
      .mockResolvedValue({
        status: 200,
        result: { updated: 2, unchanged: 1, undefined_keys_count: 0 },
      });
    const { select, showNotification } = mountFileUpload();

    select();

    await notification(showNotification);
    const [locale, project, resource, file] = uploadTranslations.mock.calls[0];
    expect([locale, project, resource]).toEqual(['my', 'proj', 'res.po']);
    expect(file.name).toBe('res.po');
  });

  it('reports a successful upload and reloads the entities', async () => {
    vi.spyOn(Upload, 'uploadTranslations').mockResolvedValue({
      status: 200,
      result: { updated: 2, unchanged: 1, undefined_keys_count: 0 },
    });
    const { dispatch, select, showNotification } = mountFileUpload();

    select();

    const message = await notification(showNotification);
    expect(message.type).toBe('success');
    expect(message.content.props.id).toBe('user-FileUpload--upload-summary');
    expect(dispatch).toHaveBeenCalledWith({ type: RESET_ENTITIES });
  });

  it('reports the keys that were not found', async () => {
    vi.spyOn(Upload, 'uploadTranslations').mockResolvedValue({
      status: 200,
      result: { updated: 1, unchanged: 0, undefined_keys_count: 3 },
    });
    const { select, showNotification } = mountFileUpload();

    select();

    const message = await notification(showNotification);
    expect(message.content.props.id).toBe(
      'user-FileUpload--upload-summary-not-found',
    );
    expect(message.content.props.vars.notFound).toBe(3);
  });

  it('does not reload the entities when nothing changed', async () => {
    vi.spyOn(Upload, 'uploadTranslations').mockResolvedValue({
      status: 200,
      result: { updated: 0, unchanged: 4, undefined_keys_count: 0 },
    });
    const { dispatch, select, showNotification } = mountFileUpload();

    select();

    const message = await notification(showNotification);
    expect(message.type).toBe('info');
    expect(dispatch).not.toHaveBeenCalledWith({ type: RESET_ENTITIES });
  });

  it('shows a tooltip for a badge level reached through the upload', async () => {
    vi.spyOn(Upload, 'uploadTranslations').mockResolvedValue({
      status: 200,
      result: {
        updated: 1,
        unchanged: 0,
        undefined_keys_count: 0,
        badge_updates: [{ name: 'Translation Champion', level: 1 }],
      },
    });
    const { select, showBadgeTooltip, showNotification } = mountFileUpload();

    select();

    await notification(showNotification);
    expect(showBadgeTooltip).toHaveBeenCalledWith({
      badgeName: 'Translation Champion',
      badgeLevel: 1,
    });
  });

  it.each([
    [403, 'user-FileUpload--upload-forbidden'],
    [409, 'user-FileUpload--upload-conflict'],
    [429, 'user-FileUpload--upload-throttled'],
    [500, 'user-FileUpload--upload-error'],
  ])('reports a %i response', async (status, id) => {
    vi.spyOn(Upload, 'uploadTranslations').mockResolvedValue({ status });
    const { dispatch, select, showNotification } = mountFileUpload();

    select();

    const message = await notification(showNotification);
    expect(message.type).toBe('error');
    expect(message.content.props.id).toBe(id);
    expect(dispatch).not.toHaveBeenCalledWith({ type: RESET_ENTITIES });
  });

  it('shows progress while the upload is running', async () => {
    const start = vi.spyOn(NProgress, 'start');
    const done = vi.spyOn(NProgress, 'done');
    vi.spyOn(Upload, 'uploadTranslations').mockResolvedValue({ status: 500 });
    const { select, showNotification } = mountFileUpload();

    select();

    expect(start).toHaveBeenCalled();
    await notification(showNotification);
    // Also cleared when the upload fails.
    expect(done).toHaveBeenCalled();
  });

  it('asks about unsaved changes before uploading', async () => {
    const uploadTranslations = vi.spyOn(Upload, 'uploadTranslations');
    const { select } = mountFileUpload({
      hasUnsavedChanges: true,
      confirm: false,
    });

    select();

    expect(uploadTranslations).not.toHaveBeenCalled();
  });

  it('keeps protecting the draft when the upload starts', async () => {
    vi.spyOn(Upload, 'uploadTranslations').mockResolvedValue({ status: 500 });
    const { select, setUnsavedChanges } = mountFileUpload({
      hasUnsavedChanges: true,
    });

    select();

    // Before the response, so that a later edit or entity change wins.
    expect(setUnsavedChanges).toHaveBeenCalledTimes(1);
    expect(setUnsavedChanges.mock.calls[0][0]()).toBe(true);
  });

  it('does not touch the unsaved changes once the upload is under way', async () => {
    vi.spyOn(Upload, 'uploadTranslations').mockResolvedValue({
      status: 200,
      result: { updated: 2, unchanged: 1, undefined_keys_count: 0 },
    });
    const { dispatch, select, setUnsavedChanges, showNotification } =
      mountFileUpload({ hasUnsavedChanges: true });

    select();

    await notification(showNotification);
    expect(dispatch).toHaveBeenCalledWith({ type: RESET_ENTITIES });
    expect(setUnsavedChanges).toHaveBeenCalledTimes(1);
  });

  it('does not touch the unsaved changes when there is no draft', async () => {
    vi.spyOn(Upload, 'uploadTranslations').mockResolvedValue({ status: 500 });
    const { select, setUnsavedChanges, showNotification } = mountFileUpload();

    select();

    await notification(showNotification);
    expect(setUnsavedChanges).not.toHaveBeenCalled();
  });

  it('shows the server message of a rejected file', async () => {
    vi.spyOn(Upload, 'uploadTranslations').mockResolvedValue({
      status: 400,
      error: 'Upload failed. File format not supported. Use res.po.',
    });
    const { select, showNotification } = mountFileUpload();

    select();

    const message = await notification(showNotification);
    expect(message.type).toBe('error');
    expect(message.content.props.children).toBe(
      'Upload failed. File format not supported. Use res.po.',
    );
  });
});
