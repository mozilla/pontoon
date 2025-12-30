import React, { useState } from 'react';
import { render, act, fireEvent } from '@testing-library/react';
import { vi } from 'vitest';

import { NotificationMessage, ShowNotification } from '~/context/Notification';
import { NotificationPanel } from './NotificationPanel';

const NOTIF = { type: 'info', content: 'Hello, World!' };

function ComponentWithProvider({ initialMessage }) {
  const [internalMessage, setInternalMessage] = useState(initialMessage);
  return (
    <NotificationMessage.Provider value={internalMessage}>
      <ShowNotification.Provider value={setInternalMessage}>
        <NotificationPanel />
      </ShowNotification.Provider>
    </NotificationMessage.Provider>
  );
}

describe('<NotificationPanel>', () => {
  afterEach(() => {
    vi.useRealTimers();
    vi.restoreAllMocks();
  });

  it('returns an empty element when there is no notification', () => {
    const { container } = render(
      <ComponentWithProvider initialMessage={null} />,
    );

    expect(container.firstChild.childNodes.length).toBe(1);
    expect(container.querySelector('span').textContent).toBe('');
  });

  it('shows a message when there is a notification', () => {
    const { container } = render(
      <ComponentWithProvider initialMessage={NOTIF} />,
    );

    expect(container.querySelector('span').textContent).toEqual(NOTIF.content);
    expect(container.querySelectorAll('.showing')).toHaveLength(1);
  });

  it('hides a message after a delay', () => {
    vi.useFakeTimers();
    const { container } = render(
      <ComponentWithProvider initialMessage={NOTIF} />,
    );

    // Run time forward, the message with disappear.
    vi.runAllTimers()

    expect(container.childNodes).toHaveLength(1);
    expect(container.querySelectorAll('.showing')).toHaveLength(0);
  });

  it('hides a message on click', () => {
    const { container } = render(
      <ComponentWithProvider initialMessage={NOTIF} />,
    );

    expect(container.querySelectorAll('.showing')).toHaveLength(1);

    act(() => {
      fireEvent.click(container.firstElementChild);
    });

    expect(container.querySelectorAll('.showing')).toHaveLength(0);
  });
});
