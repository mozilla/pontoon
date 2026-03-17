import React from 'react';

import { Comment } from './Comment';
import { expect, vi } from 'vitest';
import { getByTitle, queryByTitle, render } from '@testing-library/react';
import { MockLocalizationProvider } from '~/test/utils';

vi.mock('react-time-ago', () => {
  return {
    default: () => null,
  };
});

vi.mock('./AddComment', () => ({
  AddComment: () => null,
}));

describe('<Comment>', () => {
  const DEFAULT_COMMENT = {
    author: '',
    username: '',
    userGravatarUrlSmall: '',
    createdAt: '',
    dateIso: '',
    userBanner: [],
    content:
      "What I hear when I'm being yelled at is people caring loudly at me.",
    translation: 0,
    id: 1,
  };

  const DEFAULT_USER = {
    username: 'Leslie_Knope',
  };

  const DEFAULT_ISTRANSLATOR = {
    isTranslator: true,
  };

  it('renders the correct text', () => {
    const deleteMock = vi.fn();
    const { getByText } = render(
      <MockLocalizationProvider>
        <Comment
          comment={DEFAULT_COMMENT}
          key={DEFAULT_COMMENT.id}
          user={DEFAULT_USER}
          isTranslator={DEFAULT_ISTRANSLATOR}
          deleteComment={deleteMock}
        />
      </MockLocalizationProvider>,
    );
    getByText(
      "What I hear when I'm being yelled at is people caring loudly at me.",
    );
  });

  it('renders a link for the author', () => {
    const deleteMock = vi.fn();
    const comments = {
      ...DEFAULT_COMMENT,
      ...{ username: 'Leslie_Knope', author: 'LKnope' },
    };
    const { getByRole } = render(
      <MockLocalizationProvider>
        <Comment
          comment={comments}
          key={comments.id}
          user={DEFAULT_USER}
          isTranslator={DEFAULT_ISTRANSLATOR}
          deleteComment={deleteMock}
        />
      </MockLocalizationProvider>,
    );

    const link = getByRole('link', { name: /LKnope/i });
    expect(link).toHaveAttribute('href', '/contributors/Leslie_Knope');
  });

  it('shows edit and delete buttons when canEditAndDelete is true', () => {
    const { getByTitle } = render(
      <MockLocalizationProvider>
        <Comment
          comment={DEFAULT_COMMENT}
          canEditAndDelete={true}
          user={DEFAULT_USER}
        />
      </MockLocalizationProvider>,
    );

    getByTitle('Edit comment');
    getByTitle('Delete comment');
  });

  it('does not show edit and delete buttons when canEditAndDelete is false', () => {
    const { queryByTitle } = render(
      <MockLocalizationProvider>
        <Comment
          comment={DEFAULT_COMMENT}
          canEditAndDelete={false}
          user={DEFAULT_USER}
        />
      </MockLocalizationProvider>,
    );

    expect(queryByTitle('Edit comment')).toBeNull;
    expect(queryByTitle('Delete comment')).toBeNull;
  });

  it('calls onDeleteComment when delete button is clicked', () => {
    const onDeleteComment = vi.fn();

    const { getByTitle } = render(
      <MockLocalizationProvider>
        <Comment
          comment={DEFAULT_COMMENT}
          canEditAndDelete={true}
          onDeleteComment={onDeleteComment}
          user={DEFAULT_USER}
        />
      </MockLocalizationProvider>,
    );

    getByTitle('Delete comment').click();
    expect(onDeleteComment).toHaveBeenCalledWith(DEFAULT_COMMENT.id);
  });

  it('calls onEditComment when edit button is clicked', () => {
    const onEditComment = vi.fn();

    const { getByTitle, queryByText } = render(
      <MockLocalizationProvider>
        <Comment
          comment={DEFAULT_COMMENT}
          canEditAndDelete={true}
          onEditComment={onEditComment}
          user={DEFAULT_USER}
        />
      </MockLocalizationProvider>,
    );

    getByTitle('Edit comment').click();
    expect(
      queryByText(
        "What I hear when I'm being yelled at is people caring loudly at me.",
      ),
    ).toBeNull();
  });
});
