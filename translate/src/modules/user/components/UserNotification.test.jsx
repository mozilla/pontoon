import { render, screen } from '@testing-library/react';
import { UserNotification } from './UserNotification';
import { describe, it, expect, vi } from 'vitest';

vi.mock('react-time-ago', () => ({
  default: () => <span>time-ago</span>,
}));

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

    render(<UserNotification notification={notification} />);

    expect(screen.getByText('foo')).toBeInTheDocument();
    expect(screen.getByText('Unreviewed suggestions:', { exact: false })).toBeInTheDocument();
  });

  it('shows a "has reviewed suggestions" notification', () => {
    const notification = {
      ...notificationBase,
      description: { content: 'Reviewed: <b id="bar">bar</b>' },
      verb: 'has reviewed suggestions',
    };

    render(<UserNotification notification={notification} />);

    expect(screen.getByText('bar')).toBeInTheDocument();
    expect(screen.getByText('Reviewed:', { exact: false })).toBeInTheDocument();
  });

  it('shows a comment notification', () => {
    const notification = {
      ...notificationBase,
      description: {
        content: 'Comment: <b id="baz">baz</b>',
        is_comment: true,
      },
    };

    render(<UserNotification notification={notification} />);

    expect(screen.getByText('baz')).toBeInTheDocument();
    expect(screen.getByText('Comment:', { exact: false })).toBeInTheDocument();
  });

  it('shows other notification with description', () => {
    const notification = {
      ...notificationBase,
      description: { content: 'Other: <b id="fuzz">fuzz</b>' },
    };

    render(<UserNotification notification={notification} />);

    expect(screen.getByText('fuzz')).toBeInTheDocument();
    expect(screen.getByText('Other:', { exact: false })).toBeInTheDocument();
  });

  it('shows other notification without description', () => {
    const notification = {
      ...notificationBase,
      description: { content: null },
      verb: 'is Other',
    };

    render(<UserNotification notification={notification} />);

    expect(document.querySelector('.message')?.textContent).toBe('');
    expect(screen.getByText('is Other')).toBeInTheDocument();
  });
});
