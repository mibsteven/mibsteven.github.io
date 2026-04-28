(function () {
    const dictionary = {
        zh: {
            brandRole: "獨立 App 開發者",
            navApps: "作品",
            navSupport: "支援",
            navPrivacy: "隱私權",
            navTerms: "條款",
            footerText: "本站採用首頁加各 App 詳細頁的結構，未來新增作品時能保持清楚、穩定且容易維護。",
            privacyPolicy: "隱私權政策",
            termsUse: "使用條款",
            support: "支援"
        },
        en: {
            brandRole: "Independent App Developer",
            navApps: "Apps",
            navSupport: "Support",
            navPrivacy: "Privacy",
            navTerms: "Terms",
            footerText: "This site uses a homepage-plus-app-pages structure so future apps can be added cleanly and maintained with minimal edits.",
            privacyPolicy: "Privacy Policy",
            termsUse: "Terms of Use",
            support: "Support"
        }
    };

    const buttons = document.querySelectorAll("[data-lang]");
    const labels = document.querySelectorAll("[data-i18n]");
    const panels = document.querySelectorAll("[data-lang-panel]");

    function setLanguage(lang) {
        const active = dictionary[lang] ? lang : "zh";
        document.documentElement.lang = active === "zh" ? "zh-Hant" : "en";
        labels.forEach((element) => {
            const key = element.dataset.i18n;
            if (dictionary[active][key]) {
                element.textContent = dictionary[active][key];
            }
        });
        panels.forEach((panel) => {
            panel.classList.toggle("is-active", panel.dataset.langPanel === active);
        });
        buttons.forEach((button) => {
            button.setAttribute("aria-pressed", String(button.dataset.lang === active));
        });
        document.querySelectorAll("[data-title-zh]").forEach((element) => {
            document.title = active === "zh" ? element.dataset.titleZh : element.dataset.titleEn;
        });
        localStorage.setItem("preferredLanguage", active);
    }

    buttons.forEach((button) => {
        button.addEventListener("click", () => setLanguage(button.dataset.lang));
    });

    const savedLanguage = localStorage.getItem("preferredLanguage");
    const browserLanguage = navigator.language && navigator.language.toLowerCase().startsWith("zh") ? "zh" : "en";
    setLanguage(savedLanguage || browserLanguage);
})();