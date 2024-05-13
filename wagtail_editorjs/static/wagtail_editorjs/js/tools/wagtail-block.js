(function(blockName, blockTitle) {
    const wagtailBlockIcon = `<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-link-45deg" viewBox="0 0 16 16">
        <!-- The MIT License (MIT) -->
        <!-- Copyright (c) 2011-2024 The Bootstrap Authors -->
        <path d="M4.715 6.542 3.343 7.914a3 3 0 1 0 4.243 4.243l1.828-1.829A3 3 0 0 0 8.586 5.5L8 6.086a1 1 0 0 0-.154.199 2 2 0 0 1 .861 3.337L6.88 11.45a2 2 0 1 1-2.83-2.83l.793-.792a4 4 0 0 1-.128-1.287z"/>
        <path d="M6.586 4.672A3 3 0 0 0 7.414 9.5l.775-.776a2 2 0 0 1-.896-3.346L9.12 3.55a2 2 0 1 1 2.83 2.83l-.793.792c.112.42.155.855.128 1.287l1.372-1.372a3 3 0 1 0-4.243-4.243z"/>
    </svg>`;

    class WagtailBlockTool extends window.BaseWagtailEditorJSTool {
        constructor({ data, api, config, block }) {

            if (!data) {
                data = {};
            }

            if (!data["block"]) {
                data["block"] = {};
            }

            super({ data, api, config, block });

            this.settings = [

            ];

            this.initSettings();
        }

        static get toolbox() {
            return {
                title: blockTitle, // Title for the block
                icon: wagtailBlockIcon,
            };
        }

        render() {
            this.wrapperElement = window.makeElement('div', {
                className: 'wagtail-block-feature-wrapper',
            });

            this.blockPrefix = `${blockName}-${Math.random().toString(36).substring(7)}`;

            const html = this.config.rendered.replace(
                /__PREFIX__/g,
                this.blockPrefix,
            );

            this.wrapperElement.innerHTML = html;

            const element = this.wrapperElement.querySelector(`#${this.blockPrefix}`);
            const id = element.id;

            if (!window.telepath) {
                console.error('Telepath is not defined');
                return;
            }

            // const dataValue = JSON.parse(element.getAttribute('data-w-block-data-value'));
            // const argumentsValue = JSON.parse(element.getAttribute('data-w-block-arguments-value'));
            const dataValue = JSON.parse(element.dataset.wBlockDataValue);
            const argumentsValue = JSON.parse(element.dataset.wBlockArgumentsValue);
            this.blockDef = telepath.unpack(dataValue);

            this.block = this.blockDef.render(
                element, id, ...argumentsValue,
            )

            if (this.data) {
                this.block.setState(this.data["block"]);
            }

            return super.render();
        }

        validate(savedData) {
            return true;
        }

        save(blockContent) {
            this.data = super.save(blockContent);
            if (!this.block.getState) {
                console.error('Block does not have a getState method', this.block)
            } else {
                this.data["block"] = this.block.getState();
            }
            return this.data || {};
        }
    }

    window[`WagtailBlockTool_${blockName}`] = WagtailBlockTool;

})(
    document.currentScript.getAttribute('data-name'),
    document.currentScript.getAttribute('data-title'),
);