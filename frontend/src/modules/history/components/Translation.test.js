import React from 'react';
import { shallow } from 'enzyme';

import { TranslationBase } from './Translation';

describe('<TranslationBase>', () => {
    const DEFAULT_TRANSLATION = {
        approved: false,
        approvedUser: '',
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

    const DEFAULT_LOCALE = {
        direction: 'ltr',
        code: 'kg',
        script: 'Latin',
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
                    locale={DEFAULT_LOCALE}
                    user={DEFAULT_USER}
                />,
            );

            expect(wrapper.instance().getStatus()).toEqual('approved');
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
                    locale={DEFAULT_LOCALE}
                    user={DEFAULT_USER}
                />,
            );

            expect(wrapper.instance().getStatus()).toEqual('rejected');
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
                    locale={DEFAULT_LOCALE}
                    user={DEFAULT_USER}
                />,
            );

            expect(wrapper.instance().getStatus()).toEqual('fuzzy');
        });

        it('returns the correct status for unreviewed translations', () => {
            const wrapper = shallow(
                <TranslationBase
                    translation={DEFAULT_TRANSLATION}
                    entity={DEFAULT_ENTITY}
                    locale={DEFAULT_LOCALE}
                    user={DEFAULT_USER}
                />,
            );

            expect(wrapper.instance().getStatus()).toEqual('unreviewed');
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
                    locale={DEFAULT_LOCALE}
                    user={DEFAULT_USER}
                />,
            );

            expect(wrapper.instance().getApprovalTitle()).toEqual(
                'Approved by Cespenar',
            );
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
                    locale={DEFAULT_LOCALE}
                    user={DEFAULT_USER}
                />,
            );

            expect(wrapper.instance().getApprovalTitle()).toEqual(
                'Unapproved by Bhaal',
            );
        });

        it('returns the correct approver title when neither approved or unapproved', () => {
            const wrapper = shallow(
                <TranslationBase
                    translation={DEFAULT_TRANSLATION}
                    entity={DEFAULT_ENTITY}
                    locale={DEFAULT_LOCALE}
                    user={DEFAULT_USER}
                />,
            );

            expect(wrapper.instance().getApprovalTitle()).toEqual(
                'Not reviewed yet',
            );
        });
    });

    describe('renderUser', () => {
        it('returns a link when the author is known', () => {
            const translation = {
                ...DEFAULT_TRANSLATION,
                ...{ uid: 1, username: 'id_Sarevok', user: 'Sarevok' },
            };
            const wrapper = shallow(
                <TranslationBase
                    translation={translation}
                    entity={DEFAULT_ENTITY}
                    locale={DEFAULT_LOCALE}
                    user={DEFAULT_USER}
                />,
            );

            const link = wrapper.find('a');
            expect(link).toHaveLength(1);
            expect(link.at(0).props().children).toEqual('Sarevok');
            expect(link.at(0).props().href).toEqual('/contributors/id_Sarevok');
        });

        it('returns no link when the author is not known', () => {
            const wrapper = shallow(
                <TranslationBase
                    translation={DEFAULT_TRANSLATION}
                    entity={DEFAULT_ENTITY}
                    locale={DEFAULT_LOCALE}
                    user={DEFAULT_USER}
                />,
            );

            expect(wrapper.find('a')).toHaveLength(0);
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
                    locale={DEFAULT_LOCALE}
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
                    locale={DEFAULT_LOCALE}
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
                    locale={DEFAULT_LOCALE}
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
                    locale={DEFAULT_LOCALE}
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
                    locale={DEFAULT_LOCALE}
                    user={DEFAULT_USER}
                />,
            );

            expect(wrapper.find('.can-reject')).toHaveLength(0);
            expect(wrapper.find('.can-approve')).toHaveLength(0);
        });

        it('allows translators to review the translation', () => {
            const wrapper = shallow(
                <TranslationBase
                    translation={DEFAULT_TRANSLATION}
                    entity={DEFAULT_ENTITY}
                    locale={DEFAULT_LOCALE}
                    isTranslator={true}
                    user={DEFAULT_USER}
                />,
            );

            expect(wrapper.find('.can-reject')).toHaveLength(1);
            expect(wrapper.find('.can-approve')).toHaveLength(1);
        });

        it('allows translators to delete the rejected translation', () => {
            const translation = { ...DEFAULT_TRANSLATION, rejected: true };
            const wrapper = shallow(
                <TranslationBase
                    translation={translation}
                    entity={DEFAULT_ENTITY}
                    locale={DEFAULT_LOCALE}
                    isTranslator={true}
                    user={DEFAULT_USER}
                />,
            );

            expect(wrapper.find('.delete')).toHaveLength(1);
        });

        it('forbids translators to delete non-rejected translation', () => {
            const translation = { ...DEFAULT_TRANSLATION, rejected: false };
            const wrapper = shallow(
                <TranslationBase
                    translation={translation}
                    entity={DEFAULT_ENTITY}
                    locale={DEFAULT_LOCALE}
                    isTranslator={true}
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
                    locale={DEFAULT_LOCALE}
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
                    locale={DEFAULT_LOCALE}
                    user={{ username: 'Andy_Dwyer' }}
                />,
            );

            expect(wrapper.find('.delete')).toHaveLength(0);
        });
    });

    describe('diff', () => {
        it('shows default translation and no Show/Hide diff button for the first translation', () => {
            const wrapper = shallow(
                <TranslationBase
                    translation={DEFAULT_TRANSLATION}
                    entity={DEFAULT_ENTITY}
                    activeTranslation={DEFAULT_TRANSLATION}
                    locale={DEFAULT_LOCALE}
                    user={DEFAULT_USER}
                    index={0}
                />,
            );

            expect(wrapper.find('.default')).toHaveLength(1);
            expect(wrapper.find('.diff')).toHaveLength(0);

            expect(wrapper.find('.toggle-diff.show')).toHaveLength(0);
            expect(wrapper.find('.toggle-diff.hide')).toHaveLength(0);
        });

        it('shows default translation and the Show diff button for a non-first translation', () => {
            const wrapper = shallow(
                <TranslationBase
                    translation={DEFAULT_TRANSLATION}
                    entity={DEFAULT_ENTITY}
                    activeTranslation={DEFAULT_TRANSLATION}
                    locale={DEFAULT_LOCALE}
                    user={DEFAULT_USER}
                    index={1}
                />,
            );

            wrapper.instance().setState({ isDiffVisible: false });

            expect(wrapper.find('.default')).toHaveLength(1);
            expect(wrapper.find('.diff')).toHaveLength(0);

            expect(wrapper.find('.toggle-diff.show')).toHaveLength(1);
            expect(wrapper.find('.toggle-diff.hide')).toHaveLength(0);
        });

        it('shows translation diff and the Hide diff button for a non-first translation if diff visible', () => {
            const wrapper = shallow(
                <TranslationBase
                    translation={DEFAULT_TRANSLATION}
                    entity={DEFAULT_ENTITY}
                    activeTranslation={DEFAULT_TRANSLATION}
                    locale={DEFAULT_LOCALE}
                    user={DEFAULT_USER}
                    index={1}
                />,
            );

            wrapper.instance().setState({ isDiffVisible: true });

            expect(wrapper.find('.default')).toHaveLength(0);
            expect(wrapper.find('.diff')).toHaveLength(1);

            expect(wrapper.find('.toggle-diff.show')).toHaveLength(0);
            expect(wrapper.find('.toggle-diff.hide')).toHaveLength(1);
        });
    });
});
