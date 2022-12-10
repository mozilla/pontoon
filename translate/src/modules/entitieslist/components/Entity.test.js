import { mount, shallow } from 'enzyme';
import React from 'react';
import sinon from 'sinon';

import * as hookModule from '~/hooks/useTranslator';
import { Entity } from './Entity';

beforeAll(() => sinon.stub(hookModule, 'useTranslator'));
beforeEach(() => hookModule.useTranslator.returns(false));
afterAll(() => hookModule.useTranslator.restore());

describe('<Entity>', () => {
  const ENTITY_A = {
    original: 'string a',
    translation: [
      {
        string: 'chaine a',
        approved: true,
        errors: [],
        warnings: [],
      },
    ],
  };

  const ENTITY_B = {
    original: 'string b',
    translation: [
      {
        string: 'chaine b',
        pretranslated: true,
        errors: [],
        warnings: [],
      },
    ],
  };

  const ENTITY_C = {
    original: 'string c',
    translation: [
      {
        string: 'chaine c',
        errors: [],
        warnings: [],
      },
    ],
  };

  const ENTITY_D = {
    original: 'string d',
    translation: [
      {
        string: 'chaine d',
        approved: true,
        errors: ['error'],
        warnings: [],
      },
    ],
  };

  const ENTITY_E = {
    original: 'string e',
    translation: [
      {
        string: 'chaine e',
        pretranslated: true,
        errors: [],
        warnings: ['warning'],
      },
    ],
  };

  const ENTITY_F = {
    original: 'string f',
    translation: [
      {
        string: 'chaine f1',
        approved: true,
        errors: [],
        warnings: [],
      },
      {
        string: 'chaine f2',
        pretranslated: true,
        errors: [],
        warnings: [],
      },
    ],
  };

  it('renders the source string and the first translation', () => {
    const wrapper = shallow(<Entity entity={ENTITY_A} parameters={{}} />);

    const contents = wrapper.find('Translation');
    expect(contents.first().props().content).toContain(ENTITY_A.original);
    expect(contents.last().props().content).toContain(
      ENTITY_A.translation[0].string,
    );
  });

  it('shows the correct status class', () => {
    let wrapper = shallow(<Entity entity={ENTITY_A} parameters={{}} />);
    expect(wrapper.find('.approved')).toHaveLength(1);

    wrapper = shallow(<Entity entity={ENTITY_B} parameters={{}} />);
    expect(wrapper.find('.pretranslated')).toHaveLength(1);

    wrapper = shallow(<Entity entity={ENTITY_C} parameters={{}} />);
    expect(wrapper.find('.missing')).toHaveLength(1);

    wrapper = shallow(<Entity entity={ENTITY_D} parameters={{}} />);
    expect(wrapper.find('.errors')).toHaveLength(1);

    wrapper = shallow(<Entity entity={ENTITY_E} parameters={{}} />);
    expect(wrapper.find('.warnings')).toHaveLength(1);

    wrapper = shallow(<Entity entity={ENTITY_F} parameters={{}} />);
    expect(wrapper.find('.partial')).toHaveLength(1);
  });

  it('calls the selectEntity function on click on li', () => {
    const selectEntityFn = sinon.spy();
    const wrapper = mount(
      <Entity
        entity={ENTITY_A}
        selectEntity={selectEntityFn}
        parameters={{}}
      />,
    );
    wrapper.find('li').simulate('click');
    expect(selectEntityFn.calledOnce).toEqual(true);
  });

  it('calls the toggleForBatchEditing function on click on .status', () => {
    hookModule.useTranslator.returns(true);
    const toggleForBatchEditingFn = sinon.spy();
    const wrapper = mount(
      <Entity
        entity={ENTITY_A}
        isReadOnlyEditor={false}
        toggleForBatchEditing={toggleForBatchEditingFn}
        parameters={{}}
      />,
    );
    wrapper.find('.status').simulate('click');
    expect(toggleForBatchEditingFn.calledOnce).toEqual(true);
  });

  it('does not call the toggleForBatchEditing function if user not translator', () => {
    const toggleForBatchEditingFn = sinon.spy();
    const selectEntityFn = sinon.spy();
    const wrapper = mount(
      <Entity
        entity={ENTITY_A}
        isReadOnlyEditor={false}
        toggleForBatchEditing={toggleForBatchEditingFn}
        selectEntity={selectEntityFn}
        parameters={{}}
      />,
    );
    wrapper.find('.status').simulate('click');
    expect(toggleForBatchEditingFn.called).toEqual(false);
  });

  it('does not call the toggleForBatchEditing function if read-only editor', () => {
    const toggleForBatchEditingFn = sinon.spy();
    const selectEntityFn = sinon.spy();
    const wrapper = mount(
      <Entity
        entity={ENTITY_A}
        isReadOnlyEditor={true}
        toggleForBatchEditing={toggleForBatchEditingFn}
        selectEntity={selectEntityFn}
        parameters={{}}
      />,
    );
    wrapper.find('.status').simulate('click');
    expect(toggleForBatchEditingFn.called).toEqual(false);
  });
});
