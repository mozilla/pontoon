/*! jQuery UI - v1.12.0 - 2016-07-27
 * http://jqueryui.com
 * Includes: widget.js, data.js, keycode.js, scroll-parent.js, widgets/sortable.js, widgets/datepicker.js, widgets/mouse.js
 * Copyright jQuery Foundation and other contributors; Licensed MIT */

(function (t) {
    'function' == typeof define && define.amd
        ? define(['jquery'], t)
        : t(jQuery);
})(function (t) {
    function e(t) {
        for (var e, i; t.length && t[0] !== document; ) {
            if (
                ((e = t.css('position')),
                ('absolute' === e || 'relative' === e || 'fixed' === e) &&
                    ((i = parseInt(t.css('zIndex'), 10)), !isNaN(i) && 0 !== i))
            )
                return i;
            t = t.parent();
        }
        return 0;
    }
    function i() {
        (this._curInst = null),
            (this._keyEvent = !1),
            (this._disabledInputs = []),
            (this._datepickerShowing = !1),
            (this._inDialog = !1),
            (this._mainDivId = 'ui-datepicker-div'),
            (this._inlineClass = 'ui-datepicker-inline'),
            (this._appendClass = 'ui-datepicker-append'),
            (this._triggerClass = 'ui-datepicker-trigger'),
            (this._dialogClass = 'ui-datepicker-dialog'),
            (this._disableClass = 'ui-datepicker-disabled'),
            (this._unselectableClass = 'ui-datepicker-unselectable'),
            (this._currentClass = 'ui-datepicker-current-day'),
            (this._dayOverClass = 'ui-datepicker-days-cell-over'),
            (this.regional = []),
            (this.regional[''] = {
                closeText: 'Done',
                prevText: 'Prev',
                nextText: 'Next',
                currentText: 'Today',
                monthNames: [
                    'January',
                    'February',
                    'March',
                    'April',
                    'May',
                    'June',
                    'July',
                    'August',
                    'September',
                    'October',
                    'November',
                    'December',
                ],
                monthNamesShort: [
                    'Jan',
                    'Feb',
                    'Mar',
                    'Apr',
                    'May',
                    'Jun',
                    'Jul',
                    'Aug',
                    'Sep',
                    'Oct',
                    'Nov',
                    'Dec',
                ],
                dayNames: [
                    'Sunday',
                    'Monday',
                    'Tuesday',
                    'Wednesday',
                    'Thursday',
                    'Friday',
                    'Saturday',
                ],
                dayNamesShort: [
                    'Sun',
                    'Mon',
                    'Tue',
                    'Wed',
                    'Thu',
                    'Fri',
                    'Sat',
                ],
                dayNamesMin: ['Su', 'Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa'],
                weekHeader: 'Wk',
                dateFormat: 'mm/dd/yy',
                firstDay: 0,
                isRTL: !1,
                showMonthAfterYear: !1,
                yearSuffix: '',
            }),
            (this._defaults = {
                showOn: 'focus',
                showAnim: 'fadeIn',
                showOptions: {},
                defaultDate: null,
                appendText: '',
                buttonText: '...',
                buttonImage: '',
                buttonImageOnly: !1,
                hideIfNoPrevNext: !1,
                navigationAsDateFormat: !1,
                gotoCurrent: !1,
                changeMonth: !1,
                changeYear: !1,
                yearRange: 'c-10:c+10',
                showOtherMonths: !1,
                selectOtherMonths: !1,
                showWeek: !1,
                calculateWeek: this.iso8601Week,
                shortYearCutoff: '+10',
                minDate: null,
                maxDate: null,
                duration: 'fast',
                beforeShowDay: null,
                beforeShow: null,
                onSelect: null,
                onChangeMonthYear: null,
                onClose: null,
                numberOfMonths: 1,
                showCurrentAtPos: 0,
                stepMonths: 1,
                stepBigMonths: 12,
                altField: '',
                altFormat: '',
                constrainInput: !0,
                showButtonPanel: !1,
                autoSize: !1,
                disabled: !1,
            }),
            t.extend(this._defaults, this.regional['']),
            (this.regional.en = t.extend(!0, {}, this.regional[''])),
            (this.regional['en-US'] = t.extend(!0, {}, this.regional.en)),
            (this.dpDiv = s(
                t(
                    "<div id='" +
                        this._mainDivId +
                        "' class='ui-datepicker ui-widget ui-widget-content ui-helper-clearfix ui-corner-all'></div>",
                ),
            ));
    }
    function s(e) {
        var i =
            'button, .ui-datepicker-prev, .ui-datepicker-next, .ui-datepicker-calendar td a';
        return e
            .on('mouseout', i, function () {
                t(this).removeClass('ui-state-hover'),
                    -1 !== this.className.indexOf('ui-datepicker-prev') &&
                        t(this).removeClass('ui-datepicker-prev-hover'),
                    -1 !== this.className.indexOf('ui-datepicker-next') &&
                        t(this).removeClass('ui-datepicker-next-hover');
            })
            .on('mouseover', i, n);
    }
    function n() {
        t.datepicker._isDisabledDatepicker(
            h.inline ? h.dpDiv.parent()[0] : h.input[0],
        ) ||
            (t(this)
                .parents('.ui-datepicker-calendar')
                .find('a')
                .removeClass('ui-state-hover'),
            t(this).addClass('ui-state-hover'),
            -1 !== this.className.indexOf('ui-datepicker-prev') &&
                t(this).addClass('ui-datepicker-prev-hover'),
            -1 !== this.className.indexOf('ui-datepicker-next') &&
                t(this).addClass('ui-datepicker-next-hover'));
    }
    function o(e, i) {
        t.extend(e, i);
        for (var s in i) null == i[s] && (e[s] = i[s]);
        return e;
    }
    (t.ui = t.ui || {}), (t.ui.version = '1.12.0');
    var a = 0,
        r = Array.prototype.slice;
    (t.cleanData = (function (e) {
        return function (i) {
            var s, n, o;
            for (o = 0; null != (n = i[o]); o++)
                try {
                    (s = t._data(n, 'events')),
                        s && s.remove && t(n).triggerHandler('remove');
                } catch (a) {}
            e(i);
        };
    })(t.cleanData)),
        (t.widget = function (e, i, s) {
            var n,
                o,
                a,
                r = {},
                l = e.split('.')[0];
            e = e.split('.')[1];
            var h = l + '-' + e;
            return (
                s || ((s = i), (i = t.Widget)),
                t.isArray(s) && (s = t.extend.apply(null, [{}].concat(s))),
                (t.expr[':'][h.toLowerCase()] = function (e) {
                    return !!t.data(e, h);
                }),
                (t[l] = t[l] || {}),
                (n = t[l][e]),
                (o = t[l][e] = function (t, e) {
                    return this._createWidget
                        ? (arguments.length && this._createWidget(t, e), void 0)
                        : new o(t, e);
                }),
                t.extend(o, n, {
                    version: s.version,
                    _proto: t.extend({}, s),
                    _childConstructors: [],
                }),
                (a = new i()),
                (a.options = t.widget.extend({}, a.options)),
                t.each(s, function (e, s) {
                    return t.isFunction(s)
                        ? ((r[e] = (function () {
                              function t() {
                                  return i.prototype[e].apply(this, arguments);
                              }
                              function n(t) {
                                  return i.prototype[e].apply(this, t);
                              }
                              return function () {
                                  var e,
                                      i = this._super,
                                      o = this._superApply;
                                  return (
                                      (this._super = t),
                                      (this._superApply = n),
                                      (e = s.apply(this, arguments)),
                                      (this._super = i),
                                      (this._superApply = o),
                                      e
                                  );
                              };
                          })()),
                          void 0)
                        : ((r[e] = s), void 0);
                }),
                (o.prototype = t.widget.extend(
                    a,
                    { widgetEventPrefix: n ? a.widgetEventPrefix || e : e },
                    r,
                    {
                        constructor: o,
                        namespace: l,
                        widgetName: e,
                        widgetFullName: h,
                    },
                )),
                n
                    ? (t.each(n._childConstructors, function (e, i) {
                          var s = i.prototype;
                          t.widget(
                              s.namespace + '.' + s.widgetName,
                              o,
                              i._proto,
                          );
                      }),
                      delete n._childConstructors)
                    : i._childConstructors.push(o),
                t.widget.bridge(e, o),
                o
            );
        }),
        (t.widget.extend = function (e) {
            for (
                var i, s, n = r.call(arguments, 1), o = 0, a = n.length;
                a > o;
                o++
            )
                for (i in n[o])
                    (s = n[o][i]),
                        n[o].hasOwnProperty(i) &&
                            void 0 !== s &&
                            (e[i] = t.isPlainObject(s)
                                ? t.isPlainObject(e[i])
                                    ? t.widget.extend({}, e[i], s)
                                    : t.widget.extend({}, s)
                                : s);
            return e;
        }),
        (t.widget.bridge = function (e, i) {
            var s = i.prototype.widgetFullName || e;
            t.fn[e] = function (n) {
                var o = 'string' == typeof n,
                    a = r.call(arguments, 1),
                    l = this;
                return (
                    o
                        ? this.each(function () {
                              var i,
                                  o = t.data(this, s);
                              return 'instance' === n
                                  ? ((l = o), !1)
                                  : o
                                  ? t.isFunction(o[n]) && '_' !== n.charAt(0)
                                      ? ((i = o[n].apply(o, a)),
                                        i !== o && void 0 !== i
                                            ? ((l =
                                                  i && i.jquery
                                                      ? l.pushStack(i.get())
                                                      : i),
                                              !1)
                                            : void 0)
                                      : t.error(
                                            "no such method '" +
                                                n +
                                                "' for " +
                                                e +
                                                ' widget instance',
                                        )
                                  : t.error(
                                        'cannot call methods on ' +
                                            e +
                                            ' prior to initialization; ' +
                                            "attempted to call method '" +
                                            n +
                                            "'",
                                    );
                          })
                        : (a.length &&
                              (n = t.widget.extend.apply(null, [n].concat(a))),
                          this.each(function () {
                              var e = t.data(this, s);
                              e
                                  ? (e.option(n || {}), e._init && e._init())
                                  : t.data(this, s, new i(n, this));
                          })),
                    l
                );
            };
        }),
        (t.Widget = function () {}),
        (t.Widget._childConstructors = []),
        (t.Widget.prototype = {
            widgetName: 'widget',
            widgetEventPrefix: '',
            defaultElement: '<div>',
            options: { classes: {}, disabled: !1, create: null },
            _createWidget: function (e, i) {
                (i = t(i || this.defaultElement || this)[0]),
                    (this.element = t(i)),
                    (this.uuid = a++),
                    (this.eventNamespace = '.' + this.widgetName + this.uuid),
                    (this.bindings = t()),
                    (this.hoverable = t()),
                    (this.focusable = t()),
                    (this.classesElementLookup = {}),
                    i !== this &&
                        (t.data(i, this.widgetFullName, this),
                        this._on(!0, this.element, {
                            remove: function (t) {
                                t.target === i && this.destroy();
                            },
                        }),
                        (this.document = t(
                            i.style ? i.ownerDocument : i.document || i,
                        )),
                        (this.window = t(
                            this.document[0].defaultView ||
                                this.document[0].parentWindow,
                        ))),
                    (this.options = t.widget.extend(
                        {},
                        this.options,
                        this._getCreateOptions(),
                        e,
                    )),
                    this._create(),
                    this.options.disabled &&
                        this._setOptionDisabled(this.options.disabled),
                    this._trigger('create', null, this._getCreateEventData()),
                    this._init();
            },
            _getCreateOptions: function () {
                return {};
            },
            _getCreateEventData: t.noop,
            _create: t.noop,
            _init: t.noop,
            destroy: function () {
                var e = this;
                this._destroy(),
                    t.each(this.classesElementLookup, function (t, i) {
                        e._removeClass(i, t);
                    }),
                    this.element
                        .off(this.eventNamespace)
                        .removeData(this.widgetFullName),
                    this.widget()
                        .off(this.eventNamespace)
                        .removeAttr('aria-disabled'),
                    this.bindings.off(this.eventNamespace);
            },
            _destroy: t.noop,
            widget: function () {
                return this.element;
            },
            option: function (e, i) {
                var s,
                    n,
                    o,
                    a = e;
                if (0 === arguments.length)
                    return t.widget.extend({}, this.options);
                if ('string' == typeof e)
                    if (
                        ((a = {}),
                        (s = e.split('.')),
                        (e = s.shift()),
                        s.length)
                    ) {
                        for (
                            n = a[e] = t.widget.extend({}, this.options[e]),
                                o = 0;
                            s.length - 1 > o;
                            o++
                        )
                            (n[s[o]] = n[s[o]] || {}), (n = n[s[o]]);
                        if (((e = s.pop()), 1 === arguments.length))
                            return void 0 === n[e] ? null : n[e];
                        n[e] = i;
                    } else {
                        if (1 === arguments.length)
                            return void 0 === this.options[e]
                                ? null
                                : this.options[e];
                        a[e] = i;
                    }
                return this._setOptions(a), this;
            },
            _setOptions: function (t) {
                var e;
                for (e in t) this._setOption(e, t[e]);
                return this;
            },
            _setOption: function (t, e) {
                return (
                    'classes' === t && this._setOptionClasses(e),
                    (this.options[t] = e),
                    'disabled' === t && this._setOptionDisabled(e),
                    this
                );
            },
            _setOptionClasses: function (e) {
                var i, s, n;
                for (i in e)
                    (n = this.classesElementLookup[i]),
                        e[i] !== this.options.classes[i] &&
                            n &&
                            n.length &&
                            ((s = t(n.get())),
                            this._removeClass(n, i),
                            s.addClass(
                                this._classes({
                                    element: s,
                                    keys: i,
                                    classes: e,
                                    add: !0,
                                }),
                            ));
            },
            _setOptionDisabled: function (t) {
                this._toggleClass(
                    this.widget(),
                    this.widgetFullName + '-disabled',
                    null,
                    !!t,
                ),
                    t &&
                        (this._removeClass(
                            this.hoverable,
                            null,
                            'ui-state-hover',
                        ),
                        this._removeClass(
                            this.focusable,
                            null,
                            'ui-state-focus',
                        ));
            },
            enable: function () {
                return this._setOptions({ disabled: !1 });
            },
            disable: function () {
                return this._setOptions({ disabled: !0 });
            },
            _classes: function (e) {
                function i(i, o) {
                    var a, r;
                    for (r = 0; i.length > r; r++)
                        (a = n.classesElementLookup[i[r]] || t()),
                            (a = e.add
                                ? t(t.unique(a.get().concat(e.element.get())))
                                : t(a.not(e.element).get())),
                            (n.classesElementLookup[i[r]] = a),
                            s.push(i[r]),
                            o && e.classes[i[r]] && s.push(e.classes[i[r]]);
                }
                var s = [],
                    n = this;
                return (
                    (e = t.extend(
                        {
                            element: this.element,
                            classes: this.options.classes || {},
                        },
                        e,
                    )),
                    e.keys && i(e.keys.match(/\S+/g) || [], !0),
                    e.extra && i(e.extra.match(/\S+/g) || []),
                    s.join(' ')
                );
            },
            _removeClass: function (t, e, i) {
                return this._toggleClass(t, e, i, !1);
            },
            _addClass: function (t, e, i) {
                return this._toggleClass(t, e, i, !0);
            },
            _toggleClass: function (t, e, i, s) {
                s = 'boolean' == typeof s ? s : i;
                var n = 'string' == typeof t || null === t,
                    o = {
                        extra: n ? e : i,
                        keys: n ? t : e,
                        element: n ? this.element : t,
                        add: s,
                    };
                return o.element.toggleClass(this._classes(o), s), this;
            },
            _on: function (e, i, s) {
                var n,
                    o = this;
                'boolean' != typeof e && ((s = i), (i = e), (e = !1)),
                    s
                        ? ((i = n = t(i)),
                          (this.bindings = this.bindings.add(i)))
                        : ((s = i), (i = this.element), (n = this.widget())),
                    t.each(s, function (s, a) {
                        function r() {
                            return e ||
                                (o.options.disabled !== !0 &&
                                    !t(this).hasClass('ui-state-disabled'))
                                ? ('string' == typeof a ? o[a] : a).apply(
                                      o,
                                      arguments,
                                  )
                                : void 0;
                        }
                        'string' != typeof a &&
                            (r.guid = a.guid = a.guid || r.guid || t.guid++);
                        var l = s.match(/^([\w:-]*)\s*(.*)$/),
                            h = l[1] + o.eventNamespace,
                            c = l[2];
                        c ? n.on(h, c, r) : i.on(h, r);
                    });
            },
            _off: function (e, i) {
                (i =
                    (i || '').split(' ').join(this.eventNamespace + ' ') +
                    this.eventNamespace),
                    e.off(i).off(i),
                    (this.bindings = t(this.bindings.not(e).get())),
                    (this.focusable = t(this.focusable.not(e).get())),
                    (this.hoverable = t(this.hoverable.not(e).get()));
            },
            _delay: function (t, e) {
                function i() {
                    return ('string' == typeof t ? s[t] : t).apply(
                        s,
                        arguments,
                    );
                }
                var s = this;
                return setTimeout(i, e || 0);
            },
            _hoverable: function (e) {
                (this.hoverable = this.hoverable.add(e)),
                    this._on(e, {
                        mouseenter: function (e) {
                            this._addClass(
                                t(e.currentTarget),
                                null,
                                'ui-state-hover',
                            );
                        },
                        mouseleave: function (e) {
                            this._removeClass(
                                t(e.currentTarget),
                                null,
                                'ui-state-hover',
                            );
                        },
                    });
            },
            _focusable: function (e) {
                (this.focusable = this.focusable.add(e)),
                    this._on(e, {
                        focusin: function (e) {
                            this._addClass(
                                t(e.currentTarget),
                                null,
                                'ui-state-focus',
                            );
                        },
                        focusout: function (e) {
                            this._removeClass(
                                t(e.currentTarget),
                                null,
                                'ui-state-focus',
                            );
                        },
                    });
            },
            _trigger: function (e, i, s) {
                var n,
                    o,
                    a = this.options[e];
                if (
                    ((s = s || {}),
                    (i = t.Event(i)),
                    (i.type = (e === this.widgetEventPrefix
                        ? e
                        : this.widgetEventPrefix + e
                    ).toLowerCase()),
                    (i.target = this.element[0]),
                    (o = i.originalEvent))
                )
                    for (n in o) n in i || (i[n] = o[n]);
                return (
                    this.element.trigger(i, s),
                    !(
                        (t.isFunction(a) &&
                            a.apply(this.element[0], [i].concat(s)) === !1) ||
                        i.isDefaultPrevented()
                    )
                );
            },
        }),
        t.each({ show: 'fadeIn', hide: 'fadeOut' }, function (e, i) {
            t.Widget.prototype['_' + e] = function (s, n, o) {
                'string' == typeof n && (n = { effect: n });
                var a,
                    r = n
                        ? n === !0 || 'number' == typeof n
                            ? i
                            : n.effect || i
                        : e;
                (n = n || {}),
                    'number' == typeof n && (n = { duration: n }),
                    (a = !t.isEmptyObject(n)),
                    (n.complete = o),
                    n.delay && s.delay(n.delay),
                    a && t.effects && t.effects.effect[r]
                        ? s[e](n)
                        : r !== e && s[r]
                        ? s[r](n.duration, n.easing, o)
                        : s.queue(function (i) {
                              t(this)[e](), o && o.call(s[0]), i();
                          });
            };
        }),
        t.widget,
        t.extend(t.expr[':'], {
            data: t.expr.createPseudo
                ? t.expr.createPseudo(function (e) {
                      return function (i) {
                          return !!t.data(i, e);
                      };
                  })
                : function (e, i, s) {
                      return !!t.data(e, s[3]);
                  },
        }),
        (t.ui.keyCode = {
            BACKSPACE: 8,
            COMMA: 188,
            DELETE: 46,
            DOWN: 40,
            END: 35,
            ENTER: 13,
            ESCAPE: 27,
            HOME: 36,
            LEFT: 37,
            PAGE_DOWN: 34,
            PAGE_UP: 33,
            PERIOD: 190,
            RIGHT: 39,
            SPACE: 32,
            TAB: 9,
            UP: 38,
        }),
        (t.fn.scrollParent = function (e) {
            var i = this.css('position'),
                s = 'absolute' === i,
                n = e ? /(auto|scroll|hidden)/ : /(auto|scroll)/,
                o = this.parents()
                    .filter(function () {
                        var e = t(this);
                        return s && 'static' === e.css('position')
                            ? !1
                            : n.test(
                                  e.css('overflow') +
                                      e.css('overflow-y') +
                                      e.css('overflow-x'),
                              );
                    })
                    .eq(0);
            return 'fixed' !== i && o.length
                ? o
                : t(this[0].ownerDocument || document);
        }),
        (t.ui.ie = !!/msie [\w.]+/.exec(navigator.userAgent.toLowerCase()));
    var l = !1;
    t(document).on('mouseup', function () {
        l = !1;
    }),
        t.widget('ui.mouse', {
            version: '1.12.0',
            options: {
                cancel: 'input, textarea, button, select, option',
                distance: 1,
                delay: 0,
            },
            _mouseInit: function () {
                var e = this;
                this.element
                    .on('mousedown.' + this.widgetName, function (t) {
                        return e._mouseDown(t);
                    })
                    .on('click.' + this.widgetName, function (i) {
                        return !0 ===
                            t.data(
                                i.target,
                                e.widgetName + '.preventClickEvent',
                            )
                            ? (t.removeData(
                                  i.target,
                                  e.widgetName + '.preventClickEvent',
                              ),
                              i.stopImmediatePropagation(),
                              !1)
                            : void 0;
                    }),
                    (this.started = !1);
            },
            _mouseDestroy: function () {
                this.element.off('.' + this.widgetName),
                    this._mouseMoveDelegate &&
                        this.document
                            .off(
                                'mousemove.' + this.widgetName,
                                this._mouseMoveDelegate,
                            )
                            .off(
                                'mouseup.' + this.widgetName,
                                this._mouseUpDelegate,
                            );
            },
            _mouseDown: function (e) {
                if (!l) {
                    (this._mouseMoved = !1),
                        this._mouseStarted && this._mouseUp(e),
                        (this._mouseDownEvent = e);
                    var i = this,
                        s = 1 === e.which,
                        n =
                            'string' == typeof this.options.cancel &&
                            e.target.nodeName
                                ? t(e.target).closest(this.options.cancel)
                                      .length
                                : !1;
                    return s && !n && this._mouseCapture(e)
                        ? ((this.mouseDelayMet = !this.options.delay),
                          this.mouseDelayMet ||
                              (this._mouseDelayTimer = setTimeout(function () {
                                  i.mouseDelayMet = !0;
                              }, this.options.delay)),
                          this._mouseDistanceMet(e) &&
                          this._mouseDelayMet(e) &&
                          ((this._mouseStarted = this._mouseStart(e) !== !1),
                          !this._mouseStarted)
                              ? (e.preventDefault(), !0)
                              : (!0 ===
                                    t.data(
                                        e.target,
                                        this.widgetName + '.preventClickEvent',
                                    ) &&
                                    t.removeData(
                                        e.target,
                                        this.widgetName + '.preventClickEvent',
                                    ),
                                (this._mouseMoveDelegate = function (t) {
                                    return i._mouseMove(t);
                                }),
                                (this._mouseUpDelegate = function (t) {
                                    return i._mouseUp(t);
                                }),
                                this.document
                                    .on(
                                        'mousemove.' + this.widgetName,
                                        this._mouseMoveDelegate,
                                    )
                                    .on(
                                        'mouseup.' + this.widgetName,
                                        this._mouseUpDelegate,
                                    ),
                                e.preventDefault(),
                                (l = !0),
                                !0))
                        : !0;
                }
            },
            _mouseMove: function (e) {
                if (this._mouseMoved) {
                    if (
                        t.ui.ie &&
                        (!document.documentMode || 9 > document.documentMode) &&
                        !e.button
                    )
                        return this._mouseUp(e);
                    if (!e.which)
                        if (
                            e.originalEvent.altKey ||
                            e.originalEvent.ctrlKey ||
                            e.originalEvent.metaKey ||
                            e.originalEvent.shiftKey
                        )
                            this.ignoreMissingWhich = !0;
                        else if (!this.ignoreMissingWhich)
                            return this._mouseUp(e);
                }
                return (
                    (e.which || e.button) && (this._mouseMoved = !0),
                    this._mouseStarted
                        ? (this._mouseDrag(e), e.preventDefault())
                        : (this._mouseDistanceMet(e) &&
                              this._mouseDelayMet(e) &&
                              ((this._mouseStarted =
                                  this._mouseStart(this._mouseDownEvent, e) !==
                                  !1),
                              this._mouseStarted
                                  ? this._mouseDrag(e)
                                  : this._mouseUp(e)),
                          !this._mouseStarted)
                );
            },
            _mouseUp: function (e) {
                this.document
                    .off(
                        'mousemove.' + this.widgetName,
                        this._mouseMoveDelegate,
                    )
                    .off('mouseup.' + this.widgetName, this._mouseUpDelegate),
                    this._mouseStarted &&
                        ((this._mouseStarted = !1),
                        e.target === this._mouseDownEvent.target &&
                            t.data(
                                e.target,
                                this.widgetName + '.preventClickEvent',
                                !0,
                            ),
                        this._mouseStop(e)),
                    this._mouseDelayTimer &&
                        (clearTimeout(this._mouseDelayTimer),
                        delete this._mouseDelayTimer),
                    (this.ignoreMissingWhich = !1),
                    (l = !1),
                    e.preventDefault();
            },
            _mouseDistanceMet: function (t) {
                return (
                    Math.max(
                        Math.abs(this._mouseDownEvent.pageX - t.pageX),
                        Math.abs(this._mouseDownEvent.pageY - t.pageY),
                    ) >= this.options.distance
                );
            },
            _mouseDelayMet: function () {
                return this.mouseDelayMet;
            },
            _mouseStart: function () {},
            _mouseDrag: function () {},
            _mouseStop: function () {},
            _mouseCapture: function () {
                return !0;
            },
        }),
        t.widget('ui.sortable', t.ui.mouse, {
            version: '1.12.0',
            widgetEventPrefix: 'sort',
            ready: !1,
            options: {
                appendTo: 'parent',
                axis: !1,
                connectWith: !1,
                containment: !1,
                cursor: 'auto',
                cursorAt: !1,
                dropOnEmpty: !0,
                forcePlaceholderSize: !1,
                forceHelperSize: !1,
                grid: !1,
                handle: !1,
                helper: 'original',
                items: '> *',
                opacity: !1,
                placeholder: !1,
                revert: !1,
                scroll: !0,
                scrollSensitivity: 20,
                scrollSpeed: 20,
                scope: 'default',
                tolerance: 'intersect',
                zIndex: 1e3,
                activate: null,
                beforeStop: null,
                change: null,
                deactivate: null,
                out: null,
                over: null,
                receive: null,
                remove: null,
                sort: null,
                start: null,
                stop: null,
                update: null,
            },
            _isOverAxis: function (t, e, i) {
                return t >= e && e + i > t;
            },
            _isFloating: function (t) {
                return (
                    /left|right/.test(t.css('float')) ||
                    /inline|table-cell/.test(t.css('display'))
                );
            },
            _create: function () {
                (this.containerCache = {}),
                    this._addClass('ui-sortable'),
                    this.refresh(),
                    (this.offset = this.element.offset()),
                    this._mouseInit(),
                    this._setHandleClassName(),
                    (this.ready = !0);
            },
            _setOption: function (t, e) {
                this._super(t, e), 'handle' === t && this._setHandleClassName();
            },
            _setHandleClassName: function () {
                var e = this;
                this._removeClass(
                    this.element.find('.ui-sortable-handle'),
                    'ui-sortable-handle',
                ),
                    t.each(this.items, function () {
                        e._addClass(
                            this.instance.options.handle
                                ? this.item.find(this.instance.options.handle)
                                : this.item,
                            'ui-sortable-handle',
                        );
                    });
            },
            _destroy: function () {
                this._mouseDestroy();
                for (var t = this.items.length - 1; t >= 0; t--)
                    this.items[t].item.removeData(this.widgetName + '-item');
                return this;
            },
            _mouseCapture: function (e, i) {
                var s = null,
                    n = !1,
                    o = this;
                return this.reverting
                    ? !1
                    : this.options.disabled || 'static' === this.options.type
                    ? !1
                    : (this._refreshItems(e),
                      t(e.target)
                          .parents()
                          .each(function () {
                              return t.data(this, o.widgetName + '-item') === o
                                  ? ((s = t(this)), !1)
                                  : void 0;
                          }),
                      t.data(e.target, o.widgetName + '-item') === o &&
                          (s = t(e.target)),
                      s
                          ? !this.options.handle ||
                            i ||
                            (t(this.options.handle, s)
                                .find('*')
                                .addBack()
                                .each(function () {
                                    this === e.target && (n = !0);
                                }),
                            n)
                              ? ((this.currentItem = s),
                                this._removeCurrentsFromItems(),
                                !0)
                              : !1
                          : !1);
            },
            _mouseStart: function (e, i, s) {
                var n,
                    o,
                    a = this.options;
                if (
                    ((this.currentContainer = this),
                    this.refreshPositions(),
                    (this.helper = this._createHelper(e)),
                    this._cacheHelperProportions(),
                    this._cacheMargins(),
                    (this.scrollParent = this.helper.scrollParent()),
                    (this.offset = this.currentItem.offset()),
                    (this.offset = {
                        top: this.offset.top - this.margins.top,
                        left: this.offset.left - this.margins.left,
                    }),
                    t.extend(this.offset, {
                        click: {
                            left: e.pageX - this.offset.left,
                            top: e.pageY - this.offset.top,
                        },
                        parent: this._getParentOffset(),
                        relative: this._getRelativeOffset(),
                    }),
                    this.helper.css('position', 'absolute'),
                    (this.cssPosition = this.helper.css('position')),
                    (this.originalPosition = this._generatePosition(e)),
                    (this.originalPageX = e.pageX),
                    (this.originalPageY = e.pageY),
                    a.cursorAt && this._adjustOffsetFromHelper(a.cursorAt),
                    (this.domPosition = {
                        prev: this.currentItem.prev()[0],
                        parent: this.currentItem.parent()[0],
                    }),
                    this.helper[0] !== this.currentItem[0] &&
                        this.currentItem.hide(),
                    this._createPlaceholder(),
                    a.containment && this._setContainment(),
                    a.cursor &&
                        'auto' !== a.cursor &&
                        ((o = this.document.find('body')),
                        (this.storedCursor = o.css('cursor')),
                        o.css('cursor', a.cursor),
                        (this.storedStylesheet = t(
                            '<style>*{ cursor: ' +
                                a.cursor +
                                ' !important; }</style>',
                        ).appendTo(o))),
                    a.opacity &&
                        (this.helper.css('opacity') &&
                            (this._storedOpacity = this.helper.css('opacity')),
                        this.helper.css('opacity', a.opacity)),
                    a.zIndex &&
                        (this.helper.css('zIndex') &&
                            (this._storedZIndex = this.helper.css('zIndex')),
                        this.helper.css('zIndex', a.zIndex)),
                    this.scrollParent[0] !== this.document[0] &&
                        'HTML' !== this.scrollParent[0].tagName &&
                        (this.overflowOffset = this.scrollParent.offset()),
                    this._trigger('start', e, this._uiHash()),
                    this._preserveHelperProportions ||
                        this._cacheHelperProportions(),
                    !s)
                )
                    for (n = this.containers.length - 1; n >= 0; n--)
                        this.containers[n]._trigger(
                            'activate',
                            e,
                            this._uiHash(this),
                        );
                return (
                    t.ui.ddmanager && (t.ui.ddmanager.current = this),
                    t.ui.ddmanager &&
                        !a.dropBehaviour &&
                        t.ui.ddmanager.prepareOffsets(this, e),
                    (this.dragging = !0),
                    this._addClass(this.helper, 'ui-sortable-helper'),
                    this._mouseDrag(e),
                    !0
                );
            },
            _mouseDrag: function (e) {
                var i,
                    s,
                    n,
                    o,
                    a = this.options,
                    r = !1;
                for (
                    this.position = this._generatePosition(e),
                        this.positionAbs = this._convertPositionTo('absolute'),
                        this.lastPositionAbs ||
                            (this.lastPositionAbs = this.positionAbs),
                        this.options.scroll &&
                            (this.scrollParent[0] !== this.document[0] &&
                            'HTML' !== this.scrollParent[0].tagName
                                ? (this.overflowOffset.top +
                                      this.scrollParent[0].offsetHeight -
                                      e.pageY <
                                  a.scrollSensitivity
                                      ? (this.scrollParent[0].scrollTop = r =
                                            this.scrollParent[0].scrollTop +
                                            a.scrollSpeed)
                                      : e.pageY - this.overflowOffset.top <
                                            a.scrollSensitivity &&
                                        (this.scrollParent[0].scrollTop = r =
                                            this.scrollParent[0].scrollTop -
                                            a.scrollSpeed),
                                  this.overflowOffset.left +
                                      this.scrollParent[0].offsetWidth -
                                      e.pageX <
                                  a.scrollSensitivity
                                      ? (this.scrollParent[0].scrollLeft = r =
                                            this.scrollParent[0].scrollLeft +
                                            a.scrollSpeed)
                                      : e.pageX - this.overflowOffset.left <
                                            a.scrollSensitivity &&
                                        (this.scrollParent[0].scrollLeft = r =
                                            this.scrollParent[0].scrollLeft -
                                            a.scrollSpeed))
                                : (e.pageY - this.document.scrollTop() <
                                  a.scrollSensitivity
                                      ? (r = this.document.scrollTop(
                                            this.document.scrollTop() -
                                                a.scrollSpeed,
                                        ))
                                      : this.window.height() -
                                            (e.pageY -
                                                this.document.scrollTop()) <
                                            a.scrollSensitivity &&
                                        (r = this.document.scrollTop(
                                            this.document.scrollTop() +
                                                a.scrollSpeed,
                                        )),
                                  e.pageX - this.document.scrollLeft() <
                                  a.scrollSensitivity
                                      ? (r = this.document.scrollLeft(
                                            this.document.scrollLeft() -
                                                a.scrollSpeed,
                                        ))
                                      : this.window.width() -
                                            (e.pageX -
                                                this.document.scrollLeft()) <
                                            a.scrollSensitivity &&
                                        (r = this.document.scrollLeft(
                                            this.document.scrollLeft() +
                                                a.scrollSpeed,
                                        ))),
                            r !== !1 &&
                                t.ui.ddmanager &&
                                !a.dropBehaviour &&
                                t.ui.ddmanager.prepareOffsets(this, e)),
                        this.positionAbs = this._convertPositionTo('absolute'),
                        (this.options.axis && 'y' === this.options.axis) ||
                            (this.helper[0].style.left =
                                this.position.left + 'px'),
                        (this.options.axis && 'x' === this.options.axis) ||
                            (this.helper[0].style.top =
                                this.position.top + 'px'),
                        i = this.items.length - 1;
                    i >= 0;
                    i--
                )
                    if (
                        ((s = this.items[i]),
                        (n = s.item[0]),
                        (o = this._intersectsWithPointer(s)),
                        o &&
                            s.instance === this.currentContainer &&
                            n !== this.currentItem[0] &&
                            this.placeholder[1 === o ? 'next' : 'prev']()[0] !==
                                n &&
                            !t.contains(this.placeholder[0], n) &&
                            ('semi-dynamic' === this.options.type
                                ? !t.contains(this.element[0], n)
                                : !0))
                    ) {
                        if (
                            ((this.direction = 1 === o ? 'down' : 'up'),
                            'pointer' !== this.options.tolerance &&
                                !this._intersectsWithSides(s))
                        )
                            break;
                        this._rearrange(e, s),
                            this._trigger('change', e, this._uiHash());
                        break;
                    }
                return (
                    this._contactContainers(e),
                    t.ui.ddmanager && t.ui.ddmanager.drag(this, e),
                    this._trigger('sort', e, this._uiHash()),
                    (this.lastPositionAbs = this.positionAbs),
                    !1
                );
            },
            _mouseStop: function (e, i) {
                if (e) {
                    if (
                        (t.ui.ddmanager &&
                            !this.options.dropBehaviour &&
                            t.ui.ddmanager.drop(this, e),
                        this.options.revert)
                    ) {
                        var s = this,
                            n = this.placeholder.offset(),
                            o = this.options.axis,
                            a = {};
                        (o && 'x' !== o) ||
                            (a.left =
                                n.left -
                                this.offset.parent.left -
                                this.margins.left +
                                (this.offsetParent[0] === this.document[0].body
                                    ? 0
                                    : this.offsetParent[0].scrollLeft)),
                            (o && 'y' !== o) ||
                                (a.top =
                                    n.top -
                                    this.offset.parent.top -
                                    this.margins.top +
                                    (this.offsetParent[0] ===
                                    this.document[0].body
                                        ? 0
                                        : this.offsetParent[0].scrollTop)),
                            (this.reverting = !0),
                            t(this.helper).animate(
                                a,
                                parseInt(this.options.revert, 10) || 500,
                                function () {
                                    s._clear(e);
                                },
                            );
                    } else this._clear(e, i);
                    return !1;
                }
            },
            cancel: function () {
                if (this.dragging) {
                    this._mouseUp({ target: null }),
                        'original' === this.options.helper
                            ? (this.currentItem.css(this._storedCSS),
                              this._removeClass(
                                  this.currentItem,
                                  'ui-sortable-helper',
                              ))
                            : this.currentItem.show();
                    for (var e = this.containers.length - 1; e >= 0; e--)
                        this.containers[e]._trigger(
                            'deactivate',
                            null,
                            this._uiHash(this),
                        ),
                            this.containers[e].containerCache.over &&
                                (this.containers[e]._trigger(
                                    'out',
                                    null,
                                    this._uiHash(this),
                                ),
                                (this.containers[e].containerCache.over = 0));
                }
                return (
                    this.placeholder &&
                        (this.placeholder[0].parentNode &&
                            this.placeholder[0].parentNode.removeChild(
                                this.placeholder[0],
                            ),
                        'original' !== this.options.helper &&
                            this.helper &&
                            this.helper[0].parentNode &&
                            this.helper.remove(),
                        t.extend(this, {
                            helper: null,
                            dragging: !1,
                            reverting: !1,
                            _noFinalSort: null,
                        }),
                        this.domPosition.prev
                            ? t(this.domPosition.prev).after(this.currentItem)
                            : t(this.domPosition.parent).prepend(
                                  this.currentItem,
                              )),
                    this
                );
            },
            serialize: function (e) {
                var i = this._getItemsAsjQuery(e && e.connected),
                    s = [];
                return (
                    (e = e || {}),
                    t(i).each(function () {
                        var i = (
                            t(e.item || this).attr(e.attribute || 'id') || ''
                        ).match(e.expression || /(.+)[\-=_](.+)/);
                        i &&
                            s.push(
                                (e.key || i[1] + '[]') +
                                    '=' +
                                    (e.key && e.expression ? i[1] : i[2]),
                            );
                    }),
                    !s.length && e.key && s.push(e.key + '='),
                    s.join('&')
                );
            },
            toArray: function (e) {
                var i = this._getItemsAsjQuery(e && e.connected),
                    s = [];
                return (
                    (e = e || {}),
                    i.each(function () {
                        s.push(
                            t(e.item || this).attr(e.attribute || 'id') || '',
                        );
                    }),
                    s
                );
            },
            _intersectsWith: function (t) {
                var e = this.positionAbs.left,
                    i = e + this.helperProportions.width,
                    s = this.positionAbs.top,
                    n = s + this.helperProportions.height,
                    o = t.left,
                    a = o + t.width,
                    r = t.top,
                    l = r + t.height,
                    h = this.offset.click.top,
                    c = this.offset.click.left,
                    u = 'x' === this.options.axis || (s + h > r && l > s + h),
                    d = 'y' === this.options.axis || (e + c > o && a > e + c),
                    p = u && d;
                return 'pointer' === this.options.tolerance ||
                    this.options.forcePointerForContainers ||
                    ('pointer' !== this.options.tolerance &&
                        this.helperProportions[
                            this.floating ? 'width' : 'height'
                        ] > t[this.floating ? 'width' : 'height'])
                    ? p
                    : e + this.helperProportions.width / 2 > o &&
                          a > i - this.helperProportions.width / 2 &&
                          s + this.helperProportions.height / 2 > r &&
                          l > n - this.helperProportions.height / 2;
            },
            _intersectsWithPointer: function (t) {
                var e,
                    i,
                    s =
                        'x' === this.options.axis ||
                        this._isOverAxis(
                            this.positionAbs.top + this.offset.click.top,
                            t.top,
                            t.height,
                        ),
                    n =
                        'y' === this.options.axis ||
                        this._isOverAxis(
                            this.positionAbs.left + this.offset.click.left,
                            t.left,
                            t.width,
                        ),
                    o = s && n;
                return o
                    ? ((e = this._getDragVerticalDirection()),
                      (i = this._getDragHorizontalDirection()),
                      this.floating
                          ? 'right' === i || 'down' === e
                              ? 2
                              : 1
                          : e && ('down' === e ? 2 : 1))
                    : !1;
            },
            _intersectsWithSides: function (t) {
                var e = this._isOverAxis(
                        this.positionAbs.top + this.offset.click.top,
                        t.top + t.height / 2,
                        t.height,
                    ),
                    i = this._isOverAxis(
                        this.positionAbs.left + this.offset.click.left,
                        t.left + t.width / 2,
                        t.width,
                    ),
                    s = this._getDragVerticalDirection(),
                    n = this._getDragHorizontalDirection();
                return this.floating && n
                    ? ('right' === n && i) || ('left' === n && !i)
                    : s && (('down' === s && e) || ('up' === s && !e));
            },
            _getDragVerticalDirection: function () {
                var t = this.positionAbs.top - this.lastPositionAbs.top;
                return 0 !== t && (t > 0 ? 'down' : 'up');
            },
            _getDragHorizontalDirection: function () {
                var t = this.positionAbs.left - this.lastPositionAbs.left;
                return 0 !== t && (t > 0 ? 'right' : 'left');
            },
            refresh: function (t) {
                return (
                    this._refreshItems(t),
                    this._setHandleClassName(),
                    this.refreshPositions(),
                    this
                );
            },
            _connectWith: function () {
                var t = this.options;
                return t.connectWith.constructor === String
                    ? [t.connectWith]
                    : t.connectWith;
            },
            _getItemsAsjQuery: function (e) {
                function i() {
                    r.push(this);
                }
                var s,
                    n,
                    o,
                    a,
                    r = [],
                    l = [],
                    h = this._connectWith();
                if (h && e)
                    for (s = h.length - 1; s >= 0; s--)
                        for (
                            o = t(h[s], this.document[0]), n = o.length - 1;
                            n >= 0;
                            n--
                        )
                            (a = t.data(o[n], this.widgetFullName)),
                                a &&
                                    a !== this &&
                                    !a.options.disabled &&
                                    l.push([
                                        t.isFunction(a.options.items)
                                            ? a.options.items.call(a.element)
                                            : t(a.options.items, a.element)
                                                  .not('.ui-sortable-helper')
                                                  .not(
                                                      '.ui-sortable-placeholder',
                                                  ),
                                        a,
                                    ]);
                for (
                    l.push([
                        t.isFunction(this.options.items)
                            ? this.options.items.call(this.element, null, {
                                  options: this.options,
                                  item: this.currentItem,
                              })
                            : t(this.options.items, this.element)
                                  .not('.ui-sortable-helper')
                                  .not('.ui-sortable-placeholder'),
                        this,
                    ]),
                        s = l.length - 1;
                    s >= 0;
                    s--
                )
                    l[s][0].each(i);
                return t(r);
            },
            _removeCurrentsFromItems: function () {
                var e = this.currentItem.find(
                    ':data(' + this.widgetName + '-item)',
                );
                this.items = t.grep(this.items, function (t) {
                    for (var i = 0; e.length > i; i++)
                        if (e[i] === t.item[0]) return !1;
                    return !0;
                });
            },
            _refreshItems: function (e) {
                (this.items = []), (this.containers = [this]);
                var i,
                    s,
                    n,
                    o,
                    a,
                    r,
                    l,
                    h,
                    c = this.items,
                    u = [
                        [
                            t.isFunction(this.options.items)
                                ? this.options.items.call(this.element[0], e, {
                                      item: this.currentItem,
                                  })
                                : t(this.options.items, this.element),
                            this,
                        ],
                    ],
                    d = this._connectWith();
                if (d && this.ready)
                    for (i = d.length - 1; i >= 0; i--)
                        for (
                            n = t(d[i], this.document[0]), s = n.length - 1;
                            s >= 0;
                            s--
                        )
                            (o = t.data(n[s], this.widgetFullName)),
                                o &&
                                    o !== this &&
                                    !o.options.disabled &&
                                    (u.push([
                                        t.isFunction(o.options.items)
                                            ? o.options.items.call(
                                                  o.element[0],
                                                  e,
                                                  { item: this.currentItem },
                                              )
                                            : t(o.options.items, o.element),
                                        o,
                                    ]),
                                    this.containers.push(o));
                for (i = u.length - 1; i >= 0; i--)
                    for (
                        a = u[i][1], r = u[i][0], s = 0, h = r.length;
                        h > s;
                        s++
                    )
                        (l = t(r[s])),
                            l.data(this.widgetName + '-item', a),
                            c.push({
                                item: l,
                                instance: a,
                                width: 0,
                                height: 0,
                                left: 0,
                                top: 0,
                            });
            },
            refreshPositions: function (e) {
                (this.floating = this.items.length
                    ? 'x' === this.options.axis ||
                      this._isFloating(this.items[0].item)
                    : !1),
                    this.offsetParent &&
                        this.helper &&
                        (this.offset.parent = this._getParentOffset());
                var i, s, n, o;
                for (i = this.items.length - 1; i >= 0; i--)
                    (s = this.items[i]),
                        (s.instance !== this.currentContainer &&
                            this.currentContainer &&
                            s.item[0] !== this.currentItem[0]) ||
                            ((n = this.options.toleranceElement
                                ? t(this.options.toleranceElement, s.item)
                                : s.item),
                            e ||
                                ((s.width = n.outerWidth()),
                                (s.height = n.outerHeight())),
                            (o = n.offset()),
                            (s.left = o.left),
                            (s.top = o.top));
                if (
                    this.options.custom &&
                    this.options.custom.refreshContainers
                )
                    this.options.custom.refreshContainers.call(this);
                else
                    for (i = this.containers.length - 1; i >= 0; i--)
                        (o = this.containers[i].element.offset()),
                            (this.containers[i].containerCache.left = o.left),
                            (this.containers[i].containerCache.top = o.top),
                            (this.containers[
                                i
                            ].containerCache.width = this.containers[
                                i
                            ].element.outerWidth()),
                            (this.containers[
                                i
                            ].containerCache.height = this.containers[
                                i
                            ].element.outerHeight());
                return this;
            },
            _createPlaceholder: function (e) {
                e = e || this;
                var i,
                    s = e.options;
                (s.placeholder && s.placeholder.constructor !== String) ||
                    ((i = s.placeholder),
                    (s.placeholder = {
                        element: function () {
                            var s = e.currentItem[0].nodeName.toLowerCase(),
                                n = t('<' + s + '>', e.document[0]);
                            return (
                                e
                                    ._addClass(
                                        n,
                                        'ui-sortable-placeholder',
                                        i || e.currentItem[0].className,
                                    )
                                    ._removeClass(n, 'ui-sortable-helper'),
                                'tbody' === s
                                    ? e._createTrPlaceholder(
                                          e.currentItem.find('tr').eq(0),
                                          t('<tr>', e.document[0]).appendTo(n),
                                      )
                                    : 'tr' === s
                                    ? e._createTrPlaceholder(e.currentItem, n)
                                    : 'img' === s &&
                                      n.attr('src', e.currentItem.attr('src')),
                                i || n.css('visibility', 'hidden'),
                                n
                            );
                        },
                        update: function (t, n) {
                            (!i || s.forcePlaceholderSize) &&
                                (n.height() ||
                                    n.height(
                                        e.currentItem.innerHeight() -
                                            parseInt(
                                                e.currentItem.css(
                                                    'paddingTop',
                                                ) || 0,
                                                10,
                                            ) -
                                            parseInt(
                                                e.currentItem.css(
                                                    'paddingBottom',
                                                ) || 0,
                                                10,
                                            ),
                                    ),
                                n.width() ||
                                    n.width(
                                        e.currentItem.innerWidth() -
                                            parseInt(
                                                e.currentItem.css(
                                                    'paddingLeft',
                                                ) || 0,
                                                10,
                                            ) -
                                            parseInt(
                                                e.currentItem.css(
                                                    'paddingRight',
                                                ) || 0,
                                                10,
                                            ),
                                    ));
                        },
                    })),
                    (e.placeholder = t(
                        s.placeholder.element.call(e.element, e.currentItem),
                    )),
                    e.currentItem.after(e.placeholder),
                    s.placeholder.update(e, e.placeholder);
            },
            _createTrPlaceholder: function (e, i) {
                var s = this;
                e.children().each(function () {
                    t('<td>&#160;</td>', s.document[0])
                        .attr('colspan', t(this).attr('colspan') || 1)
                        .appendTo(i);
                });
            },
            _contactContainers: function (e) {
                var i,
                    s,
                    n,
                    o,
                    a,
                    r,
                    l,
                    h,
                    c,
                    u,
                    d = null,
                    p = null;
                for (i = this.containers.length - 1; i >= 0; i--)
                    if (
                        !t.contains(
                            this.currentItem[0],
                            this.containers[i].element[0],
                        )
                    )
                        if (
                            this._intersectsWith(
                                this.containers[i].containerCache,
                            )
                        ) {
                            if (
                                d &&
                                t.contains(
                                    this.containers[i].element[0],
                                    d.element[0],
                                )
                            )
                                continue;
                            (d = this.containers[i]), (p = i);
                        } else
                            this.containers[i].containerCache.over &&
                                (this.containers[i]._trigger(
                                    'out',
                                    e,
                                    this._uiHash(this),
                                ),
                                (this.containers[i].containerCache.over = 0));
                if (d)
                    if (1 === this.containers.length)
                        this.containers[p].containerCache.over ||
                            (this.containers[p]._trigger(
                                'over',
                                e,
                                this._uiHash(this),
                            ),
                            (this.containers[p].containerCache.over = 1));
                    else {
                        for (
                            n = 1e4,
                                o = null,
                                c =
                                    d.floating ||
                                    this._isFloating(this.currentItem),
                                a = c ? 'left' : 'top',
                                r = c ? 'width' : 'height',
                                u = c ? 'pageX' : 'pageY',
                                s = this.items.length - 1;
                            s >= 0;
                            s--
                        )
                            t.contains(
                                this.containers[p].element[0],
                                this.items[s].item[0],
                            ) &&
                                this.items[s].item[0] !== this.currentItem[0] &&
                                ((l = this.items[s].item.offset()[a]),
                                (h = !1),
                                e[u] - l > this.items[s][r] / 2 && (h = !0),
                                n > Math.abs(e[u] - l) &&
                                    ((n = Math.abs(e[u] - l)),
                                    (o = this.items[s]),
                                    (this.direction = h ? 'up' : 'down')));
                        if (!o && !this.options.dropOnEmpty) return;
                        if (this.currentContainer === this.containers[p])
                            return (
                                this.currentContainer.containerCache.over ||
                                    (this.containers[p]._trigger(
                                        'over',
                                        e,
                                        this._uiHash(),
                                    ),
                                    (this.currentContainer.containerCache.over = 1)),
                                void 0
                            );
                        o
                            ? this._rearrange(e, o, null, !0)
                            : this._rearrange(
                                  e,
                                  null,
                                  this.containers[p].element,
                                  !0,
                              ),
                            this._trigger('change', e, this._uiHash()),
                            this.containers[p]._trigger(
                                'change',
                                e,
                                this._uiHash(this),
                            ),
                            (this.currentContainer = this.containers[p]),
                            this.options.placeholder.update(
                                this.currentContainer,
                                this.placeholder,
                            ),
                            this.containers[p]._trigger(
                                'over',
                                e,
                                this._uiHash(this),
                            ),
                            (this.containers[p].containerCache.over = 1);
                    }
            },
            _createHelper: function (e) {
                var i = this.options,
                    s = t.isFunction(i.helper)
                        ? t(
                              i.helper.apply(this.element[0], [
                                  e,
                                  this.currentItem,
                              ]),
                          )
                        : 'clone' === i.helper
                        ? this.currentItem.clone()
                        : this.currentItem;
                return (
                    s.parents('body').length ||
                        t(
                            'parent' !== i.appendTo
                                ? i.appendTo
                                : this.currentItem[0].parentNode,
                        )[0].appendChild(s[0]),
                    s[0] === this.currentItem[0] &&
                        (this._storedCSS = {
                            width: this.currentItem[0].style.width,
                            height: this.currentItem[0].style.height,
                            position: this.currentItem.css('position'),
                            top: this.currentItem.css('top'),
                            left: this.currentItem.css('left'),
                        }),
                    (!s[0].style.width || i.forceHelperSize) &&
                        s.width(this.currentItem.width()),
                    (!s[0].style.height || i.forceHelperSize) &&
                        s.height(this.currentItem.height()),
                    s
                );
            },
            _adjustOffsetFromHelper: function (e) {
                'string' == typeof e && (e = e.split(' ')),
                    t.isArray(e) && (e = { left: +e[0], top: +e[1] || 0 }),
                    'left' in e &&
                        (this.offset.click.left = e.left + this.margins.left),
                    'right' in e &&
                        (this.offset.click.left =
                            this.helperProportions.width -
                            e.right +
                            this.margins.left),
                    'top' in e &&
                        (this.offset.click.top = e.top + this.margins.top),
                    'bottom' in e &&
                        (this.offset.click.top =
                            this.helperProportions.height -
                            e.bottom +
                            this.margins.top);
            },
            _getParentOffset: function () {
                this.offsetParent = this.helper.offsetParent();
                var e = this.offsetParent.offset();
                return (
                    'absolute' === this.cssPosition &&
                        this.scrollParent[0] !== this.document[0] &&
                        t.contains(
                            this.scrollParent[0],
                            this.offsetParent[0],
                        ) &&
                        ((e.left += this.scrollParent.scrollLeft()),
                        (e.top += this.scrollParent.scrollTop())),
                    (this.offsetParent[0] === this.document[0].body ||
                        (this.offsetParent[0].tagName &&
                            'html' ===
                                this.offsetParent[0].tagName.toLowerCase() &&
                            t.ui.ie)) &&
                        (e = { top: 0, left: 0 }),
                    {
                        top:
                            e.top +
                            (parseInt(
                                this.offsetParent.css('borderTopWidth'),
                                10,
                            ) || 0),
                        left:
                            e.left +
                            (parseInt(
                                this.offsetParent.css('borderLeftWidth'),
                                10,
                            ) || 0),
                    }
                );
            },
            _getRelativeOffset: function () {
                if ('relative' === this.cssPosition) {
                    var t = this.currentItem.position();
                    return {
                        top:
                            t.top -
                            (parseInt(this.helper.css('top'), 10) || 0) +
                            this.scrollParent.scrollTop(),
                        left:
                            t.left -
                            (parseInt(this.helper.css('left'), 10) || 0) +
                            this.scrollParent.scrollLeft(),
                    };
                }
                return { top: 0, left: 0 };
            },
            _cacheMargins: function () {
                this.margins = {
                    left: parseInt(this.currentItem.css('marginLeft'), 10) || 0,
                    top: parseInt(this.currentItem.css('marginTop'), 10) || 0,
                };
            },
            _cacheHelperProportions: function () {
                this.helperProportions = {
                    width: this.helper.outerWidth(),
                    height: this.helper.outerHeight(),
                };
            },
            _setContainment: function () {
                var e,
                    i,
                    s,
                    n = this.options;
                'parent' === n.containment &&
                    (n.containment = this.helper[0].parentNode),
                    ('document' === n.containment ||
                        'window' === n.containment) &&
                        (this.containment = [
                            0 -
                                this.offset.relative.left -
                                this.offset.parent.left,
                            0 -
                                this.offset.relative.top -
                                this.offset.parent.top,
                            'document' === n.containment
                                ? this.document.width()
                                : this.window.width() -
                                  this.helperProportions.width -
                                  this.margins.left,
                            ('document' === n.containment
                                ? this.document.height() ||
                                  document.body.parentNode.scrollHeight
                                : this.window.height() ||
                                  this.document[0].body.parentNode
                                      .scrollHeight) -
                                this.helperProportions.height -
                                this.margins.top,
                        ]),
                    /^(document|window|parent)$/.test(n.containment) ||
                        ((e = t(n.containment)[0]),
                        (i = t(n.containment).offset()),
                        (s = 'hidden' !== t(e).css('overflow')),
                        (this.containment = [
                            i.left +
                                (parseInt(t(e).css('borderLeftWidth'), 10) ||
                                    0) +
                                (parseInt(t(e).css('paddingLeft'), 10) || 0) -
                                this.margins.left,
                            i.top +
                                (parseInt(t(e).css('borderTopWidth'), 10) ||
                                    0) +
                                (parseInt(t(e).css('paddingTop'), 10) || 0) -
                                this.margins.top,
                            i.left +
                                (s
                                    ? Math.max(e.scrollWidth, e.offsetWidth)
                                    : e.offsetWidth) -
                                (parseInt(t(e).css('borderLeftWidth'), 10) ||
                                    0) -
                                (parseInt(t(e).css('paddingRight'), 10) || 0) -
                                this.helperProportions.width -
                                this.margins.left,
                            i.top +
                                (s
                                    ? Math.max(e.scrollHeight, e.offsetHeight)
                                    : e.offsetHeight) -
                                (parseInt(t(e).css('borderTopWidth'), 10) ||
                                    0) -
                                (parseInt(t(e).css('paddingBottom'), 10) || 0) -
                                this.helperProportions.height -
                                this.margins.top,
                        ]));
            },
            _convertPositionTo: function (e, i) {
                i || (i = this.position);
                var s = 'absolute' === e ? 1 : -1,
                    n =
                        'absolute' !== this.cssPosition ||
                        (this.scrollParent[0] !== this.document[0] &&
                            t.contains(
                                this.scrollParent[0],
                                this.offsetParent[0],
                            ))
                            ? this.scrollParent
                            : this.offsetParent,
                    o = /(html|body)/i.test(n[0].tagName);
                return {
                    top:
                        i.top +
                        this.offset.relative.top * s +
                        this.offset.parent.top * s -
                        ('fixed' === this.cssPosition
                            ? -this.scrollParent.scrollTop()
                            : o
                            ? 0
                            : n.scrollTop()) *
                            s,
                    left:
                        i.left +
                        this.offset.relative.left * s +
                        this.offset.parent.left * s -
                        ('fixed' === this.cssPosition
                            ? -this.scrollParent.scrollLeft()
                            : o
                            ? 0
                            : n.scrollLeft()) *
                            s,
                };
            },
            _generatePosition: function (e) {
                var i,
                    s,
                    n = this.options,
                    o = e.pageX,
                    a = e.pageY,
                    r =
                        'absolute' !== this.cssPosition ||
                        (this.scrollParent[0] !== this.document[0] &&
                            t.contains(
                                this.scrollParent[0],
                                this.offsetParent[0],
                            ))
                            ? this.scrollParent
                            : this.offsetParent,
                    l = /(html|body)/i.test(r[0].tagName);
                return (
                    'relative' !== this.cssPosition ||
                        (this.scrollParent[0] !== this.document[0] &&
                            this.scrollParent[0] !== this.offsetParent[0]) ||
                        (this.offset.relative = this._getRelativeOffset()),
                    this.originalPosition &&
                        (this.containment &&
                            (e.pageX - this.offset.click.left <
                                this.containment[0] &&
                                (o =
                                    this.containment[0] +
                                    this.offset.click.left),
                            e.pageY - this.offset.click.top <
                                this.containment[1] &&
                                (a =
                                    this.containment[1] +
                                    this.offset.click.top),
                            e.pageX - this.offset.click.left >
                                this.containment[2] &&
                                (o =
                                    this.containment[2] +
                                    this.offset.click.left),
                            e.pageY - this.offset.click.top >
                                this.containment[3] &&
                                (a =
                                    this.containment[3] +
                                    this.offset.click.top)),
                        n.grid &&
                            ((i =
                                this.originalPageY +
                                Math.round(
                                    (a - this.originalPageY) / n.grid[1],
                                ) *
                                    n.grid[1]),
                            (a = this.containment
                                ? i - this.offset.click.top >=
                                      this.containment[1] &&
                                  i - this.offset.click.top <=
                                      this.containment[3]
                                    ? i
                                    : i - this.offset.click.top >=
                                      this.containment[1]
                                    ? i - n.grid[1]
                                    : i + n.grid[1]
                                : i),
                            (s =
                                this.originalPageX +
                                Math.round(
                                    (o - this.originalPageX) / n.grid[0],
                                ) *
                                    n.grid[0]),
                            (o = this.containment
                                ? s - this.offset.click.left >=
                                      this.containment[0] &&
                                  s - this.offset.click.left <=
                                      this.containment[2]
                                    ? s
                                    : s - this.offset.click.left >=
                                      this.containment[0]
                                    ? s - n.grid[0]
                                    : s + n.grid[0]
                                : s))),
                    {
                        top:
                            a -
                            this.offset.click.top -
                            this.offset.relative.top -
                            this.offset.parent.top +
                            ('fixed' === this.cssPosition
                                ? -this.scrollParent.scrollTop()
                                : l
                                ? 0
                                : r.scrollTop()),
                        left:
                            o -
                            this.offset.click.left -
                            this.offset.relative.left -
                            this.offset.parent.left +
                            ('fixed' === this.cssPosition
                                ? -this.scrollParent.scrollLeft()
                                : l
                                ? 0
                                : r.scrollLeft()),
                    }
                );
            },
            _rearrange: function (t, e, i, s) {
                i
                    ? i[0].appendChild(this.placeholder[0])
                    : e.item[0].parentNode.insertBefore(
                          this.placeholder[0],
                          'down' === this.direction
                              ? e.item[0]
                              : e.item[0].nextSibling,
                      ),
                    (this.counter = this.counter ? ++this.counter : 1);
                var n = this.counter;
                this._delay(function () {
                    n === this.counter && this.refreshPositions(!s);
                });
            },
            _clear: function (t, e) {
                function i(t, e, i) {
                    return function (s) {
                        i._trigger(t, s, e._uiHash(e));
                    };
                }
                this.reverting = !1;
                var s,
                    n = [];
                if (
                    (!this._noFinalSort &&
                        this.currentItem.parent().length &&
                        this.placeholder.before(this.currentItem),
                    (this._noFinalSort = null),
                    this.helper[0] === this.currentItem[0])
                ) {
                    for (s in this._storedCSS)
                        ('auto' === this._storedCSS[s] ||
                            'static' === this._storedCSS[s]) &&
                            (this._storedCSS[s] = '');
                    this.currentItem.css(this._storedCSS),
                        this._removeClass(
                            this.currentItem,
                            'ui-sortable-helper',
                        );
                } else this.currentItem.show();
                for (
                    this.fromOutside &&
                        !e &&
                        n.push(function (t) {
                            this._trigger(
                                'receive',
                                t,
                                this._uiHash(this.fromOutside),
                            );
                        }),
                        (!this.fromOutside &&
                            this.domPosition.prev ===
                                this.currentItem
                                    .prev()
                                    .not('.ui-sortable-helper')[0] &&
                            this.domPosition.parent ===
                                this.currentItem.parent()[0]) ||
                            e ||
                            n.push(function (t) {
                                this._trigger('update', t, this._uiHash());
                            }),
                        this !== this.currentContainer &&
                            (e ||
                                (n.push(function (t) {
                                    this._trigger('remove', t, this._uiHash());
                                }),
                                n.push(
                                    function (t) {
                                        return function (e) {
                                            t._trigger(
                                                'receive',
                                                e,
                                                this._uiHash(this),
                                            );
                                        };
                                    }.call(this, this.currentContainer),
                                ),
                                n.push(
                                    function (t) {
                                        return function (e) {
                                            t._trigger(
                                                'update',
                                                e,
                                                this._uiHash(this),
                                            );
                                        };
                                    }.call(this, this.currentContainer),
                                ))),
                        s = this.containers.length - 1;
                    s >= 0;
                    s--
                )
                    e || n.push(i('deactivate', this, this.containers[s])),
                        this.containers[s].containerCache.over &&
                            (n.push(i('out', this, this.containers[s])),
                            (this.containers[s].containerCache.over = 0));
                if (
                    (this.storedCursor &&
                        (this.document
                            .find('body')
                            .css('cursor', this.storedCursor),
                        this.storedStylesheet.remove()),
                    this._storedOpacity &&
                        this.helper.css('opacity', this._storedOpacity),
                    this._storedZIndex &&
                        this.helper.css(
                            'zIndex',
                            'auto' === this._storedZIndex
                                ? ''
                                : this._storedZIndex,
                        ),
                    (this.dragging = !1),
                    e || this._trigger('beforeStop', t, this._uiHash()),
                    this.placeholder[0].parentNode.removeChild(
                        this.placeholder[0],
                    ),
                    this.cancelHelperRemoval ||
                        (this.helper[0] !== this.currentItem[0] &&
                            this.helper.remove(),
                        (this.helper = null)),
                    !e)
                ) {
                    for (s = 0; n.length > s; s++) n[s].call(this, t);
                    this._trigger('stop', t, this._uiHash());
                }
                return (this.fromOutside = !1), !this.cancelHelperRemoval;
            },
            _trigger: function () {
                t.Widget.prototype._trigger.apply(this, arguments) === !1 &&
                    this.cancel();
            },
            _uiHash: function (e) {
                var i = e || this;
                return {
                    helper: i.helper,
                    placeholder: i.placeholder || t([]),
                    position: i.position,
                    originalPosition: i.originalPosition,
                    offset: i.positionAbs,
                    item: i.currentItem,
                    sender: e ? e.element : null,
                };
            },
        }),
        t.extend(t.ui, { datepicker: { version: '1.12.0' } });
    var h;
    t.extend(i.prototype, {
        markerClassName: 'hasDatepicker',
        maxRows: 4,
        _widgetDatepicker: function () {
            return this.dpDiv;
        },
        setDefaults: function (t) {
            return o(this._defaults, t || {}), this;
        },
        _attachDatepicker: function (e, i) {
            var s, n, o;
            (s = e.nodeName.toLowerCase()),
                (n = 'div' === s || 'span' === s),
                e.id || ((this.uuid += 1), (e.id = 'dp' + this.uuid)),
                (o = this._newInst(t(e), n)),
                (o.settings = t.extend({}, i || {})),
                'input' === s
                    ? this._connectDatepicker(e, o)
                    : n && this._inlineDatepicker(e, o);
        },
        _newInst: function (e, i) {
            var n = e[0].id.replace(/([^A-Za-z0-9_\-])/g, '\\\\$1');
            return {
                id: n,
                input: e,
                selectedDay: 0,
                selectedMonth: 0,
                selectedYear: 0,
                drawMonth: 0,
                drawYear: 0,
                inline: i,
                dpDiv: i
                    ? s(
                          t(
                              "<div class='" +
                                  this._inlineClass +
                                  " ui-datepicker ui-widget ui-widget-content ui-helper-clearfix ui-corner-all'></div>",
                          ),
                      )
                    : this.dpDiv,
            };
        },
        _connectDatepicker: function (e, i) {
            var s = t(e);
            (i.append = t([])),
                (i.trigger = t([])),
                s.hasClass(this.markerClassName) ||
                    (this._attachments(s, i),
                    s
                        .addClass(this.markerClassName)
                        .on('keydown', this._doKeyDown)
                        .on('keypress', this._doKeyPress)
                        .on('keyup', this._doKeyUp),
                    this._autoSize(i),
                    t.data(e, 'datepicker', i),
                    i.settings.disabled && this._disableDatepicker(e));
        },
        _attachments: function (e, i) {
            var s,
                n,
                o,
                a = this._get(i, 'appendText'),
                r = this._get(i, 'isRTL');
            i.append && i.append.remove(),
                a &&
                    ((i.append = t(
                        "<span class='" +
                            this._appendClass +
                            "'>" +
                            a +
                            '</span>',
                    )),
                    e[r ? 'before' : 'after'](i.append)),
                e.off('focus', this._showDatepicker),
                i.trigger && i.trigger.remove(),
                (s = this._get(i, 'showOn')),
                ('focus' === s || 'both' === s) &&
                    e.on('focus', this._showDatepicker),
                ('button' === s || 'both' === s) &&
                    ((n = this._get(i, 'buttonText')),
                    (o = this._get(i, 'buttonImage')),
                    (i.trigger = t(
                        this._get(i, 'buttonImageOnly')
                            ? t('<img/>')
                                  .addClass(this._triggerClass)
                                  .attr({ src: o, alt: n, title: n })
                            : t("<button type='button'></button>")
                                  .addClass(this._triggerClass)
                                  .html(
                                      o
                                          ? t('<img/>').attr({
                                                src: o,
                                                alt: n,
                                                title: n,
                                            })
                                          : n,
                                  ),
                    )),
                    e[r ? 'before' : 'after'](i.trigger),
                    i.trigger.on('click', function () {
                        return (
                            t.datepicker._datepickerShowing &&
                            t.datepicker._lastInput === e[0]
                                ? t.datepicker._hideDatepicker()
                                : t.datepicker._datepickerShowing &&
                                  t.datepicker._lastInput !== e[0]
                                ? (t.datepicker._hideDatepicker(),
                                  t.datepicker._showDatepicker(e[0]))
                                : t.datepicker._showDatepicker(e[0]),
                            !1
                        );
                    }));
        },
        _autoSize: function (t) {
            if (this._get(t, 'autoSize') && !t.inline) {
                var e,
                    i,
                    s,
                    n,
                    o = new Date(2009, 11, 20),
                    a = this._get(t, 'dateFormat');
                a.match(/[DM]/) &&
                    ((e = function (t) {
                        for (i = 0, s = 0, n = 0; t.length > n; n++)
                            t[n].length > i && ((i = t[n].length), (s = n));
                        return s;
                    }),
                    o.setMonth(
                        e(
                            this._get(
                                t,
                                a.match(/MM/)
                                    ? 'monthNames'
                                    : 'monthNamesShort',
                            ),
                        ),
                    ),
                    o.setDate(
                        e(
                            this._get(
                                t,
                                a.match(/DD/) ? 'dayNames' : 'dayNamesShort',
                            ),
                        ) +
                            20 -
                            o.getDay(),
                    )),
                    t.input.attr('size', this._formatDate(t, o).length);
            }
        },
        _inlineDatepicker: function (e, i) {
            var s = t(e);
            s.hasClass(this.markerClassName) ||
                (s.addClass(this.markerClassName).append(i.dpDiv),
                t.data(e, 'datepicker', i),
                this._setDate(i, this._getDefaultDate(i), !0),
                this._updateDatepicker(i),
                this._updateAlternate(i),
                i.settings.disabled && this._disableDatepicker(e),
                i.dpDiv.css('display', 'block'));
        },
        _dialogDatepicker: function (e, i, s, n, a) {
            var r,
                l,
                h,
                c,
                u,
                d = this._dialogInst;
            return (
                d ||
                    ((this.uuid += 1),
                    (r = 'dp' + this.uuid),
                    (this._dialogInput = t(
                        "<input type='text' id='" +
                            r +
                            "' style='position: absolute; top: -100px; width: 0px;'/>",
                    )),
                    this._dialogInput.on('keydown', this._doKeyDown),
                    t('body').append(this._dialogInput),
                    (d = this._dialogInst = this._newInst(
                        this._dialogInput,
                        !1,
                    )),
                    (d.settings = {}),
                    t.data(this._dialogInput[0], 'datepicker', d)),
                o(d.settings, n || {}),
                (i = i && i.constructor === Date ? this._formatDate(d, i) : i),
                this._dialogInput.val(i),
                (this._pos = a ? (a.length ? a : [a.pageX, a.pageY]) : null),
                this._pos ||
                    ((l = document.documentElement.clientWidth),
                    (h = document.documentElement.clientHeight),
                    (c =
                        document.documentElement.scrollLeft ||
                        document.body.scrollLeft),
                    (u =
                        document.documentElement.scrollTop ||
                        document.body.scrollTop),
                    (this._pos = [l / 2 - 100 + c, h / 2 - 150 + u])),
                this._dialogInput
                    .css('left', this._pos[0] + 20 + 'px')
                    .css('top', this._pos[1] + 'px'),
                (d.settings.onSelect = s),
                (this._inDialog = !0),
                this.dpDiv.addClass(this._dialogClass),
                this._showDatepicker(this._dialogInput[0]),
                t.blockUI && t.blockUI(this.dpDiv),
                t.data(this._dialogInput[0], 'datepicker', d),
                this
            );
        },
        _destroyDatepicker: function (e) {
            var i,
                s = t(e),
                n = t.data(e, 'datepicker');
            s.hasClass(this.markerClassName) &&
                ((i = e.nodeName.toLowerCase()),
                t.removeData(e, 'datepicker'),
                'input' === i
                    ? (n.append.remove(),
                      n.trigger.remove(),
                      s
                          .removeClass(this.markerClassName)
                          .off('focus', this._showDatepicker)
                          .off('keydown', this._doKeyDown)
                          .off('keypress', this._doKeyPress)
                          .off('keyup', this._doKeyUp))
                    : ('div' === i || 'span' === i) &&
                      s.removeClass(this.markerClassName).empty(),
                h === n && (h = null));
        },
        _enableDatepicker: function (e) {
            var i,
                s,
                n = t(e),
                o = t.data(e, 'datepicker');
            n.hasClass(this.markerClassName) &&
                ((i = e.nodeName.toLowerCase()),
                'input' === i
                    ? ((e.disabled = !1),
                      o.trigger
                          .filter('button')
                          .each(function () {
                              this.disabled = !1;
                          })
                          .end()
                          .filter('img')
                          .css({ opacity: '1.0', cursor: '' }))
                    : ('div' === i || 'span' === i) &&
                      ((s = n.children('.' + this._inlineClass)),
                      s.children().removeClass('ui-state-disabled'),
                      s
                          .find(
                              'select.ui-datepicker-month, select.ui-datepicker-year',
                          )
                          .prop('disabled', !1)),
                (this._disabledInputs = t.map(
                    this._disabledInputs,
                    function (t) {
                        return t === e ? null : t;
                    },
                )));
        },
        _disableDatepicker: function (e) {
            var i,
                s,
                n = t(e),
                o = t.data(e, 'datepicker');
            n.hasClass(this.markerClassName) &&
                ((i = e.nodeName.toLowerCase()),
                'input' === i
                    ? ((e.disabled = !0),
                      o.trigger
                          .filter('button')
                          .each(function () {
                              this.disabled = !0;
                          })
                          .end()
                          .filter('img')
                          .css({ opacity: '0.5', cursor: 'default' }))
                    : ('div' === i || 'span' === i) &&
                      ((s = n.children('.' + this._inlineClass)),
                      s.children().addClass('ui-state-disabled'),
                      s
                          .find(
                              'select.ui-datepicker-month, select.ui-datepicker-year',
                          )
                          .prop('disabled', !0)),
                (this._disabledInputs = t.map(
                    this._disabledInputs,
                    function (t) {
                        return t === e ? null : t;
                    },
                )),
                (this._disabledInputs[this._disabledInputs.length] = e));
        },
        _isDisabledDatepicker: function (t) {
            if (!t) return !1;
            for (var e = 0; this._disabledInputs.length > e; e++)
                if (this._disabledInputs[e] === t) return !0;
            return !1;
        },
        _getInst: function (e) {
            try {
                return t.data(e, 'datepicker');
            } catch (i) {
                throw 'Missing instance data for this datepicker';
            }
        },
        _optionDatepicker: function (e, i, s) {
            var n,
                a,
                r,
                l,
                h = this._getInst(e);
            return 2 === arguments.length && 'string' == typeof i
                ? 'defaults' === i
                    ? t.extend({}, t.datepicker._defaults)
                    : h
                    ? 'all' === i
                        ? t.extend({}, h.settings)
                        : this._get(h, i)
                    : null
                : ((n = i || {}),
                  'string' == typeof i && ((n = {}), (n[i] = s)),
                  h &&
                      (this._curInst === h && this._hideDatepicker(),
                      (a = this._getDateDatepicker(e, !0)),
                      (r = this._getMinMaxDate(h, 'min')),
                      (l = this._getMinMaxDate(h, 'max')),
                      o(h.settings, n),
                      null !== r &&
                          void 0 !== n.dateFormat &&
                          void 0 === n.minDate &&
                          (h.settings.minDate = this._formatDate(h, r)),
                      null !== l &&
                          void 0 !== n.dateFormat &&
                          void 0 === n.maxDate &&
                          (h.settings.maxDate = this._formatDate(h, l)),
                      'disabled' in n &&
                          (n.disabled
                              ? this._disableDatepicker(e)
                              : this._enableDatepicker(e)),
                      this._attachments(t(e), h),
                      this._autoSize(h),
                      this._setDate(h, a),
                      this._updateAlternate(h),
                      this._updateDatepicker(h)),
                  void 0);
        },
        _changeDatepicker: function (t, e, i) {
            this._optionDatepicker(t, e, i);
        },
        _refreshDatepicker: function (t) {
            var e = this._getInst(t);
            e && this._updateDatepicker(e);
        },
        _setDateDatepicker: function (t, e) {
            var i = this._getInst(t);
            i &&
                (this._setDate(i, e),
                this._updateDatepicker(i),
                this._updateAlternate(i));
        },
        _getDateDatepicker: function (t, e) {
            var i = this._getInst(t);
            return (
                i && !i.inline && this._setDateFromField(i, e),
                i ? this._getDate(i) : null
            );
        },
        _doKeyDown: function (e) {
            var i,
                s,
                n,
                o = t.datepicker._getInst(e.target),
                a = !0,
                r = o.dpDiv.is('.ui-datepicker-rtl');
            if (((o._keyEvent = !0), t.datepicker._datepickerShowing))
                switch (e.keyCode) {
                    case 9:
                        t.datepicker._hideDatepicker(), (a = !1);
                        break;
                    case 13:
                        return (
                            (n = t(
                                'td.' +
                                    t.datepicker._dayOverClass +
                                    ':not(.' +
                                    t.datepicker._currentClass +
                                    ')',
                                o.dpDiv,
                            )),
                            n[0] &&
                                t.datepicker._selectDay(
                                    e.target,
                                    o.selectedMonth,
                                    o.selectedYear,
                                    n[0],
                                ),
                            (i = t.datepicker._get(o, 'onSelect')),
                            i
                                ? ((s = t.datepicker._formatDate(o)),
                                  i.apply(o.input ? o.input[0] : null, [s, o]))
                                : t.datepicker._hideDatepicker(),
                            !1
                        );
                    case 27:
                        t.datepicker._hideDatepicker();
                        break;
                    case 33:
                        t.datepicker._adjustDate(
                            e.target,
                            e.ctrlKey
                                ? -t.datepicker._get(o, 'stepBigMonths')
                                : -t.datepicker._get(o, 'stepMonths'),
                            'M',
                        );
                        break;
                    case 34:
                        t.datepicker._adjustDate(
                            e.target,
                            e.ctrlKey
                                ? +t.datepicker._get(o, 'stepBigMonths')
                                : +t.datepicker._get(o, 'stepMonths'),
                            'M',
                        );
                        break;
                    case 35:
                        (e.ctrlKey || e.metaKey) &&
                            t.datepicker._clearDate(e.target),
                            (a = e.ctrlKey || e.metaKey);
                        break;
                    case 36:
                        (e.ctrlKey || e.metaKey) &&
                            t.datepicker._gotoToday(e.target),
                            (a = e.ctrlKey || e.metaKey);
                        break;
                    case 37:
                        (e.ctrlKey || e.metaKey) &&
                            t.datepicker._adjustDate(e.target, r ? 1 : -1, 'D'),
                            (a = e.ctrlKey || e.metaKey),
                            e.originalEvent.altKey &&
                                t.datepicker._adjustDate(
                                    e.target,
                                    e.ctrlKey
                                        ? -t.datepicker._get(o, 'stepBigMonths')
                                        : -t.datepicker._get(o, 'stepMonths'),
                                    'M',
                                );
                        break;
                    case 38:
                        (e.ctrlKey || e.metaKey) &&
                            t.datepicker._adjustDate(e.target, -7, 'D'),
                            (a = e.ctrlKey || e.metaKey);
                        break;
                    case 39:
                        (e.ctrlKey || e.metaKey) &&
                            t.datepicker._adjustDate(e.target, r ? -1 : 1, 'D'),
                            (a = e.ctrlKey || e.metaKey),
                            e.originalEvent.altKey &&
                                t.datepicker._adjustDate(
                                    e.target,
                                    e.ctrlKey
                                        ? +t.datepicker._get(o, 'stepBigMonths')
                                        : +t.datepicker._get(o, 'stepMonths'),
                                    'M',
                                );
                        break;
                    case 40:
                        (e.ctrlKey || e.metaKey) &&
                            t.datepicker._adjustDate(e.target, 7, 'D'),
                            (a = e.ctrlKey || e.metaKey);
                        break;
                    default:
                        a = !1;
                }
            else
                36 === e.keyCode && e.ctrlKey
                    ? t.datepicker._showDatepicker(this)
                    : (a = !1);
            a && (e.preventDefault(), e.stopPropagation());
        },
        _doKeyPress: function (e) {
            var i,
                s,
                n = t.datepicker._getInst(e.target);
            return t.datepicker._get(n, 'constrainInput')
                ? ((i = t.datepicker._possibleChars(
                      t.datepicker._get(n, 'dateFormat'),
                  )),
                  (s = String.fromCharCode(
                      null == e.charCode ? e.keyCode : e.charCode,
                  )),
                  e.ctrlKey || e.metaKey || ' ' > s || !i || i.indexOf(s) > -1)
                : void 0;
        },
        _doKeyUp: function (e) {
            var i,
                s = t.datepicker._getInst(e.target);
            if (s.input.val() !== s.lastVal)
                try {
                    (i = t.datepicker.parseDate(
                        t.datepicker._get(s, 'dateFormat'),
                        s.input ? s.input.val() : null,
                        t.datepicker._getFormatConfig(s),
                    )),
                        i &&
                            (t.datepicker._setDateFromField(s),
                            t.datepicker._updateAlternate(s),
                            t.datepicker._updateDatepicker(s));
                } catch (n) {}
            return !0;
        },
        _showDatepicker: function (i) {
            if (
                ((i = i.target || i),
                'input' !== i.nodeName.toLowerCase() &&
                    (i = t('input', i.parentNode)[0]),
                !t.datepicker._isDisabledDatepicker(i) &&
                    t.datepicker._lastInput !== i)
            ) {
                var s, n, a, r, l, h, c;
                (s = t.datepicker._getInst(i)),
                    t.datepicker._curInst &&
                        t.datepicker._curInst !== s &&
                        (t.datepicker._curInst.dpDiv.stop(!0, !0),
                        s &&
                            t.datepicker._datepickerShowing &&
                            t.datepicker._hideDatepicker(
                                t.datepicker._curInst.input[0],
                            )),
                    (n = t.datepicker._get(s, 'beforeShow')),
                    (a = n ? n.apply(i, [i, s]) : {}),
                    a !== !1 &&
                        (o(s.settings, a),
                        (s.lastVal = null),
                        (t.datepicker._lastInput = i),
                        t.datepicker._setDateFromField(s),
                        t.datepicker._inDialog && (i.value = ''),
                        t.datepicker._pos ||
                            ((t.datepicker._pos = t.datepicker._findPos(i)),
                            (t.datepicker._pos[1] += i.offsetHeight)),
                        (r = !1),
                        t(i)
                            .parents()
                            .each(function () {
                                return (
                                    (r |= 'fixed' === t(this).css('position')),
                                    !r
                                );
                            }),
                        (l = {
                            left: t.datepicker._pos[0],
                            top: t.datepicker._pos[1],
                        }),
                        (t.datepicker._pos = null),
                        s.dpDiv.empty(),
                        s.dpDiv.css({
                            position: 'absolute',
                            display: 'block',
                            top: '-1000px',
                        }),
                        t.datepicker._updateDatepicker(s),
                        (l = t.datepicker._checkOffset(s, l, r)),
                        s.dpDiv.css({
                            position:
                                t.datepicker._inDialog && t.blockUI
                                    ? 'static'
                                    : r
                                    ? 'fixed'
                                    : 'absolute',
                            display: 'none',
                            left: l.left + 'px',
                            top: l.top + 'px',
                        }),
                        s.inline ||
                            ((h = t.datepicker._get(s, 'showAnim')),
                            (c = t.datepicker._get(s, 'duration')),
                            s.dpDiv.css('z-index', e(t(i)) + 1),
                            (t.datepicker._datepickerShowing = !0),
                            t.effects && t.effects.effect[h]
                                ? s.dpDiv.show(
                                      h,
                                      t.datepicker._get(s, 'showOptions'),
                                      c,
                                  )
                                : s.dpDiv[h || 'show'](h ? c : null),
                            t.datepicker._shouldFocusInput(s) &&
                                s.input.trigger('focus'),
                            (t.datepicker._curInst = s)));
            }
        },
        _updateDatepicker: function (e) {
            (this.maxRows = 4),
                (h = e),
                e.dpDiv.empty().append(this._generateHTML(e)),
                this._attachHandlers(e);
            var i,
                s = this._getNumberOfMonths(e),
                o = s[1],
                a = 17,
                r = e.dpDiv.find('.' + this._dayOverClass + ' a');
            r.length > 0 && n.apply(r.get(0)),
                e.dpDiv
                    .removeClass(
                        'ui-datepicker-multi-2 ui-datepicker-multi-3 ui-datepicker-multi-4',
                    )
                    .width(''),
                o > 1 &&
                    e.dpDiv
                        .addClass('ui-datepicker-multi-' + o)
                        .css('width', a * o + 'em'),
                e.dpDiv[
                    (1 !== s[0] || 1 !== s[1] ? 'add' : 'remove') + 'Class'
                ]('ui-datepicker-multi'),
                e.dpDiv[(this._get(e, 'isRTL') ? 'add' : 'remove') + 'Class'](
                    'ui-datepicker-rtl',
                ),
                e === t.datepicker._curInst &&
                    t.datepicker._datepickerShowing &&
                    t.datepicker._shouldFocusInput(e) &&
                    e.input.trigger('focus'),
                e.yearshtml &&
                    ((i = e.yearshtml),
                    setTimeout(function () {
                        i === e.yearshtml &&
                            e.yearshtml &&
                            e.dpDiv
                                .find('select.ui-datepicker-year:first')
                                .replaceWith(e.yearshtml),
                            (i = e.yearshtml = null);
                    }, 0));
        },
        _shouldFocusInput: function (t) {
            return (
                t.input &&
                t.input.is(':visible') &&
                !t.input.is(':disabled') &&
                !t.input.is(':focus')
            );
        },
        _checkOffset: function (e, i, s) {
            var n = e.dpDiv.outerWidth(),
                o = e.dpDiv.outerHeight(),
                a = e.input ? e.input.outerWidth() : 0,
                r = e.input ? e.input.outerHeight() : 0,
                l =
                    document.documentElement.clientWidth +
                    (s ? 0 : t(document).scrollLeft()),
                h =
                    document.documentElement.clientHeight +
                    (s ? 0 : t(document).scrollTop());
            return (
                (i.left -= this._get(e, 'isRTL') ? n - a : 0),
                (i.left -=
                    s && i.left === e.input.offset().left
                        ? t(document).scrollLeft()
                        : 0),
                (i.top -=
                    s && i.top === e.input.offset().top + r
                        ? t(document).scrollTop()
                        : 0),
                (i.left -= Math.min(
                    i.left,
                    i.left + n > l && l > n ? Math.abs(i.left + n - l) : 0,
                )),
                (i.top -= Math.min(
                    i.top,
                    i.top + o > h && h > o ? Math.abs(o + r) : 0,
                )),
                i
            );
        },
        _findPos: function (e) {
            for (
                var i, s = this._getInst(e), n = this._get(s, 'isRTL');
                e &&
                ('hidden' === e.type ||
                    1 !== e.nodeType ||
                    t.expr.filters.hidden(e));

            )
                e = e[n ? 'previousSibling' : 'nextSibling'];
            return (i = t(e).offset()), [i.left, i.top];
        },
        _hideDatepicker: function (e) {
            var i,
                s,
                n,
                o,
                a = this._curInst;
            !a ||
                (e && a !== t.data(e, 'datepicker')) ||
                (this._datepickerShowing &&
                    ((i = this._get(a, 'showAnim')),
                    (s = this._get(a, 'duration')),
                    (n = function () {
                        t.datepicker._tidyDialog(a);
                    }),
                    t.effects && (t.effects.effect[i] || t.effects[i])
                        ? a.dpDiv.hide(
                              i,
                              t.datepicker._get(a, 'showOptions'),
                              s,
                              n,
                          )
                        : a.dpDiv[
                              'slideDown' === i
                                  ? 'slideUp'
                                  : 'fadeIn' === i
                                  ? 'fadeOut'
                                  : 'hide'
                          ](i ? s : null, n),
                    i || n(),
                    (this._datepickerShowing = !1),
                    (o = this._get(a, 'onClose')),
                    o &&
                        o.apply(a.input ? a.input[0] : null, [
                            a.input ? a.input.val() : '',
                            a,
                        ]),
                    (this._lastInput = null),
                    this._inDialog &&
                        (this._dialogInput.css({
                            position: 'absolute',
                            left: '0',
                            top: '-100px',
                        }),
                        t.blockUI &&
                            (t.unblockUI(), t('body').append(this.dpDiv))),
                    (this._inDialog = !1)));
        },
        _tidyDialog: function (t) {
            t.dpDiv
                .removeClass(this._dialogClass)
                .off('.ui-datepicker-calendar');
        },
        _checkExternalClick: function (e) {
            if (t.datepicker._curInst) {
                var i = t(e.target),
                    s = t.datepicker._getInst(i[0]);
                ((i[0].id !== t.datepicker._mainDivId &&
                    0 === i.parents('#' + t.datepicker._mainDivId).length &&
                    !i.hasClass(t.datepicker.markerClassName) &&
                    !i.closest('.' + t.datepicker._triggerClass).length &&
                    t.datepicker._datepickerShowing &&
                    (!t.datepicker._inDialog || !t.blockUI)) ||
                    (i.hasClass(t.datepicker.markerClassName) &&
                        t.datepicker._curInst !== s)) &&
                    t.datepicker._hideDatepicker();
            }
        },
        _adjustDate: function (e, i, s) {
            var n = t(e),
                o = this._getInst(n[0]);
            this._isDisabledDatepicker(n[0]) ||
                (this._adjustInstDate(
                    o,
                    i + ('M' === s ? this._get(o, 'showCurrentAtPos') : 0),
                    s,
                ),
                this._updateDatepicker(o));
        },
        _gotoToday: function (e) {
            var i,
                s = t(e),
                n = this._getInst(s[0]);
            this._get(n, 'gotoCurrent') && n.currentDay
                ? ((n.selectedDay = n.currentDay),
                  (n.drawMonth = n.selectedMonth = n.currentMonth),
                  (n.drawYear = n.selectedYear = n.currentYear))
                : ((i = new Date()),
                  (n.selectedDay = i.getDate()),
                  (n.drawMonth = n.selectedMonth = i.getMonth()),
                  (n.drawYear = n.selectedYear = i.getFullYear())),
                this._notifyChange(n),
                this._adjustDate(s);
        },
        _selectMonthYear: function (e, i, s) {
            var n = t(e),
                o = this._getInst(n[0]);
            (o['selected' + ('M' === s ? 'Month' : 'Year')] = o[
                'draw' + ('M' === s ? 'Month' : 'Year')
            ] = parseInt(i.options[i.selectedIndex].value, 10)),
                this._notifyChange(o),
                this._adjustDate(n);
        },
        _selectDay: function (e, i, s, n) {
            var o,
                a = t(e);
            t(n).hasClass(this._unselectableClass) ||
                this._isDisabledDatepicker(a[0]) ||
                ((o = this._getInst(a[0])),
                (o.selectedDay = o.currentDay = t('a', n).html()),
                (o.selectedMonth = o.currentMonth = i),
                (o.selectedYear = o.currentYear = s),
                this._selectDate(
                    e,
                    this._formatDate(
                        o,
                        o.currentDay,
                        o.currentMonth,
                        o.currentYear,
                    ),
                ));
        },
        _clearDate: function (e) {
            var i = t(e);
            this._selectDate(i, '');
        },
        _selectDate: function (e, i) {
            var s,
                n = t(e),
                o = this._getInst(n[0]);
            (i = null != i ? i : this._formatDate(o)),
                o.input && o.input.val(i),
                this._updateAlternate(o),
                (s = this._get(o, 'onSelect')),
                s
                    ? s.apply(o.input ? o.input[0] : null, [i, o])
                    : o.input && o.input.trigger('change'),
                o.inline
                    ? this._updateDatepicker(o)
                    : (this._hideDatepicker(),
                      (this._lastInput = o.input[0]),
                      'object' != typeof o.input[0] && o.input.trigger('focus'),
                      (this._lastInput = null));
        },
        _updateAlternate: function (e) {
            var i,
                s,
                n,
                o = this._get(e, 'altField');
            o &&
                ((i = this._get(e, 'altFormat') || this._get(e, 'dateFormat')),
                (s = this._getDate(e)),
                (n = this.formatDate(i, s, this._getFormatConfig(e))),
                t(o).val(n));
        },
        noWeekends: function (t) {
            var e = t.getDay();
            return [e > 0 && 6 > e, ''];
        },
        iso8601Week: function (t) {
            var e,
                i = new Date(t.getTime());
            return (
                i.setDate(i.getDate() + 4 - (i.getDay() || 7)),
                (e = i.getTime()),
                i.setMonth(0),
                i.setDate(1),
                Math.floor(Math.round((e - i) / 864e5) / 7) + 1
            );
        },
        parseDate: function (e, i, s) {
            if (null == e || null == i) throw 'Invalid arguments';
            if (((i = 'object' == typeof i ? '' + i : i + ''), '' === i))
                return null;
            var n,
                o,
                a,
                r,
                l = 0,
                h =
                    (s ? s.shortYearCutoff : null) ||
                    this._defaults.shortYearCutoff,
                c =
                    'string' != typeof h
                        ? h
                        : (new Date().getFullYear() % 100) + parseInt(h, 10),
                u =
                    (s ? s.dayNamesShort : null) ||
                    this._defaults.dayNamesShort,
                d = (s ? s.dayNames : null) || this._defaults.dayNames,
                p =
                    (s ? s.monthNamesShort : null) ||
                    this._defaults.monthNamesShort,
                f = (s ? s.monthNames : null) || this._defaults.monthNames,
                g = -1,
                m = -1,
                _ = -1,
                v = -1,
                b = !1,
                y = function (t) {
                    var i = e.length > n + 1 && e.charAt(n + 1) === t;
                    return i && n++, i;
                },
                w = function (t) {
                    var e = y(t),
                        s =
                            '@' === t
                                ? 14
                                : '!' === t
                                ? 20
                                : 'y' === t && e
                                ? 4
                                : 'o' === t
                                ? 3
                                : 2,
                        n = 'y' === t ? s : 1,
                        o = RegExp('^\\d{' + n + ',' + s + '}'),
                        a = i.substring(l).match(o);
                    if (!a) throw 'Missing number at position ' + l;
                    return (l += a[0].length), parseInt(a[0], 10);
                },
                k = function (e, s, n) {
                    var o = -1,
                        a = t
                            .map(y(e) ? n : s, function (t, e) {
                                return [[e, t]];
                            })
                            .sort(function (t, e) {
                                return -(t[1].length - e[1].length);
                            });
                    if (
                        (t.each(a, function (t, e) {
                            var s = e[1];
                            return i.substr(l, s.length).toLowerCase() ===
                                s.toLowerCase()
                                ? ((o = e[0]), (l += s.length), !1)
                                : void 0;
                        }),
                        -1 !== o)
                    )
                        return o + 1;
                    throw 'Unknown name at position ' + l;
                },
                x = function () {
                    if (i.charAt(l) !== e.charAt(n))
                        throw 'Unexpected literal at position ' + l;
                    l++;
                };
            for (n = 0; e.length > n; n++)
                if (b) "'" !== e.charAt(n) || y("'") ? x() : (b = !1);
                else
                    switch (e.charAt(n)) {
                        case 'd':
                            _ = w('d');
                            break;
                        case 'D':
                            k('D', u, d);
                            break;
                        case 'o':
                            v = w('o');
                            break;
                        case 'm':
                            m = w('m');
                            break;
                        case 'M':
                            m = k('M', p, f);
                            break;
                        case 'y':
                            g = w('y');
                            break;
                        case '@':
                            (r = new Date(w('@'))),
                                (g = r.getFullYear()),
                                (m = r.getMonth() + 1),
                                (_ = r.getDate());
                            break;
                        case '!':
                            (r = new Date((w('!') - this._ticksTo1970) / 1e4)),
                                (g = r.getFullYear()),
                                (m = r.getMonth() + 1),
                                (_ = r.getDate());
                            break;
                        case "'":
                            y("'") ? x() : (b = !0);
                            break;
                        default:
                            x();
                    }
            if (i.length > l && ((a = i.substr(l)), !/^\s+/.test(a)))
                throw 'Extra/unparsed characters found in date: ' + a;
            if (
                (-1 === g
                    ? (g = new Date().getFullYear())
                    : 100 > g &&
                      (g +=
                          new Date().getFullYear() -
                          (new Date().getFullYear() % 100) +
                          (c >= g ? 0 : -100)),
                v > -1)
            )
                for (m = 1, _ = v; ; ) {
                    if (((o = this._getDaysInMonth(g, m - 1)), o >= _)) break;
                    m++, (_ -= o);
                }
            if (
                ((r = this._daylightSavingAdjust(new Date(g, m - 1, _))),
                r.getFullYear() !== g ||
                    r.getMonth() + 1 !== m ||
                    r.getDate() !== _)
            )
                throw 'Invalid date';
            return r;
        },
        ATOM: 'yy-mm-dd',
        COOKIE: 'D, dd M yy',
        ISO_8601: 'yy-mm-dd',
        RFC_822: 'D, d M y',
        RFC_850: 'DD, dd-M-y',
        RFC_1036: 'D, d M y',
        RFC_1123: 'D, d M yy',
        RFC_2822: 'D, d M yy',
        RSS: 'D, d M y',
        TICKS: '!',
        TIMESTAMP: '@',
        W3C: 'yy-mm-dd',
        _ticksTo1970:
            1e7 *
            60 *
            60 *
            24 *
            (718685 + Math.floor(492.5) - Math.floor(19.7) + Math.floor(4.925)),
        formatDate: function (t, e, i) {
            if (!e) return '';
            var s,
                n =
                    (i ? i.dayNamesShort : null) ||
                    this._defaults.dayNamesShort,
                o = (i ? i.dayNames : null) || this._defaults.dayNames,
                a =
                    (i ? i.monthNamesShort : null) ||
                    this._defaults.monthNamesShort,
                r = (i ? i.monthNames : null) || this._defaults.monthNames,
                l = function (e) {
                    var i = t.length > s + 1 && t.charAt(s + 1) === e;
                    return i && s++, i;
                },
                h = function (t, e, i) {
                    var s = '' + e;
                    if (l(t)) for (; i > s.length; ) s = '0' + s;
                    return s;
                },
                c = function (t, e, i, s) {
                    return l(t) ? s[e] : i[e];
                },
                u = '',
                d = !1;
            if (e)
                for (s = 0; t.length > s; s++)
                    if (d)
                        "'" !== t.charAt(s) || l("'")
                            ? (u += t.charAt(s))
                            : (d = !1);
                    else
                        switch (t.charAt(s)) {
                            case 'd':
                                u += h('d', e.getDate(), 2);
                                break;
                            case 'D':
                                u += c('D', e.getDay(), n, o);
                                break;
                            case 'o':
                                u += h(
                                    'o',
                                    Math.round(
                                        (new Date(
                                            e.getFullYear(),
                                            e.getMonth(),
                                            e.getDate(),
                                        ).getTime() -
                                            new Date(
                                                e.getFullYear(),
                                                0,
                                                0,
                                            ).getTime()) /
                                            864e5,
                                    ),
                                    3,
                                );
                                break;
                            case 'm':
                                u += h('m', e.getMonth() + 1, 2);
                                break;
                            case 'M':
                                u += c('M', e.getMonth(), a, r);
                                break;
                            case 'y':
                                u += l('y')
                                    ? e.getFullYear()
                                    : (10 > e.getFullYear() % 100 ? '0' : '') +
                                      (e.getFullYear() % 100);
                                break;
                            case '@':
                                u += e.getTime();
                                break;
                            case '!':
                                u += 1e4 * e.getTime() + this._ticksTo1970;
                                break;
                            case "'":
                                l("'") ? (u += "'") : (d = !0);
                                break;
                            default:
                                u += t.charAt(s);
                        }
            return u;
        },
        _possibleChars: function (t) {
            var e,
                i = '',
                s = !1,
                n = function (i) {
                    var s = t.length > e + 1 && t.charAt(e + 1) === i;
                    return s && e++, s;
                };
            for (e = 0; t.length > e; e++)
                if (s)
                    "'" !== t.charAt(e) || n("'")
                        ? (i += t.charAt(e))
                        : (s = !1);
                else
                    switch (t.charAt(e)) {
                        case 'd':
                        case 'm':
                        case 'y':
                        case '@':
                            i += '0123456789';
                            break;
                        case 'D':
                        case 'M':
                            return null;
                        case "'":
                            n("'") ? (i += "'") : (s = !0);
                            break;
                        default:
                            i += t.charAt(e);
                    }
            return i;
        },
        _get: function (t, e) {
            return void 0 !== t.settings[e] ? t.settings[e] : this._defaults[e];
        },
        _setDateFromField: function (t, e) {
            if (t.input.val() !== t.lastVal) {
                var i = this._get(t, 'dateFormat'),
                    s = (t.lastVal = t.input ? t.input.val() : null),
                    n = this._getDefaultDate(t),
                    o = n,
                    a = this._getFormatConfig(t);
                try {
                    o = this.parseDate(i, s, a) || n;
                } catch (r) {
                    s = e ? '' : s;
                }
                (t.selectedDay = o.getDate()),
                    (t.drawMonth = t.selectedMonth = o.getMonth()),
                    (t.drawYear = t.selectedYear = o.getFullYear()),
                    (t.currentDay = s ? o.getDate() : 0),
                    (t.currentMonth = s ? o.getMonth() : 0),
                    (t.currentYear = s ? o.getFullYear() : 0),
                    this._adjustInstDate(t);
            }
        },
        _getDefaultDate: function (t) {
            return this._restrictMinMax(
                t,
                this._determineDate(t, this._get(t, 'defaultDate'), new Date()),
            );
        },
        _determineDate: function (e, i, s) {
            var n = function (t) {
                    var e = new Date();
                    return e.setDate(e.getDate() + t), e;
                },
                o = function (i) {
                    try {
                        return t.datepicker.parseDate(
                            t.datepicker._get(e, 'dateFormat'),
                            i,
                            t.datepicker._getFormatConfig(e),
                        );
                    } catch (s) {}
                    for (
                        var n =
                                (i.toLowerCase().match(/^c/)
                                    ? t.datepicker._getDate(e)
                                    : null) || new Date(),
                            o = n.getFullYear(),
                            a = n.getMonth(),
                            r = n.getDate(),
                            l = /([+\-]?[0-9]+)\s*(d|D|w|W|m|M|y|Y)?/g,
                            h = l.exec(i);
                        h;

                    ) {
                        switch (h[2] || 'd') {
                            case 'd':
                            case 'D':
                                r += parseInt(h[1], 10);
                                break;
                            case 'w':
                            case 'W':
                                r += 7 * parseInt(h[1], 10);
                                break;
                            case 'm':
                            case 'M':
                                (a += parseInt(h[1], 10)),
                                    (r = Math.min(
                                        r,
                                        t.datepicker._getDaysInMonth(o, a),
                                    ));
                                break;
                            case 'y':
                            case 'Y':
                                (o += parseInt(h[1], 10)),
                                    (r = Math.min(
                                        r,
                                        t.datepicker._getDaysInMonth(o, a),
                                    ));
                        }
                        h = l.exec(i);
                    }
                    return new Date(o, a, r);
                },
                a =
                    null == i || '' === i
                        ? s
                        : 'string' == typeof i
                        ? o(i)
                        : 'number' == typeof i
                        ? isNaN(i)
                            ? s
                            : n(i)
                        : new Date(i.getTime());
            return (
                (a = a && 'Invalid Date' == '' + a ? s : a),
                a &&
                    (a.setHours(0),
                    a.setMinutes(0),
                    a.setSeconds(0),
                    a.setMilliseconds(0)),
                this._daylightSavingAdjust(a)
            );
        },
        _daylightSavingAdjust: function (t) {
            return t
                ? (t.setHours(t.getHours() > 12 ? t.getHours() + 2 : 0), t)
                : null;
        },
        _setDate: function (t, e, i) {
            var s = !e,
                n = t.selectedMonth,
                o = t.selectedYear,
                a = this._restrictMinMax(
                    t,
                    this._determineDate(t, e, new Date()),
                );
            (t.selectedDay = t.currentDay = a.getDate()),
                (t.drawMonth = t.selectedMonth = t.currentMonth = a.getMonth()),
                (t.drawYear = t.selectedYear = t.currentYear = a.getFullYear()),
                (n === t.selectedMonth && o === t.selectedYear) ||
                    i ||
                    this._notifyChange(t),
                this._adjustInstDate(t),
                t.input && t.input.val(s ? '' : this._formatDate(t));
        },
        _getDate: function (t) {
            var e =
                !t.currentYear || (t.input && '' === t.input.val())
                    ? null
                    : this._daylightSavingAdjust(
                          new Date(t.currentYear, t.currentMonth, t.currentDay),
                      );
            return e;
        },
        _attachHandlers: function (e) {
            var i = this._get(e, 'stepMonths'),
                s = '#' + e.id.replace(/\\\\/g, '\\');
            e.dpDiv.find('[data-handler]').map(function () {
                var e = {
                    prev: function () {
                        t.datepicker._adjustDate(s, -i, 'M');
                    },
                    next: function () {
                        t.datepicker._adjustDate(s, +i, 'M');
                    },
                    hide: function () {
                        t.datepicker._hideDatepicker();
                    },
                    today: function () {
                        t.datepicker._gotoToday(s);
                    },
                    selectDay: function () {
                        return (
                            t.datepicker._selectDay(
                                s,
                                +this.getAttribute('data-month'),
                                +this.getAttribute('data-year'),
                                this,
                            ),
                            !1
                        );
                    },
                    selectMonth: function () {
                        return t.datepicker._selectMonthYear(s, this, 'M'), !1;
                    },
                    selectYear: function () {
                        return t.datepicker._selectMonthYear(s, this, 'Y'), !1;
                    },
                };
                t(this).on(
                    this.getAttribute('data-event'),
                    e[this.getAttribute('data-handler')],
                );
            });
        },
        _generateHTML: function (t) {
            var e,
                i,
                s,
                n,
                o,
                a,
                r,
                l,
                h,
                c,
                u,
                d,
                p,
                f,
                g,
                m,
                _,
                v,
                b,
                y,
                w,
                k,
                x,
                C,
                D,
                T,
                I,
                M,
                P,
                S,
                N,
                H,
                A,
                z,
                O,
                E,
                W,
                F,
                L,
                R = new Date(),
                Y = this._daylightSavingAdjust(
                    new Date(R.getFullYear(), R.getMonth(), R.getDate()),
                ),
                B = this._get(t, 'isRTL'),
                j = this._get(t, 'showButtonPanel'),
                q = this._get(t, 'hideIfNoPrevNext'),
                K = this._get(t, 'navigationAsDateFormat'),
                U = this._getNumberOfMonths(t),
                V = this._get(t, 'showCurrentAtPos'),
                X = this._get(t, 'stepMonths'),
                $ = 1 !== U[0] || 1 !== U[1],
                G = this._daylightSavingAdjust(
                    t.currentDay
                        ? new Date(t.currentYear, t.currentMonth, t.currentDay)
                        : new Date(9999, 9, 9),
                ),
                J = this._getMinMaxDate(t, 'min'),
                Q = this._getMinMaxDate(t, 'max'),
                Z = t.drawMonth - V,
                te = t.drawYear;
            if ((0 > Z && ((Z += 12), te--), Q))
                for (
                    e = this._daylightSavingAdjust(
                        new Date(
                            Q.getFullYear(),
                            Q.getMonth() - U[0] * U[1] + 1,
                            Q.getDate(),
                        ),
                    ),
                        e = J && J > e ? J : e;
                    this._daylightSavingAdjust(new Date(te, Z, 1)) > e;

                )
                    Z--, 0 > Z && ((Z = 11), te--);
            for (
                t.drawMonth = Z,
                    t.drawYear = te,
                    i = this._get(t, 'prevText'),
                    i = K
                        ? this.formatDate(
                              i,
                              this._daylightSavingAdjust(
                                  new Date(te, Z - X, 1),
                              ),
                              this._getFormatConfig(t),
                          )
                        : i,
                    s = this._canAdjustMonth(t, -1, te, Z)
                        ? "<a class='ui-datepicker-prev ui-corner-all' data-handler='prev' data-event='click' title='" +
                          i +
                          "'><span class='ui-icon ui-icon-circle-triangle-" +
                          (B ? 'e' : 'w') +
                          "'>" +
                          i +
                          '</span></a>'
                        : q
                        ? ''
                        : "<a class='ui-datepicker-prev ui-corner-all ui-state-disabled' title='" +
                          i +
                          "'><span class='ui-icon ui-icon-circle-triangle-" +
                          (B ? 'e' : 'w') +
                          "'>" +
                          i +
                          '</span></a>',
                    n = this._get(t, 'nextText'),
                    n = K
                        ? this.formatDate(
                              n,
                              this._daylightSavingAdjust(
                                  new Date(te, Z + X, 1),
                              ),
                              this._getFormatConfig(t),
                          )
                        : n,
                    o = this._canAdjustMonth(t, 1, te, Z)
                        ? "<a class='ui-datepicker-next ui-corner-all' data-handler='next' data-event='click' title='" +
                          n +
                          "'><span class='ui-icon ui-icon-circle-triangle-" +
                          (B ? 'w' : 'e') +
                          "'>" +
                          n +
                          '</span></a>'
                        : q
                        ? ''
                        : "<a class='ui-datepicker-next ui-corner-all ui-state-disabled' title='" +
                          n +
                          "'><span class='ui-icon ui-icon-circle-triangle-" +
                          (B ? 'w' : 'e') +
                          "'>" +
                          n +
                          '</span></a>',
                    a = this._get(t, 'currentText'),
                    r = this._get(t, 'gotoCurrent') && t.currentDay ? G : Y,
                    a = K ? this.formatDate(a, r, this._getFormatConfig(t)) : a,
                    l = t.inline
                        ? ''
                        : "<button type='button' class='ui-datepicker-close ui-state-default ui-priority-primary ui-corner-all' data-handler='hide' data-event='click'>" +
                          this._get(t, 'closeText') +
                          '</button>',
                    h = j
                        ? "<div class='ui-datepicker-buttonpane ui-widget-content'>" +
                          (B ? l : '') +
                          (this._isInRange(t, r)
                              ? "<button type='button' class='ui-datepicker-current ui-state-default ui-priority-secondary ui-corner-all' data-handler='today' data-event='click'>" +
                                a +
                                '</button>'
                              : '') +
                          (B ? '' : l) +
                          '</div>'
                        : '',
                    c = parseInt(this._get(t, 'firstDay'), 10),
                    c = isNaN(c) ? 0 : c,
                    u = this._get(t, 'showWeek'),
                    d = this._get(t, 'dayNames'),
                    p = this._get(t, 'dayNamesMin'),
                    f = this._get(t, 'monthNames'),
                    g = this._get(t, 'monthNamesShort'),
                    m = this._get(t, 'beforeShowDay'),
                    _ = this._get(t, 'showOtherMonths'),
                    v = this._get(t, 'selectOtherMonths'),
                    b = this._getDefaultDate(t),
                    y = '',
                    k = 0;
                U[0] > k;
                k++
            ) {
                for (x = '', this.maxRows = 4, C = 0; U[1] > C; C++) {
                    if (
                        ((D = this._daylightSavingAdjust(
                            new Date(te, Z, t.selectedDay),
                        )),
                        (T = ' ui-corner-all'),
                        (I = ''),
                        $)
                    ) {
                        if (
                            ((I += "<div class='ui-datepicker-group"), U[1] > 1)
                        )
                            switch (C) {
                                case 0:
                                    (I += ' ui-datepicker-group-first'),
                                        (T =
                                            ' ui-corner-' +
                                            (B ? 'right' : 'left'));
                                    break;
                                case U[1] - 1:
                                    (I += ' ui-datepicker-group-last'),
                                        (T =
                                            ' ui-corner-' +
                                            (B ? 'left' : 'right'));
                                    break;
                                default:
                                    (I += ' ui-datepicker-group-middle'),
                                        (T = '');
                            }
                        I += "'>";
                    }
                    for (
                        I +=
                            "<div class='ui-datepicker-header ui-widget-header ui-helper-clearfix" +
                            T +
                            "'>" +
                            (/all|left/.test(T) && 0 === k ? (B ? o : s) : '') +
                            (/all|right/.test(T) && 0 === k
                                ? B
                                    ? s
                                    : o
                                : '') +
                            this._generateMonthYearHeader(
                                t,
                                Z,
                                te,
                                J,
                                Q,
                                k > 0 || C > 0,
                                f,
                                g,
                            ) +
                            "</div><table class='ui-datepicker-calendar'><thead>" +
                            '<tr>',
                            M = u
                                ? "<th class='ui-datepicker-week-col'>" +
                                  this._get(t, 'weekHeader') +
                                  '</th>'
                                : '',
                            w = 0;
                        7 > w;
                        w++
                    )
                        (P = (w + c) % 7),
                            (M +=
                                "<th scope='col'" +
                                ((w + c + 6) % 7 >= 5
                                    ? " class='ui-datepicker-week-end'"
                                    : '') +
                                '>' +
                                "<span title='" +
                                d[P] +
                                "'>" +
                                p[P] +
                                '</span></th>');
                    for (
                        I += M + '</tr></thead><tbody>',
                            S = this._getDaysInMonth(te, Z),
                            te === t.selectedYear &&
                                Z === t.selectedMonth &&
                                (t.selectedDay = Math.min(t.selectedDay, S)),
                            N = (this._getFirstDayOfMonth(te, Z) - c + 7) % 7,
                            H = Math.ceil((N + S) / 7),
                            A = $ ? (this.maxRows > H ? this.maxRows : H) : H,
                            this.maxRows = A,
                            z = this._daylightSavingAdjust(
                                new Date(te, Z, 1 - N),
                            ),
                            O = 0;
                        A > O;
                        O++
                    ) {
                        for (
                            I += '<tr>',
                                E = u
                                    ? "<td class='ui-datepicker-week-col'>" +
                                      this._get(t, 'calculateWeek')(z) +
                                      '</td>'
                                    : '',
                                w = 0;
                            7 > w;
                            w++
                        )
                            (W = m
                                ? m.apply(t.input ? t.input[0] : null, [z])
                                : [!0, '']),
                                (F = z.getMonth() !== Z),
                                (L =
                                    (F && !v) ||
                                    !W[0] ||
                                    (J && J > z) ||
                                    (Q && z > Q)),
                                (E +=
                                    "<td class='" +
                                    ((w + c + 6) % 7 >= 5
                                        ? ' ui-datepicker-week-end'
                                        : '') +
                                    (F ? ' ui-datepicker-other-month' : '') +
                                    ((z.getTime() === D.getTime() &&
                                        Z === t.selectedMonth &&
                                        t._keyEvent) ||
                                    (b.getTime() === z.getTime() &&
                                        b.getTime() === D.getTime())
                                        ? ' ' + this._dayOverClass
                                        : '') +
                                    (L
                                        ? ' ' +
                                          this._unselectableClass +
                                          ' ui-state-disabled'
                                        : '') +
                                    (F && !_
                                        ? ''
                                        : ' ' +
                                          W[1] +
                                          (z.getTime() === G.getTime()
                                              ? ' ' + this._currentClass
                                              : '') +
                                          (z.getTime() === Y.getTime()
                                              ? ' ui-datepicker-today'
                                              : '')) +
                                    "'" +
                                    ((F && !_) || !W[2]
                                        ? ''
                                        : " title='" +
                                          W[2].replace(/'/g, '&#39;') +
                                          "'") +
                                    (L
                                        ? ''
                                        : " data-handler='selectDay' data-event='click' data-month='" +
                                          z.getMonth() +
                                          "' data-year='" +
                                          z.getFullYear() +
                                          "'") +
                                    '>' +
                                    (F && !_
                                        ? '&#xa0;'
                                        : L
                                        ? "<span class='ui-state-default'>" +
                                          z.getDate() +
                                          '</span>'
                                        : "<a class='ui-state-default" +
                                          (z.getTime() === Y.getTime()
                                              ? ' ui-state-highlight'
                                              : '') +
                                          (z.getTime() === G.getTime()
                                              ? ' ui-state-active'
                                              : '') +
                                          (F ? ' ui-priority-secondary' : '') +
                                          "' href='#'>" +
                                          z.getDate() +
                                          '</a>') +
                                    '</td>'),
                                z.setDate(z.getDate() + 1),
                                (z = this._daylightSavingAdjust(z));
                        I += E + '</tr>';
                    }
                    Z++,
                        Z > 11 && ((Z = 0), te++),
                        (I +=
                            '</tbody></table>' +
                            ($
                                ? '</div>' +
                                  (U[0] > 0 && C === U[1] - 1
                                      ? "<div class='ui-datepicker-row-break'></div>"
                                      : '')
                                : '')),
                        (x += I);
                }
                y += x;
            }
            return (y += h), (t._keyEvent = !1), y;
        },
        _generateMonthYearHeader: function (t, e, i, s, n, o, a, r) {
            var l,
                h,
                c,
                u,
                d,
                p,
                f,
                g,
                m = this._get(t, 'changeMonth'),
                _ = this._get(t, 'changeYear'),
                v = this._get(t, 'showMonthAfterYear'),
                b = "<div class='ui-datepicker-title'>",
                y = '';
            if (o || !m)
                y += "<span class='ui-datepicker-month'>" + a[e] + '</span>';
            else {
                for (
                    l = s && s.getFullYear() === i,
                        h = n && n.getFullYear() === i,
                        y +=
                            "<select class='ui-datepicker-month' data-handler='selectMonth' data-event='change'>",
                        c = 0;
                    12 > c;
                    c++
                )
                    (!l || c >= s.getMonth()) &&
                        (!h || n.getMonth() >= c) &&
                        (y +=
                            "<option value='" +
                            c +
                            "'" +
                            (c === e ? " selected='selected'" : '') +
                            '>' +
                            r[c] +
                            '</option>');
                y += '</select>';
            }
            if ((v || (b += y + (!o && m && _ ? '' : '&#xa0;')), !t.yearshtml))
                if (((t.yearshtml = ''), o || !_))
                    b += "<span class='ui-datepicker-year'>" + i + '</span>';
                else {
                    for (
                        u = this._get(t, 'yearRange').split(':'),
                            d = new Date().getFullYear(),
                            p = function (t) {
                                var e = t.match(/c[+\-].*/)
                                    ? i + parseInt(t.substring(1), 10)
                                    : t.match(/[+\-].*/)
                                    ? d + parseInt(t, 10)
                                    : parseInt(t, 10);
                                return isNaN(e) ? d : e;
                            },
                            f = p(u[0]),
                            g = Math.max(f, p(u[1] || '')),
                            f = s ? Math.max(f, s.getFullYear()) : f,
                            g = n ? Math.min(g, n.getFullYear()) : g,
                            t.yearshtml +=
                                "<select class='ui-datepicker-year' data-handler='selectYear' data-event='change'>";
                        g >= f;
                        f++
                    )
                        t.yearshtml +=
                            "<option value='" +
                            f +
                            "'" +
                            (f === i ? " selected='selected'" : '') +
                            '>' +
                            f +
                            '</option>';
                    (t.yearshtml += '</select>'),
                        (b += t.yearshtml),
                        (t.yearshtml = null);
                }
            return (
                (b += this._get(t, 'yearSuffix')),
                v && (b += (!o && m && _ ? '' : '&#xa0;') + y),
                (b += '</div>')
            );
        },
        _adjustInstDate: function (t, e, i) {
            var s = t.selectedYear + ('Y' === i ? e : 0),
                n = t.selectedMonth + ('M' === i ? e : 0),
                o =
                    Math.min(t.selectedDay, this._getDaysInMonth(s, n)) +
                    ('D' === i ? e : 0),
                a = this._restrictMinMax(
                    t,
                    this._daylightSavingAdjust(new Date(s, n, o)),
                );
            (t.selectedDay = a.getDate()),
                (t.drawMonth = t.selectedMonth = a.getMonth()),
                (t.drawYear = t.selectedYear = a.getFullYear()),
                ('M' === i || 'Y' === i) && this._notifyChange(t);
        },
        _restrictMinMax: function (t, e) {
            var i = this._getMinMaxDate(t, 'min'),
                s = this._getMinMaxDate(t, 'max'),
                n = i && i > e ? i : e;
            return s && n > s ? s : n;
        },
        _notifyChange: function (t) {
            var e = this._get(t, 'onChangeMonthYear');
            e &&
                e.apply(t.input ? t.input[0] : null, [
                    t.selectedYear,
                    t.selectedMonth + 1,
                    t,
                ]);
        },
        _getNumberOfMonths: function (t) {
            var e = this._get(t, 'numberOfMonths');
            return null == e ? [1, 1] : 'number' == typeof e ? [1, e] : e;
        },
        _getMinMaxDate: function (t, e) {
            return this._determineDate(t, this._get(t, e + 'Date'), null);
        },
        _getDaysInMonth: function (t, e) {
            return (
                32 - this._daylightSavingAdjust(new Date(t, e, 32)).getDate()
            );
        },
        _getFirstDayOfMonth: function (t, e) {
            return new Date(t, e, 1).getDay();
        },
        _canAdjustMonth: function (t, e, i, s) {
            var n = this._getNumberOfMonths(t),
                o = this._daylightSavingAdjust(
                    new Date(i, s + (0 > e ? e : n[0] * n[1]), 1),
                );
            return (
                0 > e &&
                    o.setDate(
                        this._getDaysInMonth(o.getFullYear(), o.getMonth()),
                    ),
                this._isInRange(t, o)
            );
        },
        _isInRange: function (t, e) {
            var i,
                s,
                n = this._getMinMaxDate(t, 'min'),
                o = this._getMinMaxDate(t, 'max'),
                a = null,
                r = null,
                l = this._get(t, 'yearRange');
            return (
                l &&
                    ((i = l.split(':')),
                    (s = new Date().getFullYear()),
                    (a = parseInt(i[0], 10)),
                    (r = parseInt(i[1], 10)),
                    i[0].match(/[+\-].*/) && (a += s),
                    i[1].match(/[+\-].*/) && (r += s)),
                (!n || e.getTime() >= n.getTime()) &&
                    (!o || e.getTime() <= o.getTime()) &&
                    (!a || e.getFullYear() >= a) &&
                    (!r || r >= e.getFullYear())
            );
        },
        _getFormatConfig: function (t) {
            var e = this._get(t, 'shortYearCutoff');
            return (
                (e =
                    'string' != typeof e
                        ? e
                        : (new Date().getFullYear() % 100) + parseInt(e, 10)),
                {
                    shortYearCutoff: e,
                    dayNamesShort: this._get(t, 'dayNamesShort'),
                    dayNames: this._get(t, 'dayNames'),
                    monthNamesShort: this._get(t, 'monthNamesShort'),
                    monthNames: this._get(t, 'monthNames'),
                }
            );
        },
        _formatDate: function (t, e, i, s) {
            e ||
                ((t.currentDay = t.selectedDay),
                (t.currentMonth = t.selectedMonth),
                (t.currentYear = t.selectedYear));
            var n = e
                ? 'object' == typeof e
                    ? e
                    : this._daylightSavingAdjust(new Date(s, i, e))
                : this._daylightSavingAdjust(
                      new Date(t.currentYear, t.currentMonth, t.currentDay),
                  );
            return this.formatDate(
                this._get(t, 'dateFormat'),
                n,
                this._getFormatConfig(t),
            );
        },
    }),
        (t.fn.datepicker = function (e) {
            if (!this.length) return this;
            t.datepicker.initialized ||
                (t(document).on('mousedown', t.datepicker._checkExternalClick),
                (t.datepicker.initialized = !0)),
                0 === t('#' + t.datepicker._mainDivId).length &&
                    t('body').append(t.datepicker.dpDiv);
            var i = Array.prototype.slice.call(arguments, 1);
            return 'string' != typeof e ||
                ('isDisabled' !== e && 'getDate' !== e && 'widget' !== e)
                ? 'option' === e &&
                  2 === arguments.length &&
                  'string' == typeof arguments[1]
                    ? t.datepicker['_' + e + 'Datepicker'].apply(
                          t.datepicker,
                          [this[0]].concat(i),
                      )
                    : this.each(function () {
                          'string' == typeof e
                              ? t.datepicker['_' + e + 'Datepicker'].apply(
                                    t.datepicker,
                                    [this].concat(i),
                                )
                              : t.datepicker._attachDatepicker(this, e);
                      })
                : t.datepicker['_' + e + 'Datepicker'].apply(
                      t.datepicker,
                      [this[0]].concat(i),
                  );
        }),
        (t.datepicker = new i()),
        (t.datepicker.initialized = !1),
        (t.datepicker.uuid = new Date().getTime()),
        (t.datepicker.version = '1.12.0'),
        t.datepicker;
});
