import { render, fireEvent } from '@testing-library/react';
import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import * as api from '~/api/uxaction';

import {
  UserNotificationsMenu,
  UserNotificationsMenuDialog,
} from './UserNotificationsMenu';

vi.mock('@fluent/react', async (importOriginal) => {
  const actual = await importOriginal();
  return {
    ...actual,
    Localized: ({ children }) => <>{children}</>,
  };
});
describe('<UserNotificationsMenuDialog>', () => {
  it('shows empty notifications menu if user has no notifications', () => {
    const notifications = [];
    render(<UserNotificationsMenuDialog notifications={notifications} />);

    expect(
      document.querySelectorAll('.notification-list .user-notification')
    ).toHaveLength(0);
    expect(
      document.querySelectorAll('.notification-list .no')
    ).toHaveLength(1);
  });

  it('shows a notification in the notifications menu', () => {
    const notifications = [
      {
        id: 0,
        level: 'level',
        unread: false,
        description: 'description',
        verb: 'verb',
        date: 'Jan 31, 2000 10:20',
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

    render(<UserNotificationsMenuDialog notifications={notifications} />);

    expect(document.querySelectorAll('.notification-list .no')).toHaveLength(0);
    expect(document.querySelectorAll('.user-notification')).toHaveLength(1);
  });
});

describe('<UserNotificationsMenu>', () => {
  beforeEach(() => {
    vi.spyOn(api,'logUXAction').mockImplementation(() => {});
  })
  afterEach(() => vi.restoreAllMocks());

  it('hides the notifications icon when the user is logged out', () => {
    const user = {
      isAuthenticated: false,
      notifications: {
        has_unread: false,
      },
    };
        render(<UserNotificationsMenu user={user} />);

    expect(document.querySelectorAll('.user-notifications-menu')).toHaveLength(0);
  });

  it('shows the notifications icon when the user is logged in', () => {
    const user = {
      isAuthenticated: true,
      notifications: {
        notifications: [],
      },
    };
    render(<UserNotificationsMenu user={user} />);

    expect(document.querySelectorAll('.user-notifications-menu')).toHaveLength(1);
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
 render(<UserNotificationsMenu user={user} />);

    expect(
      document.querySelector('.user-notifications-menu .badge').textContent
    ).toEqual('5');
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
    render(
      <UserNotificationsMenu
        markAllNotificationsAsRead={markAllNotificationsAsRead}
        user={user}
      />
    );

    expect(api.logUXAction).toHaveBeenCalledTimes(1);
     fireEvent.click(document.querySelector('.selector'));
    expect(api.logUXAction).toHaveBeenCalledTimes(2);
  });
});
