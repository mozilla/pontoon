import { isSameOrigin, post } from './http-post.js';

test('isSameOrigin', () => {
  // default url is set to https://nowhere.com/at/all
  expect(isSameOrigin('https://somwhere.else/all/together')).toBe(false);
  expect(isSameOrigin('https://somwhere.else/')).toBe(false);
  expect(isSameOrigin('http://somwhere.else/')).toBe(false);
  expect(isSameOrigin('//somwhere.else/')).toBe(false);
  expect(isSameOrigin('http://nowhere.com/')).toBe(false);
  expect(isSameOrigin('http://nowhere.com/like/this')).toBe(false);
  expect(isSameOrigin('https://nowhere.org/and/this')).toBe(false);
  expect(isSameOrigin('https://nowhere.org')).toBe(false);

  expect(isSameOrigin('https://nowhere.com/but/this')).toBe(true);
  expect(isSameOrigin('https://nowhere.com/and/this')).toBe(true);
  expect(isSameOrigin('https://nowhere.com/')).toBe(true);
  expect(isSameOrigin('https://nowhere.com')).toBe(true);
  expect(isSameOrigin('//nowhere.com/or/this')).toBe(true);
  expect(isSameOrigin('/else/this')).toBe(true);
  expect(isSameOrigin('even/this')).toBe(true);

  Object.defineProperty(window, 'location', {
    writable: true,
    value: {
      href: 'https://nowhere.com:2323/some/where',
      protocol: 'https:',
      hostname: 'nowhere.com',
      host: 'nowhere.com:2323',
      port: '2323',
    },
  });

  expect(isSameOrigin('https://nowhere.com/but/this')).toBe(false);
  expect(isSameOrigin('https://nowhere.com/and/this')).toBe(false);
  expect(isSameOrigin('https://nowhere.com/')).toBe(false);
  expect(isSameOrigin('https://nowhere.com')).toBe(false);
  expect(isSameOrigin('//nowhere.com/or/this')).toBe(false);
  expect(isSameOrigin('https://nowhere.com:2323')).toBe(true);
  expect(isSameOrigin('//nowhere.com:2323/or/this')).toBe(true);
  expect(isSameOrigin('/still/this')).toBe(true);
  expect(isSameOrigin('and/even/this')).toBe(true);
});

test('http post', () => {
  window.fetch = jest.fn(() => 73);
  document.querySelector = jest.fn(() => ({ value: '37' }));
  expect(post('foo', { bar: 11 })).toBe(73);

  const { calls } = window.fetch.mock;
  expect(calls).toMatchObject([
    ['foo', { credentials: 'same-origin', method: 'POST' }],
  ]);
  expect(document.querySelector.mock.calls).toEqual([
    ['input[name=csrfmiddlewaretoken]'],
  ]);

  const { body, headers } = calls[0][1];
  expect(Array.from(body.entries())).toMatchObject([
    ['bar', '11'],
    ['csrfmiddlewaretoken', '37'],
  ]);
  expect(Array.from(headers.entries())).toMatchObject([
    ['accept', 'application/json'],
    ['x-csrftoken', '37'],
    ['x-requested-with', 'XMLHttpRequest'],
  ]);
});
