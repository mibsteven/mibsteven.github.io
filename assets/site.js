(function () {
    const dictionary = {
        zh: {
            brandRole: "為學習、創作與空間體驗打造的 Apple App",
            navApps: "作品",
            navSupport: "支援",
            navPrivacy: "隱私權",
            navTerms: "條款",
            footerText: "Apps by Yu-Hsiang Chang 為 iPhone、iPad、Mac 與 Apple Vision Pro 打造學習、創作、個人工具與空間體驗 App。",
            privacyPolicy: "隱私權政策",
            termsUse: "使用條款",
            support: "支援"
        },
        en: {
            brandRole: "Thoughtful Apple apps for learning, creativity, and spatial experiences",
            navApps: "Apps",
            navSupport: "Support",
            navPrivacy: "Privacy",
            navTerms: "Terms",
            footerText: "Apps by Yu-Hsiang Chang creates Apple apps for learning, creativity, personal tools, and spatial experiences across iPhone, iPad, Mac, and Apple Vision Pro.",
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
