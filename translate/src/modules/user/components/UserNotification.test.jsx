import React from 'react';
import { UserNotification } from './UserNotification';
import { vi } from 'vitest';
import { render } from '@testing-library/react';

const { timeAgoSpy } = vi.hoisted(() => ({ timeAgoSpy: vi.fn(() => null) }));

vi.mock('react-time-ago', () => {
  return {
    default: timeAgoSpy,
  };
});

const notificationBase = {
  id: 0,
  level: 'level',
  unread: false,
  description: null,
  verb: 'verb',
  date: 'Thursday, January 31, 2019 at 10:20 UTC',
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
    const { getByText } = render(
      <UserNotification notification={notification} />,
    );

    const element = getByText('foo');
    expect(element).toHaveAttribute('id', 'foo');
    expect(element.closest('span.description')).toBeInTheDocument();
  });

  it('shows a "has reviewed suggestions" notification', () => {
    const notification = {
      ...notificationBase,
      description: { content: 'Reviewed: <b id="bar">bar</b>' },
      verb: 'has reviewed suggestions',
    };
    const { getByText } = render(
      <UserNotification notification={notification} />,
    );

    const element = getByText('bar');
    expect(element).toHaveAttribute('id', 'bar');
    expect(element.closest('span.description')).toBeInTheDocument();
  });

  it('shows a comment notification', () => {
    const notification = {
      ...notificationBase,
      description: {
        content: 'Comment: <b id="baz">baz</b>',
        is_comment: true,
      },
    };
    const { getByText } = render(
      <UserNotification notification={notification} />,
    );

    const element = getByText('baz');
    expect(element).toHaveAttribute('id', 'baz');
    expect(element.closest('.message.trim')).toBeInTheDocument();
  });

  it('shows other notification with description', () => {
    const notification = {
      ...notificationBase,
      description: { content: 'Other: <b id="fuzz">fuzz</b>' },
    };
    const { getByText } = render(
      <UserNotification notification={notification} />,
    );

    const element = getByText('fuzz');
    expect(element).toHaveAttribute('id', 'fuzz');
    expect(element.closest('.message')).toBeInTheDocument();
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

  it('shows the exact date and time in the timestamp tooltip', () => {
    const notification = {
      ...notificationBase,
      description: { content: 'Unreviewed suggestions' },
    };
    const { container } = render(
      <UserNotification notification={notification} />,
    );

    const time = container.querySelector('time');
    expect(time).toHaveAttribute('title', notificationBase.date);
    expect(time).toHaveAttribute('datetime', notificationBase.date_iso);
    expect(time).toHaveTextContent('January 31, 2019');
  });

  it('shows the exact date and time in a recent notification tooltip', () => {
    timeAgoSpy.mockClear();
    const notification = {
      ...notificationBase,
      description: { content: 'Unreviewed suggestions' },
      date_iso: new Date(Date.now() - 60 * 1000).toISOString(),
    };
    render(<UserNotification notification={notification} />);

    const props = timeAgoSpy.mock.calls[0][0];
    expect(props.formatVerboseDate()).toBe(notificationBase.date);
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
