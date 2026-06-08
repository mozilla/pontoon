import React from 'react';
import { UserNotification } from './UserNotification';
import { vi } from 'vitest';
import { render } from '@testing-library/react';

vi.mock('react-time-ago', () => {
  return {
    default: () => null,
  };
});

const notificationBase = {
  id: 0,
  level: 'level',
  unread: false,
  description: null,
  verb: 'verb',
  date: 'Jan 31, 2000 10:20',
  date_iso: '2019-01-31T10:20:00+00:00',
  actor: { anchor: 'actor_anchor', url: 'actor_url' },
  target: { anchor: 'target_anchor', url: 'target_url' },
};

describe('<UserNotification>', () => {
  it('shows an "Unreviewed suggestions" notification', () => {
    const notification = {
      ...notificationBase,
      description: { content: 'Unreviewed suggestions: <b id="foo">foo</b>' },
    };
    const { container } = render(
      <UserNotification notification={notification} />,
    );

    expect(
      container.querySelector('span.description b#foo'),
    ).toBeInTheDocument();
  });

  it('shows a "has reviewed suggestions" notification', () => {
    const notification = {
      ...notificationBase,
      description: { content: 'Reviewed: <b id="bar">bar</b>' },
      verb: 'has reviewed suggestions',
    };
    const { container } = render(
      <UserNotification notification={notification} />,
    );

    expect(
      container.querySelector('span.description b#bar'),
    ).toBeInTheDocument();
  });

  it('shows a comment notification', () => {
    const notification = {
      ...notificationBase,
      description: {
        content: 'Comment: <b id="baz">baz</b>',
        is_comment: true,
      },
    };
    const { container } = render(
      <UserNotification notification={notification} />,
    );

    expect(container.querySelector('.message.trim b#baz')).toBeInTheDocument();
  });

  it('shows other notification with description', () => {
    const notification = {
      ...notificationBase,
      description: { content: 'Other: <b id="fuzz">fuzz</b>' },
    };
    const { container } = render(
      <UserNotification notification={notification} />,
    );

    expect(container.querySelector('.message b#fuzz')).toBeInTheDocument();
  });

  it('shows other notification without description', () => {
    const notification = {
      ...notificationBase,
      description: { content: null },
      verb: 'is Other',
    };
    const { container } = render(
      <UserNotification notification={notification} />,
    );

    expect(container.querySelector('.message')).toBeNull();
    expect(container.querySelector('.verb')).toHaveTextContent('is Other');
  });

  it('shows comment notification with deleted actor', () => {
    const notification = {
      ...notificationBase,
      actor: null,
      description: {
        content: 'Comment content',
        is_comment: true,
      },
    };
    const { container } = render(
      <UserNotification notification={notification} />,
    );

    expect(container.querySelector('.actor')).toHaveTextContent('Deleted User');
  });

  it('shows other notification with deleted actor', () => {
    const notification = {
      ...notificationBase,
      actor: null,
      description: { content: 'Other content' },
    };
    const { container } = render(
      <UserNotification notification={notification} />,
    );

    expect(container.querySelector('.actor')).toHaveTextContent('Deleted User');
    expect(container.querySelector('.actor a')).toBeNull();
  });
});
