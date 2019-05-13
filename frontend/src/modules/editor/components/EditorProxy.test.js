import React from 'react';
import { shallow } from 'enzyme';
import sinon from 'sinon';

import EditorProxy from './EditorProxy';
import FluentEditor from './FluentEditor';
import GenericEditor from './GenericEditor';


describe('<EditorProxy>', () => {
    const EDITOR = {
        translation: 'world',
        errors: ['error1'],
        warnings: ['warning1'],
    };

    it('returns null when the entity is empty', () => {
        const wrapper = shallow(<EditorProxy entity={ null } />);

        expect(wrapper.type()).toBeNull();
    });

    it('returns a FluentEditor when the format is ftl', () => {
        const wrapper = shallow(<EditorProxy entity={ { format: 'ftl' } } />);

        expect(wrapper.type()).toEqual(FluentEditor);
    });

    it('returns a GenericEditor when the format is not ftl', () => {
        const wrapper = shallow(<EditorProxy entity={ { format: 'po' } } />);

        expect(wrapper.type()).toEqual(GenericEditor);
    });

    it('resets failed checks when translation changes, but errors and warnings do not', () => {
        const resetMock = sinon.stub();

        const wrapper = shallow(<EditorProxy
            editor={ EDITOR }
            resetFailedChecks={ resetMock }
            updateUnsavedChanges={ sinon.spy() }
        />);

        wrapper.setProps({
            editor: {
                ...EDITOR,
                translation: 'hello',
            }
        });

        expect(resetMock.calledOnce).toBeTruthy();
    });

    it('keeps failed checks when translation changes, along with errors or warnings', () => {
        const resetMock = sinon.stub();

        const wrapper = shallow(<EditorProxy
            editor={ EDITOR }
            resetFailedChecks={ resetMock }
            updateUnsavedChanges={ sinon.spy() }
        />);

        wrapper.setProps({
            editor: {
                ...EDITOR,
                translation: 'hello',
                errors: [],
            }
        });

        expect(resetMock.calledOnce).toBeFalsy();
    });
});
