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
                const key = attr
                    .name.replace("data-tippy-", "")
                    .replace(/-([a-z])/g, function (g) {
                        return g[1].toUpperCase();
                    }
                );;
                let value = attr.value;
                let valueLower = value.toLowerCase();
                if (valueLower === "true" || valueLower === "false") {
                    value = valueLower === "true";
                } else if (!isNaN(value)) {
                    value = parseFloat(value);
                } else if (value === "null" || valueLower === "none") {
                    value = null;
                }
                cfg[key] = value;
            }
        }
        this.tooltipConfig = cfg;
        return cfg;
    }
}

(function() {
    const documentReadyFn = () => {
        const initTippyNode = (node) => {
            if (node.classList && node.classList.contains("wagtail-tooltip") && !node._tippy) {
                node._tippy = new TippyTooltip(node);
            }
        };
    
        const observerFunc = (mutationsList, observer) => {
            for (const mutation of mutationsList) {
                if (mutation.type === "childList") {
                    for (const node of mutation.addedNodes) {
                        initTippyNode(node);
                    }
                }
            }
        };
     
        const observer = new MutationObserver(observerFunc);
        observer.observe(document.body, { childList: true, subtree: true });
    
        const tooltipNodes = document.querySelectorAll(".wagtail-tooltip");
        tooltipNodes.forEach(initTippyNode);
    }

    if (document.readyState === "complete") {
        documentReadyFn();
    } else {
        document.addEventListener("DOMContentLoaded", documentReadyFn);
    }
})();