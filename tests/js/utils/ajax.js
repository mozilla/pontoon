import { DjangoAjax, PontoonDjangoAjax, ajax } from 'utils/ajax';

test('PontoonDjangoAjax instance', () => {
    expect(ajax instanceof DjangoAjax).toBe(true);
    expect(ajax instanceof PontoonDjangoAjax).toBe(true);
});

test('DjangoAjax csrf', () => {
    // Not implemented
    const _ajax = new DjangoAjax();
    expect(() => {
        _ajax.csrf;
    }).toThrow(Error);
});

test('PontoonDjangoAjax csrf', () => {
    const _ajax = new PontoonDjangoAjax();
    document.querySelector = jest.fn(() => ({ value: 'rhubarb' }));
    expect(_ajax.csrf).toBe('rhubarb');
    expect(document.querySelector.mock.calls).toEqual([
        ['input[name=csrfmiddlewaretoken]'],
    ]);
});

test('PontoonDjangoAjax headers', () => {
    const _ajax = new PontoonDjangoAjax();
    document.querySelector = jest.fn(() => ({ value: 'crumble' }));
    window.Headers = jest.fn(() => ({ 'X-Foo-Header': 'bar' }));
    expect(_ajax.headers).toEqual({ 'X-Foo-Header': 'bar' });
    expect(window.Headers.mock.calls).toEqual([
        [
            {
                Accept: 'application/json',
                'X-CSRFToken': 'crumble',
                'X-Requested-With': 'XMLHttpRequest',
            },
        ],
    ]);
});

test('PontoonDjangoAjax asGetParams', () => {
    const _ajax = new PontoonDjangoAjax();
    const parameters = { append: jest.fn() };
    window.URLSearchParams = jest.fn(() => parameters);
    expect(_ajax.asGetParams({ foo: 7, bar: 23, baz: 43 })).toBe(parameters);
    expect(parameters.append.mock.calls).toEqual([
        ['foo', 7],
        ['bar', 23],
        ['baz', 43],
    ]);
});

test('PontoonDjangoAjax asMultipartForm', () => {
    const _ajax = new PontoonDjangoAjax();
    const parameters = { append: jest.fn() };
    window.FormData = jest.fn(() => parameters);
    expect(_ajax.asMultipartForm({ foo: 17, bar: 73, baz: 117 })).toBe(
        parameters,
    );
    expect(parameters.append.mock.calls).toEqual([
        ['foo', 17],
        ['bar', 73],
        ['baz', 117],
    ]);
});

test('PontoonDjangoAjax isSameOrigin', () => {
    const _ajax = new PontoonDjangoAjax();
    // default url is set to https://nowhere.com/at/all
    expect(_ajax.isSameOrigin('https://somwhere.else/all/together')).toBe(
        false,
    );
    expect(_ajax.isSameOrigin('https://somwhere.else/')).toBe(false);
    expect(_ajax.isSameOrigin('http://somwhere.else/')).toBe(false);
    expect(_ajax.isSameOrigin('//somwhere.else/')).toBe(false);
    expect(_ajax.isSameOrigin('http://nowhere.com/')).toBe(false);
    expect(_ajax.isSameOrigin('http://nowhere.com/like/this')).toBe(false);
    expect(_ajax.isSameOrigin('https://nowhere.org/and/this')).toBe(false);
    expect(_ajax.isSameOrigin('https://nowhere.org')).toBe(false);

    expect(_ajax.isSameOrigin('https://nowhere.com/but/this')).toBe(true);
    expect(_ajax.isSameOrigin('https://nowhere.com/and/this')).toBe(true);
    expect(_ajax.isSameOrigin('https://nowhere.com/')).toBe(true);
    expect(_ajax.isSameOrigin('https://nowhere.com')).toBe(true);
    expect(_ajax.isSameOrigin('//nowhere.com/or/this')).toBe(true);
    expect(_ajax.isSameOrigin('/else/this')).toBe(true);
    expect(_ajax.isSameOrigin('even/this')).toBe(true);
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
    expect(_ajax.isSameOrigin('https://nowhere.com/but/this')).toBe(false);
    expect(_ajax.isSameOrigin('https://nowhere.com/and/this')).toBe(false);
    expect(_ajax.isSameOrigin('https://nowhere.com/')).toBe(false);
    expect(_ajax.isSameOrigin('https://nowhere.com')).toBe(false);
    expect(_ajax.isSameOrigin('//nowhere.com/or/this')).toBe(false);
    expect(_ajax.isSameOrigin('https://nowhere.com:2323')).toBe(true);
    expect(_ajax.isSameOrigin('//nowhere.com:2323/or/this')).toBe(true);
    expect(_ajax.isSameOrigin('/still/this')).toBe(true);
    expect(_ajax.isSameOrigin('and/even/this')).toBe(true);
});

