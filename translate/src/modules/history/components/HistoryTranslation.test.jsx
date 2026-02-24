import React from 'react';

import * as hookModule from '~/hooks/useTranslator';
import { HistoryTranslationBase } from './HistoryTranslation';
import { fireEvent, render } from '@testing-library/react';

import { MockLocalizationProvider } from '~/test/utils';

beforeAll(() => {
  vitest.mock('~/hooks/useTranslator', () => ({
    useTranslator: vi.fn(() => false),
  }));

  vi.mock('react-time-ago', () => {
    return {
      default: () => null,
    };
  });
});

afterAll(() => {
  hookModule.useTranslator.mockRestore();
});

describe('<HistoryTranslationComponent>', () => {
  const DEFAULT_TRANSLATION = {
    approved: false,
    approvedUser: '',
    pretranslated: false,
    date: '',
    fuzzy: false,
    pk: 1,
    rejected: false,
    string: 'The storm approaches. We speak no more.',
    uid: 0,
    rejectedUser: '',
    user: '',
    username: 'michel',
    comments: [],
    userBanner: [],
  };

  const DEFAULT_USER = {
    username: 'michel',
  };

  const DEFAULT_ENTITY = {
    format: 'gettext',
  };
  const WrapHistoryTranslationBase = (props) => {
    return (
      <MockLocalizationProvider>
        <HistoryTranslationBase {...props} />
      </MockLocalizationProvider>
    );
  };

  describe('getStatus', () => {
    it('returns the correct status for approved translations', () => {
      const translation = {
        ...DEFAULT_TRANSLATION,
        ...{ approved: true },
      };
      const { container } = render(
        <WrapHistoryTranslationBase
          translation={translation}
          entity={DEFAULT_ENTITY}
          user={DEFAULT_USER}
        />,
      );

      expect(container.querySelector('.approved')).toBeInTheDocument();
    });

    it('returns the correct status for rejected translations', () => {
      const translation = {
        ...DEFAULT_TRANSLATION,
        ...{ rejected: true },
      };
      const { container } = render(
        <WrapHistoryTranslationBase
          translation={translation}
          entity={DEFAULT_ENTITY}
          user={DEFAULT_USER}
        />,
      );

      expect(container.querySelector('.rejected')).toBeInTheDocument();
    });

    it('returns the correct status for pretranslated translations', () => {
      const translation = {
        ...DEFAULT_TRANSLATION,
        ...{ pretranslated: true },
      };
      const { container } = render(
        <WrapHistoryTranslationBase
          translation={translation}
          entity={DEFAULT_ENTITY}
          user={DEFAULT_USER}
        />,
      );

      expect(container.querySelector('.pretranslated')).toBeInTheDocument();
    });

    it('returns the correct status for fuzzy translations', () => {
      const translation = {
        ...DEFAULT_TRANSLATION,
        ...{ fuzzy: true },
      };
      const { container } = render(
        <WrapHistoryTranslationBase
          translation={translation}
          entity={DEFAULT_ENTITY}
          user={DEFAULT_USER}
        />,
      );

      expect(container.querySelector('.fuzzy')).toBeInTheDocument();
    });

    it('returns the correct status for unreviewed translations', () => {
      const { container } = render(
        <WrapHistoryTranslationBase
          translation={DEFAULT_TRANSLATION}
          entity={DEFAULT_ENTITY}
          user={DEFAULT_USER}
        />,
      );

      expect(container.querySelector('.unreviewed')).toBeInTheDocument();
    });
  });

  describe('review title', () => {
    it('returns the correct review title when approved and approved user is available', () => {
      const ApprovedTitle = 'test-approved';
      const translation = {
        ...DEFAULT_TRANSLATION,
        ...{ approved: true, approvedUser: 'Cespenar' },
      };

      const { getAllByTitle } = render(
        <MockLocalizationProvider
          resource={`history-translation--approved =
                      .title = ${ApprovedTitle}`}
        >
          <HistoryTranslationBase
            translation={translation}
            entity={DEFAULT_ENTITY}
            user={DEFAULT_USER}
          />
        </MockLocalizationProvider>,
      );

      expect(getAllByTitle(ApprovedTitle)).toHaveLength(2);
    });

    it('returns the correct review title when approved and approved user is not available', () => {
      const ApprovedAnonymousTitle = 'test-approved-anonymous';
      const translation = {
        ...DEFAULT_TRANSLATION,
        ...{ approved: true },
      };
      const { getAllByTitle } = render(
        <MockLocalizationProvider
          resource={`history-translation--approved-anonymous =
                      .title = ${ApprovedAnonymousTitle}`}
        >
          <HistoryTranslationBase
            translation={translation}
            entity={DEFAULT_ENTITY}
            user={DEFAULT_USER}
          />
        </MockLocalizationProvider>,
      );

      expect(getAllByTitle(ApprovedAnonymousTitle)).toHaveLength(2);
    });

    it('returns the correct review title when rejected and rejected user is available', () => {
      const RejectedTitle = 'test-rejected';
      const translation = {
        ...DEFAULT_TRANSLATION,
        ...{ rejected: true, rejectedUser: 'Bhaal' },
      };
      const { getAllByTitle } = render(
        <MockLocalizationProvider
          resource={`history-translation--rejected =
                      .title = ${RejectedTitle}`}
        >
          <HistoryTranslationBase
            translation={translation}
            entity={DEFAULT_ENTITY}
            user={DEFAULT_USER}
          />
        </MockLocalizationProvider>,
      );

      expect(getAllByTitle(RejectedTitle)).toHaveLength(2);
    });

    it('returns the correct review title when rejected and rejected user is not available', () => {
      const RejectedAnonymousTitle = 'test-rejected-anonymous';
      const translation = {
        ...DEFAULT_TRANSLATION,
        ...{ rejected: true },
      };
      const { getAllByTitle } = render(
        <MockLocalizationProvider
          resource={`history-translation--rejected-anonymous =
                      .title = ${RejectedAnonymousTitle}`}
        >
          <HistoryTranslationBase
            translation={translation}
            entity={DEFAULT_ENTITY}
            user={DEFAULT_USER}
          />
        </MockLocalizationProvider>,
      );

      expect(getAllByTitle(RejectedAnonymousTitle)).toHaveLength(2);
    });

    it('returns the correct approver title when neither approved or rejected', () => {
      const UnreviewedTitle = 'test-unreviewed';
      const { getAllByTitle } = render(
        <MockLocalizationProvider
          resource={`history-translation--unreviewed =
                      .title = ${UnreviewedTitle}`}
        >
          <HistoryTranslationBase
            translation={DEFAULT_TRANSLATION}
            entity={DEFAULT_ENTITY}
            user={DEFAULT_USER}
          />
        </MockLocalizationProvider>,
      );
      expect(getAllByTitle(UnreviewedTitle)).toHaveLength(2);
    });
  });

  describe('User', () => {
    it('returns a link when the author is known', () => {
      const translation = {
        ...DEFAULT_TRANSLATION,
        ...{ uid: 1, username: 'id_Sarevok', user: 'Sarevok' },
      };
      const { getByRole } = render(
        <WrapHistoryTranslationBase
          translation={translation}
          entity={DEFAULT_ENTITY}
          user={DEFAULT_USER}
        />,
      );

      const link = getByRole('link', { name: translation.user });
      expect(link).toHaveAttribute(
        'href',
        `/contributors/${translation.username}`,
      );
    });

    it('returns no link when the author is not known', () => {
      const translation = {
        ...DEFAULT_TRANSLATION,
        ...{ user: 'Sarevok' },
      };
      const { queryByRole, getByText } = render(
        <WrapHistoryTranslationBase
          translation={translation}
          entity={DEFAULT_ENTITY}
          user={DEFAULT_USER}
        />,
      );

      expect(queryByRole('link', { name: translation.user })).toBeNull();
      getByText(translation.user);
    });
  });

  describe('status', () => {
    const Approve = 'Approve';
    const Approved = 'Approved';
    const Unapprove = 'Unapprove';
    const NotApproved = 'Not approved';
    const Reject = 'Reject';
    const UnReject = 'Unreject';
    const NotRejected = 'Not rejected';

    it('shows the correct buttons for approved translations', () => {
      const translation = {
        ...DEFAULT_TRANSLATION,
        ...{ approved: true },
      };
      const { getByRole, queryByRole } = render(
        <WrapHistoryTranslationBase
          translation={translation}
          entity={DEFAULT_ENTITY}
          user={DEFAULT_USER}
        />,
      );

      expect(queryByRole('button', { name: Approve })).toBeNull();
      expect(getByRole('button', { name: Approved })).toBeDisabled();
      expect(getByRole('button', { name: NotRejected })).toBeDisabled();
      expect(queryByRole('button', { name: UnReject })).toBeNull();
    });

    it('shows the correct buttons for rejected translations', () => {
      const translation = {
        ...DEFAULT_TRANSLATION,
        ...{ rejected: true },
      };
      const { getByRole, queryByRole } = render(
        <WrapHistoryTranslationBase
          translation={translation}
          entity={DEFAULT_ENTITY}
          user={DEFAULT_USER}
        />,
      );

      expect(getByRole('button', { name: NotApproved })).toBeDisabled();
      expect(queryByRole('button', { name: Unapprove })).toBeNull();
      expect(queryByRole('button', { name: Reject })).toBeNull();
      expect(getByRole('button', { name: UnReject })).not.toBeDisabled();
    });

    it('shows the correct buttons for unreviewed translations', () => {
      const { getByRole, queryByRole } = render(
        <WrapHistoryTranslationBase
          translation={DEFAULT_TRANSLATION}
          entity={DEFAULT_ENTITY}
          user={DEFAULT_USER}
        />,
      );
      expect(getByRole('button', { name: NotApproved })).toBeDisabled();
      expect(queryByRole('button', { name: Unapprove })).toBeNull();
      expect(getByRole('button', { name: Reject })).not.toBeDisabled();
      expect(queryByRole('button', { name: UnReject })).toBeNull();
    });
  });

  describe('permissions', () => {
    const RejectButton = 'Reject';
    const ApproveButton = 'Approve';
    const DeleteButton = 'Delete';

    it('allows the user to reject their own unapproved translation', () => {
      const { getByRole, queryByRole } = render(
        <WrapHistoryTranslationBase
          translation={DEFAULT_TRANSLATION}
          entity={DEFAULT_ENTITY}
          user={DEFAULT_USER}
        />,
      );

      getByRole('button', { name: RejectButton });
      expect(queryByRole('button', { name: ApproveButton })).toBeNull();
    });

    it('forbids the user to reject their own approved translation', () => {
      const translation = { ...DEFAULT_TRANSLATION, approved: true };
      const { queryByRole } = render(
        <WrapHistoryTranslationBase
          translation={translation}
          entity={DEFAULT_ENTITY}
          user={DEFAULT_USER}
        />,
      );

      expect(queryByRole('button', { name: RejectButton })).toBeNull();
      expect(queryByRole('button', { name: ApproveButton })).toBeNull();
    });

    it('allows translators to review the translation', () => {
      hookModule.useTranslator.mockReturnValue(true);
      const { getByRole } = render(
        <WrapHistoryTranslationBase
          translation={DEFAULT_TRANSLATION}
          entity={DEFAULT_ENTITY}
          user={DEFAULT_USER}
        />,
      );

      getByRole('button', { name: RejectButton });
      getByRole('button', { name: ApproveButton });
    });

    it('allows translators to delete the rejected translation', () => {
      hookModule.useTranslator.mockReturnValue(true);
      const translation = { ...DEFAULT_TRANSLATION, rejected: true };
      const { getByRole } = render(
        <WrapHistoryTranslationBase
          translation={translation}
          entity={DEFAULT_ENTITY}
          user={DEFAULT_USER}
        />,
      );

      getByRole('button', { name: DeleteButton });
    });

    it('forbids translators to delete non-rejected translation', () => {
      hookModule.useTranslator.mockReturnValue(true);
      const translation = { ...DEFAULT_TRANSLATION, rejected: false };
      const { queryByRole } = render(
        <WrapHistoryTranslationBase
          translation={translation}
          entity={DEFAULT_ENTITY}
          user={DEFAULT_USER}
        />,
      );

      expect(queryByRole('button', { name: DeleteButton })).toBeNull();
    });

    it('allows the user to delete their own rejected translation', () => {
      const translation = { ...DEFAULT_TRANSLATION, rejected: true };
      const { getByRole } = render(
        <WrapHistoryTranslationBase
          translation={translation}
          entity={DEFAULT_ENTITY}
          user={DEFAULT_USER}
        />,
      );

      getByRole('button', { name: DeleteButton });
    });

    it('forbids the user to delete rejected translation of another user', () => {
      const translation = { ...DEFAULT_TRANSLATION, rejected: true };
      const { queryByRole } = render(
        <WrapHistoryTranslationBase
          translation={translation}
          entity={DEFAULT_ENTITY}
          user={{ username: 'Andy_Dwyer' }}
        />,
      );

      expect(queryByRole('button', { name: DeleteButton })).toBeNull();
    });
  });

  describe('DiffToggle', () => {
    it('shows default translation and no Show/Hide diff button for the first translation', () => {
      const { container, queryByRole } = render(
        <WrapHistoryTranslationBase
          translation={DEFAULT_TRANSLATION}
          entity={DEFAULT_ENTITY}
          activeTranslation={DEFAULT_TRANSLATION}
          user={DEFAULT_USER}
          index={0}
        />,
      );

      expect(container.querySelector('.default')).toBeInTheDocument();
      expect(container.querySelector('.diff-visible')).toBeNull();

      expect(queryByRole('button', { name: 'DIFF' })).toBeNull();
    });

    it('shows default translation and the Show diff button for a non-first translation', () => {
      const { container, getByRole } = render(
        <WrapHistoryTranslationBase
          translation={DEFAULT_TRANSLATION}
          entity={DEFAULT_ENTITY}
          activeTranslation={DEFAULT_TRANSLATION}
          user={DEFAULT_USER}
          index={1}
        />,
      );
      expect(container.querySelector('.default')).toBeInTheDocument();
      expect(container.querySelector('.diff-visible')).toBeNull();

      const DiffToggle = getByRole('button', { name: 'DIFF' });
      expect(DiffToggle.classList.contains('off')).toBeTruthy();
      expect(DiffToggle.classList.contains('on')).toBeFalsy();
    });

    it('shows translation diff and the Hide diff button for a non-first translation if diff visible', () => {
      const { container, getByRole } = render(
        <WrapHistoryTranslationBase
          translation={DEFAULT_TRANSLATION}
          entity={DEFAULT_ENTITY}
          activeTranslation={DEFAULT_TRANSLATION}
          user={DEFAULT_USER}
          index={1}
        />,
      );
      const DiffToggle = getByRole('button', { name: 'DIFF' });

      fireEvent.click(DiffToggle);

      expect(container.querySelector('.default')).toBeNull();
      expect(container.querySelector('.diff-visible')).toBeInTheDocument();

      expect(DiffToggle.classList.contains('off')).toBeFalsy();
      expect(DiffToggle.classList.contains('on')).toBeTruthy();
    });
  });
});
