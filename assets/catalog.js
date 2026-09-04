(function () {
    'use strict';
    const roots = Array.from(document.querySelectorAll('[data-catalog]'));
    if (!roots.length) return;
    const valid = (key, value) => {
        if (key === 'q') return (value || '').slice(0,160);
        if (key === 'category') return ['all','learning','music','creating','games','culture','travel','tools'].includes(value) ? value : 'all';
        if (key === 'platform') return ['all','iphone','ipad','mac','vision','tv'].includes(value) ? value : 'all';
        if (key === 'price') return ['all','paid','free'].includes(value) ? value : 'all';
        return ['recommended','updated','name'].includes(value) ? value : 'recommended';
    };
    const normalise = text => text.normalize('NFKC').toLowerCase().replace(/\s+/g,' ').trim();
    let state = {};
    function fromURL() {
        const p = new URLSearchParams(location.search);
        ['q','category','platform','price','sort'].forEach(key => state[key] = valid(key,p.get(key)));
    }
    function query() {
        const p = new URLSearchParams();
        Object.entries(state).forEach(([key,value]) => { if (value && value !== 'all' && value !== 'recommended') p.set(key,value); });
        return p;
    }
    function render() {
        const words = normalise(state.q).split(' ').filter(Boolean);
        roots.forEach(root => {
            const lang = root.dataset.catalog;
            const items = Array.from(root.querySelectorAll('[data-catalog-card]'));
            const list = root.querySelector('[data-results]');
            const form = root.querySelector('form');
            ['q','platform','price','sort'].forEach(key => { if (form.elements[key].value !== state[key]) form.elements[key].value = state[key]; });
            const matchesBase = card => words.every(word => normalise(card.dataset.search).includes(word)) && (state.platform === 'all' || card.dataset.platforms.split(' ').includes(state.platform)) && (state.price === 'all' || (state.price === 'paid' ? card.dataset.price === 'paid' : card.dataset.price !== 'paid'));
            root.querySelectorAll('[data-category]').forEach(button => {
                const id = button.dataset.category;
                const count = items.filter(card => matchesBase(card) && (id === 'all' || card.dataset.categories.split(' ').includes(id))).length;
                button.setAttribute('aria-pressed', String(state.category === id));
                button.querySelector('[data-count]').textContent = count;
            });
            items.sort((a,b) => state.sort === 'updated' ? b.dataset.updated.localeCompare(a.dataset.updated) || Number(a.dataset.rank)-Number(b.dataset.rank) : state.sort === 'name' ? a.dataset.name.localeCompare(b.dataset.name,lang === 'zh' ? 'zh-Hant' : 'en') : Number(a.dataset.rank)-Number(b.dataset.rank));
            let count = 0;
            items.forEach(card => {
                card.hidden = !(matchesBase(card) && (state.category === 'all' || card.dataset.categories.split(' ').includes(state.category)));
                if (!card.hidden) count++;
                list.appendChild(card);
                card.querySelectorAll('[data-product-link]').forEach(link => {
                    const url = new URL(link.getAttribute('href'),location.href);
                    url.searchParams.set('lang',lang);
                    url.searchParams.set('browse',query().toString());
                    link.href = url.pathname + url.search;
                });
            });
            root.querySelector('[data-result-count]').textContent = lang === 'zh' ? '找到 '+count+' 款 App' : count+' '+(count === 1 ? 'app' : 'apps')+' found';
            root.querySelector('[data-empty]').hidden = count !== 0;
            root.querySelectorAll('[data-reset]').forEach(button => button.hidden = !state.q && state.category === 'all' && state.platform === 'all' && state.price === 'all' && state.sort === 'recommended');
            root.querySelectorAll('[data-collection]').forEach(el => el.hidden = state.category !== el.dataset.collection);
        });
    }
    function update(push) {
        const url = new URL(location.href), p = query();
        p.set('lang',document.documentElement.dataset.language || 'zh');
        const target = url.pathname + '?' + p.toString();
        if (target !== location.pathname+location.search) history[push ? 'pushState' : 'replaceState'](null,'',target);
        render();
    }
    roots.forEach(root => {
        const form = root.querySelector('form');
        form.addEventListener('submit', e => { e.preventDefault(); state.q=valid('q',form.elements.q.value);update(true); });
        form.elements.q.addEventListener('input', () => { state.q=valid('q',form.elements.q.value);update(false); });
        ['platform','price','sort'].forEach(key => form.elements[key].addEventListener('change', () => {state[key]=valid(key,form.elements[key].value);update(true);}));
        root.querySelectorAll('[data-category]').forEach(button => button.addEventListener('click', () => {state.category=button.dataset.category;update(true);}));
        root.querySelectorAll('[data-reset]').forEach(button => button.addEventListener('click', () => {state={q:'',category:'all',platform:'all',price:'all',sort:'recommended'};update(true);form.elements.q.focus();}));
    });
    window.addEventListener('popstate', () => {fromURL();render();});
    document.addEventListener('languagechange', render);
    fromURL();render();
    if (location.hash.startsWith('#card-')) requestAnimationFrame(() => { const card=document.getElementById(location.hash.slice(1)); if(card && !card.hidden) card.scrollIntoView({block:'start'}); });
})();
