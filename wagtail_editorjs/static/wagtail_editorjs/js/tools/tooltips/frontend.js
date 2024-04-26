class TippyTooltip {
    /**
     * @param {HTMLElement} element
     **/
    constructor(element) {
        this.element = element;
        this.tooltipConfig = this.makeConfig();
        this.init();
    }

    init() {
        if (!window.tippy) {
            console.debug("Tippy tooltips disabled");
            return;
        }
        tippy(this.element, this.tooltipConfig);
    }

    makeConfig() {
        const cfg = {}
        for (const attr of this.element.attributes) {
            if (attr.name.startsWith("data-tippy-")) {
                const key = attr.name.replace("data-tippy-", "");
                cfg[key] = attr.value;
            }
        }
        this.tooltipConfig = cfg;
        return cfg;
    }
}

document.addEventListener("DOMContentLoaded", () => {
    const tooltips = document.querySelectorAll(".wagtail-tooltip");
    for (const tooltip of tooltips) {
        new TippyTooltip(tooltip);
    }
});