const Sections = {
    init(rootSel) {
        this.root = document.querySelector(rootSel);
        this.nav = null;
        this.sections = this.root.querySelectorAll('[id^=section-]');
        this.activeSectionIdx = 0;

        this._initKeyboard();
        this._initWheel();
        this._render();
    },

    goToNext() {
        this.goTo(
            Math.min(this.activeSectionIdx + 1, this.sections.length - 1),
        );
    },

    goToPrev() {
        this.goTo(Math.max(this.activeSectionIdx - 1, 0));
    },

    goTo(idx) {
        if (idx !== this.activeSectionIdx) {
            this.activeSectionIdx = idx;
            this.navigate();
        }
    },

    navigate() {
        requestAnimationFrame(() => {
            const section = this.sections[this.activeSectionIdx];
            section.scrollIntoView({
                behavior: 'smooth',
                block: 'nearest',
            });
            this._render();
        });
    },

    _initKeyboard() {
        document.addEventListener('keydown', (e) => {
            if (e.keyCode === 38) {
                this.goToPrev();
            }

            if (e.keyCode === 40) {
                this.goToNext();
            }
        });
    },

    _initWheel() {
        let samples = [];
        let lastScroll = new Date().getTime();
        // Disable scrollbars
        document.body.style.overflow = 'hidden';

        const avg = (numbers, count) => {
            let sum = 0;
            for (let i = 0; i < count && i < numbers.length; i++) {
                const idx = numbers.length - i - 1;
                sum += numbers[idx];
            }
            return Math.ceil(sum / count);
        };

        document.addEventListener(
            'wheel',
            (e) => {
                if (samples.length >= 50) {
                    samples.shift();
                }
                samples.push(Math.abs(e.deltaY));

                const now = new Date().getTime();
                const elapsed = now - lastScroll;
                // Too fast!
                if (elapsed < 550) {
                    return;
                }

                // Higher recent sample values mean scroll now happens faster
                const isAccelerating = avg(samples, 10) >= avg(samples, 50);
                if (!isAccelerating) {
                    return;
                }

                // Record the current scroll and restart measuring the next time
                lastScroll = new Date().getTime();
                samples = [];

                if (e.deltaY < 0) {
                    this.goToPrev();
                } else if (0 < e.deltaY) {
                    this.goToNext();
                }
            },
            { passive: true },
        );
    },

    _renderNav() {
        const nav = document.createElement('nav');
        nav.id = 'sections';
        const ul = document.createElement('ul');
        this.sections.forEach((section, idx) => {
            const li = document.createElement('li');
            const a = document.createElement('a');
            const span = document.createElement('span');
            a.className = 'js-section-nav';
            a.onclick = (e) => {
                e.preventDefault();
                this.goTo(idx);
            };
            a.appendChild(span);
            li.appendChild(a);
            ul.appendChild(li);
        });

        nav.appendChild(ul);
        this.root.appendChild(nav);

        return nav;
    },

    _render() {
        if (!this.nav) {
            this.nav = this._renderNav();
        }

        const navElements = this.nav.querySelectorAll('.js-section-nav');
        navElements.forEach((el, idx) =>
            el.classList.toggle('active', idx === this.activeSectionIdx),
        );
    },
};

$(function () {
    Sections.init('#main');

    // Scroll from Section 1 to Section 2
    $('#section-1 .footer .scroll').on('click', function (e) {
        e.preventDefault();
        Sections.goToNext();
    });

    // Show/hide header border on menu open/close
    $('body > header').on('click', '.selector', function () {
        if (!$(this).siblings('.menu').is(':visible')) {
            $('body > header').addClass('menu-opened');
        }
    });
    $('body').bind('click.main', function () {
        $('body > header').removeClass('menu-opened');
    });
});
