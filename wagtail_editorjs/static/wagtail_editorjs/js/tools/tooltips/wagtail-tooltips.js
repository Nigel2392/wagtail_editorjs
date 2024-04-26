const WagtailTooltipIconHtml = `<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-info-circle" viewBox="0 0 16 16">
    <!-- The MIT License (MIT) -->
    <!-- Copyright (c) 2011-2024 The Bootstrap Authors -->
    <path d="M8 15A7 7 0 1 1 8 1a7 7 0 0 1 0 14m0 1A8 8 0 1 0 8 0a8 8 0 0 0 0 16"/>
    <path d="m8.93 6.588-2.29.287-.082.38.45.083c.294.07.352.176.288.469l-.738 3.468c-.194.897.105 1.319.808 1.319.545 0 1.178-.252 1.465-.598l.088-.416c-.2.176-.492.246-.686.246-.275 0-.375-.193-.304-.533zM9 4.5a1 1 0 1 1-2 0 1 1 0 0 1 2 0"/>
</svg>`


class WagtailTooltip extends window.BaseWagtailInlineTool {
    constructor({ api, config }) {

        super({ api, config });

        this.tag = {
            name: 'SPAN',
            class: 'wagtail-tooltip',
        };
    }

    static get sanitize() {
        return {
            "span": {
                "class": "wagtail-tooltip",
                "data-controller": "w-tooltip",
                "data-w-tooltip-content-value": true,
                "data-w-tooltip-placement-value": true,
            },
        };
    }

    get iconHTML() {
        return WagtailTooltipIconHtml;
    }

    checkState() {
        const wrapperTag = this.api.selection.findParentTag(
            this._tag.name, this._tag.class,
        );

        this.state = !!wrapperTag;

        if (this.state) {
            this.showActions(wrapperTag);
        } else {
            this.hideActions();
        }
    }

    renderActions() {
        this.tooltipInputWrapper = document.createElement('div');
        this.tooltipInputWrapper.classList.add(
            "wagtail-button-wrapper", 
        );
        this.tooltipInputWrapper.hidden = true;

        this.tooltipInput = document.createElement('input');
        this.tooltipInput.type = 'text';
        this.tooltipInput.placeholder = this.api.i18n.t(
            'Enter tooltip text',
        );
        this.tooltipInput.classList.add(
            this.api.styles.input,
        );

        this.tooltipInputPosition = document.createElement('select');
        this.tooltipInputPosition.classList.add(
        );

        const choices = [
            ['top', this.api.i18n.t('Top')],
            ['right', this.api.i18n.t('Right')],
            ['bottom', this.api.i18n.t('Bottom')],
            ['left', this.api.i18n.t('Left')],
        ];

        choices.forEach(([value, label]) => {
            const option = document.createElement('option');
            option.value = value;
            option.innerText = label;
            this.tooltipInputPosition.appendChild(option);
        });

        this.tooltipInputWrapper.appendChild(
            this.tooltipInput,
        );

        this.tooltipInputWrapper.appendChild(
            this.tooltipInputPosition,
        );

        return this.tooltipInputWrapper;
    }

    showActions(wrapperTag) {
        this.tooltipInputWrapper.hidden = false;

        // Tooltip input element
        this.tooltipInput.oninput = (e) => {
            if (!wrapperTag.dataset.controller && e.target.value) {
                wrapperTag.dataset.controller = "w-tooltip";
            } else if (wrapperTag.dataset.controller && !e.target.value) {
                delete wrapperTag.dataset.controller;
            }
            wrapperTag.dataset.wTooltipContentValue = e.target.value;
        };

        // Position select element
        this.tooltipInputPosition.onchange = (e) => {
            wrapperTag.dataset.wTooltipPlacementValue = e.target.value;
        };
        
        // Set initial content value
        if (wrapperTag.dataset.wTooltipContentValue) {
            this.tooltipInput.value = wrapperTag.dataset.wTooltipContentValue;
        } else {
            this.tooltipInput.value = wrapperTag.innerText;
            this.tooltipInput.dispatchEvent(
                new Event('input'),
            );
        }

        // Set initial position
        this.tooltipInputPosition.value = (
            wrapperTag.dataset.wTooltipPlacementValue || 'bottom'
        )
    }

    hideActions() {
        this.tooltipInputWrapper.hidden = true;
        this.tooltipInputPosition.onchange = null;
        this.tooltipInput.oninput = null;
        this.tooltipInput.value = '';
    }
}

window.WagtailTooltip = WagtailTooltip;