test('PontoonDjangoAjax credentials', () => {
    const _ajax = new PontoonDjangoAjax();
    _ajax.isSameOrigin = jest.fn(() => true);
    expect(_ajax.getCredentials('X')).toBe('same-origin');
    expect(_ajax.isSameOrigin.mock.calls).toEqual([['X']]);
    _ajax.isSameOrigin = jest.fn(() => false);
    expect(_ajax.getCredentials('Y')).toBe(undefined);
    expect(_ajax.isSameOrigin.mock.calls).toEqual([['Y']]);
});

test('PontoonDjangoAjax getRequest', () => {
    const _ajax = new PontoonDjangoAjax();
    _ajax.getCredentials = jest.fn(() => 23);
    window.Headers = jest.fn(() => ({ 'X-Bar-Header': 'baz' }));
    expect(_ajax.getRequest('x.com', { foo: 'foo0' })).toEqual({
        credentials: 23,
        foo: 'foo0',
        headers: { 'X-Bar-Header': 'baz' },
    });
});

test('PontoonDjangoAjax fetch', () => {
    const _ajax = new PontoonDjangoAjax();

    // default method is get
    _ajax.get = jest.fn(() => 13);
    _ajax.post = jest.fn(() => 11);
    expect(_ajax.fetch('foo.bar', { some: 'data' }, { other: 117 })).toBe(13);
    expect(_ajax.get.mock.calls).toEqual([
        ['foo.bar', { some: 'data' }, { other: 117 }],
    ]);
    expect(_ajax.post.mock.calls).toEqual([]);

    // get
    _ajax.get = jest.fn(() => 7);
    _ajax.post = jest.fn(() => 23);
    expect(
        _ajax.fetch('foo.bar', { some: 'data' }, { method: 'get', other: 117 }),
    ).toBe(7);
    expect(_ajax.get.mock.calls).toEqual([
        ['foo.bar', { some: 'data' }, { method: 'get', other: 117 }],
    ]);
    expect(_ajax.post.mock.calls).toEqual([]);

    // post
    _ajax.get = jest.fn(() => 7);
    _ajax.post = jest.fn(() => 23);
    expect(
        _ajax.fetch('foo.bar', { some: 'data' }, { method: 'post', other: 43 }),
    ).toBe(23);
    expect(_ajax.get.mock.calls).toEqual([]);
    expect(_ajax.post.mock.calls).toEqual([
        ['foo.bar', { some: 'data' }, { method: 'post', other: 43 }],
    ]);
});

test('PontoonDjangoAjax fetch bad method', () => {
    const _ajax = new PontoonDjangoAjax();
    expect(() => {
        _ajax.fetch('foo.bar', {}, { method: 'baz' });
    }).toThrow(Error);
});

test('PontoonDjangoAjax get', () => {
    const _ajax = new PontoonDjangoAjax();
    _ajax.asGetParams = jest.fn(() => 17);
    _ajax.getRequest = jest.fn(() => 43);
    window.fetch = jest.fn(() => 73);
    expect(_ajax.get('foo', 'bar', { baz: 13 })).toBe(73);
    expect(_ajax.asGetParams.mock.calls).toEqual([['bar']]);
    expect(_ajax.getRequest.mock.calls).toEqual([
        ['foo', { baz: 13, method: 'GET', params: 17 }],
    ]);
    expect(window.fetch.mock.calls).toEqual([['foo', 43]]);
});

test('PontoonDjangoAjax post', () => {
    const _ajax = new PontoonDjangoAjax();
    _ajax.asMultipartForm = jest.fn(() => 17);
    _ajax.getRequest = jest.fn(() => 43);
    window.fetch = jest.fn(() => 73);
    document.querySelector = jest.fn(() => ({ value: '37' }));
    expect(_ajax.post('foo', { bar: 11 }, { baz: 13 })).toBe(73);
    expect(_ajax.asMultipartForm.mock.calls).toEqual([
        [{ bar: 11, csrfmiddlewaretoken: '37' }],
    ]);
    expect(_ajax.getRequest.mock.calls).toEqual([
        ['foo', { baz: 13, body: 17, method: 'POST' }],
    ]);
    expect(window.fetch.mock.calls).toEqual([['foo', 43]]);
});

test('PontoonDjangoAjax appendParams', () => {
    const _ajax = new PontoonDjangoAjax();
    let container = { append: jest.fn(() => 111) };
    expect(_ajax.appendParams(container, { foo: 3, bar: 7 })).toBe(container);
    expect(container.append.mock.calls).toEqual([
        ['foo', 3],
        ['bar', 7],
    ]);
    container = { append: jest.fn(() => 111) };
    expect(_ajax.appendParams(container, { foo: 3, bar: [1, 3, 7] })).toBe(
        container,
    );
    expect(container.append.mock.calls).toEqual([
        ['foo', 3],
        ['bar', 1],
        ['bar', 3],
        ['bar', 7],
    ]);
});
