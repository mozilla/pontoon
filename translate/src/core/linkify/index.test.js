import React from 'react';
import { shallow } from 'enzyme';
import { Linkify, getImageURLs } from '.';

describe('Linkify', () => {
  it('renders links as expected on plain text', () => {
    const wrapper = shallow(
      <Linkify>See pontoon.mozilla.org for more.</Linkify>,
    );
    const links = wrapper.find('a');
    expect(links.length).toBe(1);
    const link = links.at(0);
    expect(link.text()).toBe('pontoon.mozilla.org');
    expect(link.prop('href')).toBe('http://pontoon.mozilla.org');
    expect(link.prop('target')).toBeUndefined();
  });
  it('sets rel and target', () => {
    const wrapper = shallow(
      <Linkify
        properties={{
          target: '_blank',
          rel: 'noopener noreferrer',
        }}
      >
        more pontoon.mozilla.org content
      </Linkify>,
    );
    const links = wrapper.find('a');
    expect(links.length).toBe(1);
    const link = links.at(0);
    expect(link.text()).toBe('pontoon.mozilla.org');
    expect(link.prop('href')).toBe('http://pontoon.mozilla.org');
    expect(link.prop('target')).toBe('_blank');
    expect(link.prop('rel')).toContain('noopener');
    expect(link.prop('rel')).toContain('noreferrer');
  });
  it('leaves existing links alone', () => {
    const wrapper = shallow(
      <Linkify>
        more <a href='https://example.com'>pontoon.mozilla.org</a> content
      </Linkify>,
    );
    const links = wrapper.find('a');
    expect(links.length).toBe(1);
    const link = links.at(0);
    expect(link.text()).toBe('pontoon.mozilla.org');
    expect(link.prop('href')).toBe('https://example.com');
  });
});

describe('getImageURLs', () => {
  it('finds an image when there is an image URL in the source', () => {
    const source = 'That is an image URL: http://link.to/image.png';
    const urls = getImageURLs(source);

    expect(urls).toEqual(['http://link.to/image.png']);
  });

  it('finds several images', () => {
    const source = `
            Here we have 2 images: http://link.to/image.png
            and https://example.org/test.jpg
        `;
    const urls = getImageURLs(source);

    const expectedURLs = [
      'http://link.to/image.png',
      'https://example.org/test.jpg',
    ];

    expect(urls).toEqual(expectedURLs);
  });

  it('does not find non PNG or JPG images', () => {
    const source =
      'That is a non-supported image URL: http://link.to/image.bmp';
    const urls = getImageURLs(source);

    expect(urls).toHaveLength(0);
  });

  it('does not find non image links', () => {
    const source = 'That is not an image URL: http://link.to/image.php';
    const urls = getImageURLs(source);

    expect(urls).toHaveLength(0);
  });

  it('does returns an empty array when no URLs are found', () => {
    const source = 'That is not interesting at all';
    const urls = getImageURLs(source);

    expect(urls).toHaveLength(0);
  });
});
