import React from 'react';

import { Comment } from './Comment';
import { expect, vi } from 'vitest';
import { render } from '@testing-library/react';
import { MockLocalizationProvider } from '~/test/utils';

vi.mock('react-time-ago', () => {
  return {
    default: () => null,
  };
});

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
});
