import React from 'react';
import { shallow } from 'enzyme';
import sinon from 'sinon';

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
        username: '',
    };

    describe('getStatus', () => {
        it('returns the correct status for approved translations', () => {
            const translation = {
                ...DEFAULT_TRANSLATION,
                ...{ approved: true }
            };
            const wrapper = shallow(<Translation translation={ translation } />);

            expect(wrapper.instance().getStatus()).toEqual('approved');
        });

        it('returns the correct status for rejected translations', () => {
            const translation = {
                ...DEFAULT_TRANSLATION,
                ...{ rejected: true }
            };
            const wrapper = shallow(<Translation translation={ translation } />);

            expect(wrapper.instance().getStatus()).toEqual('rejected');
        });

        it('returns the correct status for fuzzy translations', () => {
            const translation = {
                ...DEFAULT_TRANSLATION,
                ...{ fuzzy: true }
            };
            const wrapper = shallow(<Translation translation={ translation } />);

            expect(wrapper.instance().getStatus()).toEqual('fuzzy');
        });

        it('returns the correct status for unreviewed translations', () => {
            const wrapper = shallow(<Translation translation={ DEFAULT_TRANSLATION } />);

            expect(wrapper.instance().getStatus()).toEqual('unreviewed');
        });
    });

    describe('getApprovalTitle', () => {
        it('returns the correct approver title when approved', () => {
            const translation = {
                ...DEFAULT_TRANSLATION,
                ...{ approved: true, approved_user: 'Cespenar' }
            };
            const wrapper = shallow(<Translation translation={ translation } />);

            expect(wrapper.instance().getApprovalTitle()).toEqual('Approved by Cespenar');
        });

        it('returns the correct approver title when unapproved', () => {
            const translation = {
                ...DEFAULT_TRANSLATION,
                ...{ unapproved_user: 'Bhaal' }
            };
            const wrapper = shallow(<Translation translation={ translation } />);

            expect(wrapper.instance().getApprovalTitle()).toEqual('Unapproved by Bhaal');
        });

        it('returns the correct approver title when neither approved or unapproved', () => {
            const wrapper = shallow(<Translation translation={ DEFAULT_TRANSLATION } />);

            expect(wrapper.instance().getApprovalTitle()).toEqual('Not reviewed yet');
        });
    });

    describe('renderUser', () => {
        it('returns a link when the author is known', () => {
            const translation = {
                ...DEFAULT_TRANSLATION,
                ...{ uid: 1, username: 'id_Sarevok', user: 'Sarevok' }
            };
            const wrapper = shallow(<Translation translation={ translation } />);

            const link = wrapper.find('a');
            expect(link).toHaveLength(1);
            expect(link.props().children).toEqual('Sarevok');
            expect(link.props().href).toEqual('/contributors/id_Sarevok');
        });

        it('returns no link when the author is not known', () => {
            const wrapper = shallow(<Translation translation={ DEFAULT_TRANSLATION } />);

            expect(wrapper.find('a')).toHaveLength(0);
        });
    });

    describe('status', () => {
        it('shows the correct status for approved translations', () => {
            const translation = {
                ...DEFAULT_TRANSLATION,
                ...{ approved: true }
            };
            const wrapper = shallow(<Translation translation={ translation } />);

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
            const wrapper = shallow(<Translation translation={ translation } />);

            expect(wrapper.find('.approve')).toHaveLength(1);
            expect(wrapper.find('.unapprove')).toHaveLength(0);
            expect(wrapper.find('.reject')).toHaveLength(0);
            expect(wrapper.find('.unreject')).toHaveLength(1);
        });

        it('shows the correct status for unreviewed translations', () => {
            const wrapper = shallow(<Translation translation={ DEFAULT_TRANSLATION } />);

            expect(wrapper.find('.approve')).toHaveLength(1);
            expect(wrapper.find('.unapprove')).toHaveLength(0);
            expect(wrapper.find('.reject')).toHaveLength(1);
            expect(wrapper.find('.unreject')).toHaveLength(0);
        });
    });
});
