import * as Fluent from '@fluent/react';
import { shallow } from 'enzyme';
import React from 'react';
import sinon from 'sinon';

import * as hookModule from '~/hooks/useTranslator';
import { TranslationBase } from './Translation';

beforeAll(() => {
  sinon
    .stub(Fluent, 'useLocalization')
    .returns({ l10n: { getString: (_id, _args, fallback) => fallback } });
  sinon.stub(hookModule, 'useTranslator');
});
beforeEach(() => hookModule.useTranslator.returns(false));
afterAll(() => {
  hookModule.useTranslator.restore();
});

describe('<TranslationBase>', () => {
  const DEFAULT_TRANSLATION = {
    approved: false,
    approvedUser: '',
    pretranslated: false,
    date: '',
    dateIso: '',
    fuzzy: false,
    pk: 1,
    rejected: false,
    string: 'The storm approaches. We speak no more.',
    uid: 0,
    unapprovedUser: '',
    user: '',
    username: 'michel',
    comments: [],
  };

  const DEFAULT_USER = {
    username: 'michel',
  };

  const DEFAULT_ENTITY = {
    format: 'po',
  };

  describe('getStatus', () => {
    it('returns the correct status for approved translations', () => {
      const translation = {
        ...DEFAULT_TRANSLATION,
        ...{ approved: true },
      };
      const wrapper = shallow(
        <TranslationBase
          translation={translation}
          entity={DEFAULT_ENTITY}
          user={DEFAULT_USER}
        />,
      );

      expect(wrapper.find('.approved')).toHaveLength(1);
    });

    it('returns the correct status for rejected translations', () => {
      const translation = {
        ...DEFAULT_TRANSLATION,
        ...{ rejected: true },
      };
      const wrapper = shallow(
        <TranslationBase
          translation={translation}
          entity={DEFAULT_ENTITY}
          user={DEFAULT_USER}
        />,
      );

      expect(wrapper.find('.rejected')).toHaveLength(1);
    });

    it('returns the correct status for pretranslated translations', () => {
      const translation = {
        ...DEFAULT_TRANSLATION,
        ...{ pretranslated: true },
      };
      const wrapper = shallow(
        <TranslationBase
          translation={translation}
          entity={DEFAULT_ENTITY}
          user={DEFAULT_USER}
        />,
      );

      expect(wrapper.find('.pretranslated')).toHaveLength(1);
    });

    it('returns the correct status for fuzzy translations', () => {
      const translation = {
        ...DEFAULT_TRANSLATION,
        ...{ fuzzy: true },
      };
      const wrapper = shallow(
        <TranslationBase
          translation={translation}
          entity={DEFAULT_ENTITY}
          user={DEFAULT_USER}
        />,
      );

      expect(wrapper.find('.fuzzy')).toHaveLength(1);
    });

    it('returns the correct status for unreviewed translations', () => {
      const wrapper = shallow(
        <TranslationBase
          translation={DEFAULT_TRANSLATION}
          entity={DEFAULT_ENTITY}
          user={DEFAULT_USER}
        />,
      );

      expect(wrapper.find('.unreviewed')).toHaveLength(1);
    });
  });

  describe('getApprovalTitle', () => {
    it('returns the correct approver title when approved', () => {
      const translation = {
        ...DEFAULT_TRANSLATION,
        ...{ approved: true, approvedUser: 'Cespenar' },
      };
      const wrapper = shallow(
        <TranslationBase
          translation={translation}
          entity={DEFAULT_ENTITY}
          user={DEFAULT_USER}
        />,
      );

      expect(wrapper.find('[title="Approved by Cespenar"]')).toHaveLength(2);
    });

    it('returns the correct approver title when unapproved', () => {
      const translation = {
        ...DEFAULT_TRANSLATION,
        ...{ unapprovedUser: 'Bhaal' },
      };
      const wrapper = shallow(
        <TranslationBase
          translation={translation}
          entity={DEFAULT_ENTITY}
          user={DEFAULT_USER}
        />,
      );

      expect(wrapper.find('[title="Unapproved by Bhaal"]')).toHaveLength(2);
    });

    it('returns the correct approver title when neither approved or unapproved', () => {
      const wrapper = shallow(
        <TranslationBase
          translation={DEFAULT_TRANSLATION}
          entity={DEFAULT_ENTITY}
          user={DEFAULT_USER}
        />,
      );

      expect(wrapper.find('[title="Not reviewed yet"]')).toHaveLength(2);
    });
  });

  describe('User', () => {
    it('returns a link when the author is known', () => {
      const translation = {
        ...DEFAULT_TRANSLATION,
        ...{ uid: 1, username: 'id_Sarevok', user: 'Sarevok' },
      };
      const wrapper = shallow(
        <TranslationBase
          translation={translation}
          entity={DEFAULT_ENTITY}
          user={DEFAULT_USER}
        />,
      );

      const link = wrapper.find('User').dive().find('a');
      expect(link.props()).toMatchObject({
        children: 'Sarevok',
        href: '/contributors/id_Sarevok',
      });
    });

    it('returns no link when the author is not known', () => {
      const wrapper = shallow(
        <TranslationBase
          translation={DEFAULT_TRANSLATION}
          entity={DEFAULT_ENTITY}
          user={DEFAULT_USER}
        />,
      );

      const link = wrapper.find('User').dive().find('a');
      expect(link).toHaveLength(0);
    });
  });

  describe('status', () => {
    it('shows the correct status for approved translations', () => {
      const translation = {
        ...DEFAULT_TRANSLATION,
        ...{ approved: true },
      };
      const wrapper = shallow(
        <TranslationBase
          translation={translation}
          entity={DEFAULT_ENTITY}
          user={DEFAULT_USER}
        />,
      );

      expect(wrapper.find('.approve')).toHaveLength(0);
      expect(wrapper.find('.unapprove')).toHaveLength(1);
      expect(wrapper.find('.reject')).toHaveLength(1);
      expect(wrapper.find('.unreject')).toHaveLength(0);
    });

    it('shows the correct status for rejected translations', () => {
      const translation = {
        ...DEFAULT_TRANSLATION,
        ...{ rejected: true },
      };
      const wrapper = shallow(
        <TranslationBase
          translation={translation}
          entity={DEFAULT_ENTITY}
          user={DEFAULT_USER}
        />,
      );

      expect(wrapper.find('.approve')).toHaveLength(1);
      expect(wrapper.find('.unapprove')).toHaveLength(0);
      expect(wrapper.find('.reject')).toHaveLength(0);
      expect(wrapper.find('.unreject')).toHaveLength(1);
    });

    it('shows the correct status for unreviewed translations', () => {
      const wrapper = shallow(
        <TranslationBase
          translation={DEFAULT_TRANSLATION}
          entity={DEFAULT_ENTITY}
          user={DEFAULT_USER}
        />,
      );

      expect(wrapper.find('.approve')).toHaveLength(1);
      expect(wrapper.find('.unapprove')).toHaveLength(0);
      expect(wrapper.find('.reject')).toHaveLength(1);
      expect(wrapper.find('.unreject')).toHaveLength(0);
    });
  });

  describe('permissions', () => {
    it('allows the user to reject their own unapproved translation', () => {
      const wrapper = shallow(
        <TranslationBase
          translation={DEFAULT_TRANSLATION}
          entity={DEFAULT_ENTITY}
          user={DEFAULT_USER}
        />,
      );

      expect(wrapper.find('.can-reject')).toHaveLength(1);
      expect(wrapper.find('.can-approve')).toHaveLength(0);
    });

    it('forbids the user to reject their own approved translation', () => {
      const translation = { ...DEFAULT_TRANSLATION, approved: true };
      const wrapper = shallow(
        <TranslationBase
          translation={translation}
          entity={DEFAULT_ENTITY}
          user={DEFAULT_USER}
        />,
      );

      expect(wrapper.find('.can-reject')).toHaveLength(0);
      expect(wrapper.find('.can-approve')).toHaveLength(0);
    });

    it('allows translators to review the translation', () => {
      hookModule.useTranslator.returns(true);
      const wrapper = shallow(
        <TranslationBase
          translation={DEFAULT_TRANSLATION}
          entity={DEFAULT_ENTITY}
          user={DEFAULT_USER}
        />,
      );

      expect(wrapper.find('.can-reject')).toHaveLength(1);
      expect(wrapper.find('.can-approve')).toHaveLength(1);
    });

    it('allows translators to delete the rejected translation', () => {
      hookModule.useTranslator.returns(true);
      const translation = { ...DEFAULT_TRANSLATION, rejected: true };
      const wrapper = shallow(
        <TranslationBase
          translation={translation}
          entity={DEFAULT_ENTITY}
          user={DEFAULT_USER}
        />,
      );

      expect(wrapper.find('.delete')).toHaveLength(1);
    });

    it('forbids translators to delete non-rejected translation', () => {
      hookModule.useTranslator.returns(true);
      const translation = { ...DEFAULT_TRANSLATION, rejected: false };
      const wrapper = shallow(
        <TranslationBase
          translation={translation}
          entity={DEFAULT_ENTITY}
          user={DEFAULT_USER}
        />,
      );

      expect(wrapper.find('.delete')).toHaveLength(0);
    });

    it('allows the user to delete their own rejected translation', () => {
      const translation = { ...DEFAULT_TRANSLATION, rejected: true };
      const wrapper = shallow(
        <TranslationBase
          translation={translation}
          entity={DEFAULT_ENTITY}
          user={DEFAULT_USER}
        />,
      );

      expect(wrapper.find('.delete')).toHaveLength(1);
    });

    it('forbids the user to delete rejected translation of another user', () => {
      const translation = { ...DEFAULT_TRANSLATION, rejected: true };
      const wrapper = shallow(
        <TranslationBase
          translation={translation}
          entity={DEFAULT_ENTITY}
          user={{ username: 'Andy_Dwyer' }}
        />,
      );

      expect(wrapper.find('.delete')).toHaveLength(0);
    });
  });

  describe('DiffToggle', () => {
    it('shows default translation and no Show/Hide diff button for the first translation', () => {
      const wrapper = shallow(
        <TranslationBase
          translation={DEFAULT_TRANSLATION}
          entity={DEFAULT_ENTITY}
          activeTranslation={DEFAULT_TRANSLATION}
          user={DEFAULT_USER}
          index={0}
        />,
      );

      expect(wrapper.find('.default')).toHaveLength(1);
      expect(wrapper.find('.diff-visible')).toHaveLength(0);

      const toggle = wrapper.find('DiffToggle').dive();
      expect(toggle.find('.toggle.diff.off')).toHaveLength(0);
      expect(toggle.find('.toggle.diff.on')).toHaveLength(0);
    });

    it('shows default translation and the Show diff button for a non-first translation', () => {
      const wrapper = shallow(
        <TranslationBase
          translation={DEFAULT_TRANSLATION}
          entity={DEFAULT_ENTITY}
          activeTranslation={DEFAULT_TRANSLATION}
          user={DEFAULT_USER}
          index={1}
        />,
      );

      expect(wrapper.find('.default')).toHaveLength(1);
      expect(wrapper.find('.diff-visible')).toHaveLength(0);

      const toggle = wrapper.find('DiffToggle').dive();
      expect(toggle.find('.toggle.diff.off')).toHaveLength(1);
      expect(toggle.find('.toggle.diff.on')).toHaveLength(0);
    });

    it('shows translation diff and the Hide diff button for a non-first translation if diff visible', () => {
      const wrapper = shallow(
        <TranslationBase
          translation={DEFAULT_TRANSLATION}
          entity={DEFAULT_ENTITY}
          activeTranslation={DEFAULT_TRANSLATION}
          user={DEFAULT_USER}
          index={1}
        />,
      );

      wrapper.find('DiffToggle').props().toggleVisible();

      expect(wrapper.find('.default')).toHaveLength(0);
      expect(wrapper.find('.diff-visible')).toHaveLength(1);

      const toggle = wrapper.find('DiffToggle').dive();
      expect(toggle.find('.toggle.diff.off')).toHaveLength(0);
      expect(toggle.find('.toggle.diff.on')).toHaveLength(1);
    });
  });
});
