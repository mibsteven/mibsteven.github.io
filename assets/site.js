(function () {
    'use strict';
    const words = {
        zh: {brandRole:'為學習、創作與空間體驗打造的 Apple App',navApps:'探索 App',navUpdates:'最新動態',navSupport:'關於與支援',navPrivacy:'隱私權',navTerms:'條款',footerText:'Apps by Yu-Hsiang Chang · 為 iPhone、iPad、Mac 與 Apple Vision Pro 打造的獨立作品。',privacyPolicy:'隱私權政策',termsUse:'使用條款',support:'支援'},
        en: {brandRole:'Independent Apple apps for learning, creating, and exploring',navApps:'Explore apps',navUpdates:'Updates',navSupport:'About & support',navPrivacy:'Privacy',navTerms:'Terms',footerText:'Apps by Yu-Hsiang Chang · Independent apps for iPhone, iPad, Mac, and Apple Vision Pro.',privacyPolicy:'Privacy Policy',termsUse:'Terms of Use',support:'Support'}
    };
    const params = new URLSearchParams(location.search);
    function savedLanguage() { try { return localStorage.getItem('preferredLanguage'); } catch (_) { return null; } }
    function setLanguage(value, updateURL) {
        const lang = value === 'en' ? 'en' : 'zh';
        document.documentElement.lang = lang === 'zh' ? 'zh-Hant' : 'en';
        document.documentElement.dataset.language = lang;
        document.querySelectorAll('[data-lang-panel]').forEach(el => el.classList.toggle('is-active', el.dataset.langPanel === lang));
        document.querySelectorAll('[data-i18n]').forEach(el => { if (words[lang][el.dataset.i18n]) el.textContent = words[lang][el.dataset.i18n]; });
        document.querySelectorAll('[data-lang]').forEach(el => el.setAttribute('aria-pressed', String(el.dataset.lang === lang)));
        const title = document.querySelector('[data-title-zh]');
        if (title) document.title = lang === 'zh' ? title.dataset.titleZh : title.dataset.titleEn;
        try { localStorage.setItem('preferredLanguage', lang); } catch (_) { /* Reading must work with storage blocked. */ }
        if (updateURL) {
            const url = new URL(location.href); url.searchParams.set('lang', lang);
            history.replaceState(null, '', url.pathname + url.search + url.hash);
        }
        document.querySelectorAll('a[href]').forEach(link => {
            const url = new URL(link.getAttribute('href'), location.href);
            if (url.origin !== location.origin || !url.pathname.endsWith('.html')) return;
            if (link.getAttribute('href').startsWith('#')) return;
            url.searchParams.set('lang', lang);
            link.setAttribute('href', url.pathname + url.search + url.hash);
        });
        document.dispatchEvent(new CustomEvent('languagechange', {detail:{lang}}));
    }
    window.siteLanguage = {set: setLanguage};
    document.querySelectorAll('[data-lang]').forEach(button => button.addEventListener('click', () => setLanguage(button.dataset.lang, true)));
    const requested = params.get('lang');
    setLanguage(requested === 'zh' || requested === 'en' ? requested : savedLanguage() || (navigator.language.toLowerCase().startsWith('zh') ? 'zh' : 'en'), false);
    window.addEventListener('popstate', () => {
        const lang = new URLSearchParams(location.search).get('lang');
        if (lang === 'zh' || lang === 'en') setLanguage(lang, false);
    });
    // Only restore known catalogue parameters. Never redirect to a supplied URL.
    const browse = params.get('browse');
    function restoreCatalogLinks() {
        if (browse === null) return;
        const received = new URLSearchParams(browse);
        const clean = new URLSearchParams();
        ['q','category','platform','price','sort'].forEach(key => { if (received.has(key)) clean.set(key, received.get(key)); });
        document.querySelectorAll('[data-back-catalog]').forEach(link => {
            const lang = document.documentElement.dataset.language;
            clean.set('lang', lang);
            link.textContent = lang === 'zh' ? '← 返回篩選結果' : '← Back to results';
            link.href = '../apps.html?' + clean.toString() + '#card-' + link.dataset.backCatalog + '-' + lang;
        });
    }
    restoreCatalogLinks();
    document.addEventListener('languagechange', restoreCatalogLinks);
    document.querySelectorAll('[data-support-form]').forEach(form => {
        const lang = form.dataset.supportForm;
        const choice = form.querySelector('select');
        if (params.has('app') && Array.from(choice.options).some(option => option.value === params.get('app'))) choice.value = params.get('app');
        form.addEventListener('submit', event => {
            event.preventDefault();
            const name = choice.options[choice.selectedIndex].text;
            const subject = (lang === 'zh' ? 'App 支援：' : 'App support: ') + name;
            const body = lang === 'zh' ? 'App 與版本：'+name+'\n裝置型號：\n系統版本：\n問題描述：\n重現步驟：\n' : 'App and version: '+name+'\nDevice: \nOS version: \nIssue: \nSteps to reproduce: \n';
            location.href = 'mailto:mibsteven.chang@gmail.com?subject='+encodeURIComponent(subject)+'&body='+encodeURIComponent(body);
        });
    });
})();
