import React from 'react';

import * as api from '~/api/uxaction';
import {
  UserNotificationsMenu,
  UserNotificationsMenuDialog,
} from './UserNotificationsMenu';
import { expect, vi } from 'vitest';
import { fireEvent, render } from '@testing-library/react';
import { MockLocalizationProvider } from '../../../test/utils';

const WrapUserNotificationsMenuDialog = (props) => {
  return (
    <MockLocalizationProvider>
      <UserNotificationsMenuDialog {...props} />
    </MockLocalizationProvider>
  );
};
const noNotificationText = 'No new notifications.';

describe('<UserNotificationsMenuDialog>', () => {
  it('shows empty notifications menu if user has no notifications', () => {
    const notifications = [];
    const { container, getByText } = render(
      <WrapUserNotificationsMenuDialog notifications={notifications} />,
    );

    expect(
      container.querySelector('.notification-list .user-notification'),
    ).toBeNull();
    getByText(noNotificationText);
  });

  it('shows a notification in the notifications menu', () => {
    const notifications = [
      {
        id: 0,
        level: 'level',
        unread: false,
        description: 'description',
        verb: 'verb',
        date: 'Thursday, January 31, 2019 at 10:20 UTC',
        date_iso: '2019-01-31T10:20:00+00:00',
        actor: {
          anchor: 'actor_anchor',
          url: 'actor_url',
        },
        target: {
          anchor: 'target_anchor',
          url: 'target_url',
        },
      },
    ];

    const { container, queryByText } = render(
      <WrapUserNotificationsMenuDialog notifications={notifications} />,
    );

    expect(queryByText(noNotificationText)).toBeNull();
    expect(
      container.querySelectorAll('.notification-list .user-notification'),
    ).toHaveLength(1);
  });
});

describe('<UserNotificationsMenu>', () => {
  beforeEach(() => vi.spyOn(api, 'logUXAction'));
  afterEach(() => vi.restoreAllMocks());

  it('hides the notifications icon when the user is logged out', () => {
    const user = {
      isAuthenticated: false,
      notifications: {
        has_unread: false,
      },
    };
    const { container } = render(<UserNotificationsMenu user={user} />);

    expect(container).toBeEmptyDOMElement();
  });

  it('shows the notifications icon when the user is logged in', () => {
    const user = {
      isAuthenticated: true,
      notifications: {
        notifications: [],
      },
    };
    const { container } = render(<UserNotificationsMenu user={user} />);

    expect(
      container.querySelector('.user-notifications-menu'),
    ).toBeInTheDocument();
  });

  it('shows the notifications badge when the user has unread notifications and call logUxAction', () => {
    const user = {
      isAuthenticated: true,
      notifications: {
        has_unread: true,
        notifications: [],
        unread_count: '5',
      },
    };
    const { container } = render(<UserNotificationsMenu user={user} />);

    expect(
      container.querySelector('.user-notifications-menu .badge'),
    ).toHaveTextContent('5');
    expect(api.logUXAction).toHaveBeenCalled();
  });

  it('calls the logUxAction function on click on the icon if menu not visible', () => {
    const markAllNotificationsAsRead = vi.fn();
    const user = {
      isAuthenticated: true,
      notifications: {
        has_unread: true,
        notifications: [],
      },
    };
    const { getByRole } = render(
      <MockLocalizationProvider>
        <UserNotificationsMenu
          markAllNotificationsAsRead={markAllNotificationsAsRead}
          user={user}
        />
      </MockLocalizationProvider>,
    );

    //useEffect calls the function once
    expect(api.logUXAction).toHaveBeenCalledOnce();

    fireEvent.click(getByRole('button'));
    expect(api.logUXAction).toHaveBeenCalledTimes(2);

    fireEvent.click(getByRole('button'));
    expect(api.logUXAction).toHaveBeenCalledTimes(2);
  });
});
