import React from 'react';
import { mount } from 'enzyme';
import { MockLocalizationProvider } from '~/test/utils';
import { Highlight } from './Highlight';

const mountMarker = (content, terms = []) =>
  mount(
    <MockLocalizationProvider>
      <Highlight terms={terms}>{content}</Highlight>
    </MockLocalizationProvider>,
  );

describe('Test parser order', () => {
  it('matches JSON placeholder', () => {
    const content = 'You have created $COUNT$ aliases';
    const wrapper = mountMarker(content);

    expect(wrapper.find('mark')).toHaveLength(1);
    expect(wrapper.find('mark').text()).toContain('$COUNT$');
  });
});

describe('mark terms', () => {
  it('marks terms properly', () => {
    const string = 'foo bar baz';
    const terms = {
      terms: [{ text: 'bar' }, { text: 'baz' }],
    };

    const wrapper = mountMarker(string, terms);

    expect(wrapper.find('mark')).toHaveLength(2);
    expect(wrapper.find('mark').at(0).text()).toEqual('bar');
    expect(wrapper.find('mark').at(1).text()).toEqual('baz');
  });

  it('marks entire words on partial match', () => {
    const string = 'Download Add-Ons from the web.';
    const terms = {
      terms: [{ text: 'add-on' }],
    };

    const wrapper = mountMarker(string, terms);

    const mark = wrapper.find('mark');
    expect(mark).toHaveLength(1);
    expect(mark.text()).toEqual('Add-Ons');
    expect(mark.prop('data-match')).toEqual('add-on');
  });

  it('only marks terms at the beginning of the word', () => {
    const string = 'Consider using one of the alternatives.';
    const terms = {
      terms: [{ text: 'native' }],
    };

    const wrapper = mountMarker(string, terms);

    expect(wrapper.find('mark')).toHaveLength(0);
  });

  it('marks longer terms first', () => {
    const string = 'This is a translation tool.';
    const terms = {
      terms: [{ text: 'translation' }, { text: 'translation tool' }],
    };

    const wrapper = mountMarker(string, terms);

    expect(wrapper.find('mark')).toHaveLength(1);
    expect(wrapper.find('mark').text()).toEqual('translation tool');
  });

  it('does not mark terms within placeables', () => {
    const string =
      'This browser { $version } does not support { $bits }-bit systems.';
    const terms = {
      terms: [{ text: 'browser' }, { text: 'version' }],
    };

    const wrapper = mountMarker(string, terms);

    expect(wrapper.find('mark')).toHaveLength(3);
    expect(wrapper.find('mark').at(0).text()).toEqual('browser');
    expect(wrapper.find('mark').at(0).hasClass('term'));
    expect(wrapper.find('mark').at(1).text()).toEqual('{ $version }');
    expect(wrapper.find('mark').at(1).hasClass('placeable'));
    expect(wrapper.find('mark').at(2).text()).toEqual('{ $bits }');
    expect(wrapper.find('mark').at(2).hasClass('placeable'));
  });
});
