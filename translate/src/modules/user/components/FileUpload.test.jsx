import React from 'react';
import { fireEvent, render, waitFor } from '@testing-library/react';
import { Provider } from 'react-redux';
import { vi } from 'vitest';

import * as Upload from '~/api/upload';
import { ShowBadgeTooltip } from '~/context/BadgeTooltip';
import { ShowNotification } from '~/context/Notification';
import { RESET_ENTITIES } from '~/modules/entities/actions';
import { createReduxStore } from '~/test/store';
import { MockLocalizationProvider } from '~/test/utils';

import { FileUpload } from './FileUpload';

const LOCATION = { locale: 'my', project: 'proj', resource: 'res.po' };

function mountFileUpload() {
  const showNotification = vi.fn();
  const showBadgeTooltip = vi.fn();
  const store = createReduxStore();
  const dispatch = vi.spyOn(store, 'dispatch');

  const { container } = render(
    <Provider store={store}>
      <MockLocalizationProvider>
        <ShowNotification.Provider value={showNotification}>
          <ShowBadgeTooltip.Provider value={showBadgeTooltip}>
            <FileUpload parameters={LOCATION} />
          </ShowBadgeTooltip.Provider>
        </ShowNotification.Provider>
      </MockLocalizationProvider>
    </Provider>,
  );

  const select = () =>
    fireEvent.change(container.querySelector('input[type="file"]'), {
      target: { files: [new File(['msgid ""'], 'res.po')] },
    });

  return { dispatch, select, showBadgeTooltip, showNotification };
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
