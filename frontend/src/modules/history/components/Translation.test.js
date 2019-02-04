import React from 'react';
import { shallow } from 'enzyme';

import Translation from './Translation';


describe('<Translation>', () => {
    const DEFAULT_TRANSLATION = {
        approved: false,
        approved_user: '',
        date: '',
        date_iso: '',
        fuzzy: false,
        pk: 1,
        rejected: false,
        string: 'The storm approaches. We speak no more.',
        uid: 0,
        unapproved_user: '',
        user: '',
        username: 'michel',
    };

    const DEFAULT_USER = {
        username: 'michel',
    };

    const DEFAULT_LOCALE = {
        direction: 'ltr',
        code: 'kg',
        script: 'Latin',
    };

    describe('getStatus', () => {
        it('returns the correct status for approved translations', () => {
            const translation = {
                ...DEFAULT_TRANSLATION,
                ...{ approved: true }
            };
            const wrapper = shallow(<Translation
                translation={ translation }
                locale={ DEFAULT_LOCALE }
            />);

            expect(wrapper.instance().getStatus()).toEqual('approved');
        });

        it('returns the correct status for rejected translations', () => {
            const translation = {
                ...DEFAULT_TRANSLATION,
                ...{ rejected: true }
            };
            const wrapper = shallow(<Translation
                translation={ translation }
                locale={ DEFAULT_LOCALE }
            />);

            expect(wrapper.instance().getStatus()).toEqual('rejected');
        });

        it('returns the correct status for fuzzy translations', () => {
            const translation = {
                ...DEFAULT_TRANSLATION,
                ...{ fuzzy: true }
            };
            const wrapper = shallow(<Translation
                translation={ translation }
                locale={ DEFAULT_LOCALE }
            />);

            expect(wrapper.instance().getStatus()).toEqual('fuzzy');
        });

        it('returns the correct status for unreviewed translations', () => {
            const wrapper = shallow(<Translation
                translation={ DEFAULT_TRANSLATION }
                locale={ DEFAULT_LOCALE }
            />);

            expect(wrapper.instance().getStatus()).toEqual('unreviewed');
        });
    });

    describe('getApprovalTitle', () => {
        it('returns the correct approver title when approved', () => {
            const translation = {
                ...DEFAULT_TRANSLATION,
                ...{ approved: true, approved_user: 'Cespenar' }
            };
            const wrapper = shallow(<Translation
                translation={ translation }
                locale={ DEFAULT_LOCALE }
            />);

            expect(wrapper.instance().getApprovalTitle()).toEqual('Approved by Cespenar');
        });

        it('returns the correct approver title when unapproved', () => {
            const translation = {
                ...DEFAULT_TRANSLATION,
                ...{ unapproved_user: 'Bhaal' }
            };
            const wrapper = shallow(<Translation
                translation={ translation }
                locale={ DEFAULT_LOCALE }
            />);

            expect(wrapper.instance().getApprovalTitle()).toEqual('Unapproved by Bhaal');
        });

        it('returns the correct approver title when neither approved or unapproved', () => {
            const wrapper = shallow(<Translation
                translation={ DEFAULT_TRANSLATION }
                locale={ DEFAULT_LOCALE }
            />);

            expect(wrapper.instance().getApprovalTitle()).toEqual('Not reviewed yet');
        });
    });

    describe('renderUser', () => {
        it('returns a link when the author is known', () => {
            const translation = {
                ...DEFAULT_TRANSLATION,
                ...{ uid: 1, username: 'id_Sarevok', user: 'Sarevok' }
            };
            const wrapper = shallow(<Translation
                translation={ translation }
                locale={ DEFAULT_LOCALE }
            />);

            const link = wrapper.find('a');
            expect(link).toHaveLength(1);
            expect(link.props().children).toEqual('Sarevok');
            expect(link.props().href).toEqual('/contributors/id_Sarevok');
        });

        it('returns no link when the author is not known', () => {
            const wrapper = shallow(<Translation
                translation={ DEFAULT_TRANSLATION }
                locale={ DEFAULT_LOCALE }
            />);

            expect(wrapper.find('a')).toHaveLength(0);
        });
    });

    describe('status', () => {
        it('shows the correct status for approved translations', () => {
            const translation = {
                ...DEFAULT_TRANSLATION,
                ...{ approved: true }
            };
            const wrapper = shallow(<Translation
                translation={ translation }
                locale={ DEFAULT_LOCALE }
            />);

            expect(wrapper.find('.approve')).toHaveLength(0);
            expect(wrapper.find('.unapprove')).toHaveLength(1);
            expect(wrapper.find('.reject')).toHaveLength(1);
            expect(wrapper.find('.unreject')).toHaveLength(0);
        });

        it('shows the correct status for rejected translations', () => {
            const translation = {
                ...DEFAULT_TRANSLATION,
                ...{ rejected: true }
            };
            const wrapper = shallow(<Translation
                translation={ translation }
                locale={ DEFAULT_LOCALE }
            />);

            expect(wrapper.find('.approve')).toHaveLength(1);
            expect(wrapper.find('.unapprove')).toHaveLength(0);
            expect(wrapper.find('.reject')).toHaveLength(0);
            expect(wrapper.find('.unreject')).toHaveLength(1);
        });

        it('shows the correct status for unreviewed translations', () => {
            const wrapper = shallow(<Translation
                translation={ DEFAULT_TRANSLATION }
                locale={ DEFAULT_LOCALE }
            />);

            expect(wrapper.find('.approve')).toHaveLength(1);
            expect(wrapper.find('.unapprove')).toHaveLength(0);
            expect(wrapper.find('.reject')).toHaveLength(1);
            expect(wrapper.find('.unreject')).toHaveLength(0);
        });
    });

    describe('permissions', () => {
        it('allows the user to reject their own unapproved translation', () => {
            const wrapper = shallow(<Translation
                translation={ DEFAULT_TRANSLATION }
                locale={ DEFAULT_LOCALE }
                user={ DEFAULT_USER }
            />);

            expect(wrapper.find('.can-reject')).toHaveLength(1);
            expect(wrapper.find('.can-approve')).toHaveLength(0);
        });

        it('forbids the user to reject their own approved translation', () => {
            const translation = { ...DEFAULT_TRANSLATION, approved: true };
            const wrapper = shallow(<Translation
                translation={ translation }
                locale={ DEFAULT_LOCALE }
                user={ DEFAULT_USER }
            />);

            expect(wrapper.find('.can-reject')).toHaveLength(0);
            expect(wrapper.find('.can-approve')).toHaveLength(0);
        });

        it('allows translators to review the translation', () => {
            const wrapper = shallow(<Translation
                translation={ DEFAULT_TRANSLATION }
                locale={ DEFAULT_LOCALE }
                canReview={ true }
            />);

            expect(wrapper.find('.can-reject')).toHaveLength(1);
            expect(wrapper.find('.can-approve')).toHaveLength(1);
        });

        it('allows translators to delete the rejected translation', () => {
            const translation = { ...DEFAULT_TRANSLATION, rejected: true };
            const wrapper = shallow(<Translation
                translation={ translation }
                locale={ DEFAULT_LOCALE }
                canReview={ true }
            />);

            expect(wrapper.find('.delete')).toHaveLength(1);
        });

        it('forbids translators to delete non-rejected translation', () => {
            const translation = { ...DEFAULT_TRANSLATION, rejected: false };
            const wrapper = shallow(<Translation
                translation={ translation }
                locale={ DEFAULT_LOCALE }
                canReview={ true }
            />);

            expect(wrapper.find('.delete')).toHaveLength(0);
        });

        it('allows the user to delete their own rejected translation', () => {
            const translation = { ...DEFAULT_TRANSLATION, rejected: true };
            const wrapper = shallow(<Translation
                translation={ translation }
                locale={ DEFAULT_LOCALE }
                user={ DEFAULT_USER }
            />);

            expect(wrapper.find('.delete')).toHaveLength(1);
        });

        it('forbids the user to delete rejected translation of another user', () => {
            const translation = { ...DEFAULT_TRANSLATION, rejected: true };
            const wrapper = shallow(<Translation
                translation={ translation }
                locale={ DEFAULT_LOCALE }
            />);

            expect(wrapper.find('.delete')).toHaveLength(0);
        });
    });
});
