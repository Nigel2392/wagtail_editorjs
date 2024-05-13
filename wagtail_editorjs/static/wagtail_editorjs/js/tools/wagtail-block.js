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

            this.blockPrefix = this.data.__prefix__ || `${blockName}-${Math.random().toString(36).substring(7)}`;

            const html = this.config.rendered.replace(
                /__ID__/g,
                this.blockPrefix,
            );

            this.wrapperElement.innerHTML = html;

            this.block = this.wrapperElement.firstChild;
            this.inputs = [];

            setTimeout(() => {

                const inputs = this.wrapperElement.querySelectorAll('input, textarea, select');
                for (let i = 0; i < inputs.length; i++) {
                    const inp = inputs[i];
                    if (inp.name.startsWith(this.blockPrefix)) {
                        this.inputs.push(inp);
                    }
                }

                if (this.data) {
                    console.log(this.data);
                    for (let i = 0; i < this.inputs.length; i++) {
                        this.inputs[i].value = this.data["block"][this.inputs[i].name] || '';
                    }
                }

            }, 0);

            return super.render();
        }

        validate(savedData) {
            return true;
        }

        save(blockContent) {
            this.data = super.save(blockContent);

            if (!this.data["block"]) {
                this.data["block"] = {};
            }

            for (let i = 0; i < this.inputs.length; i++) {
                let inp = this.inputs[i];
                this.data["block"][inp.name] = inp.value || '';
            }

            this.data["__prefix__"] = this.blockPrefix;

            return this.data || {};
        }
    }

    window[`WagtailBlockTool_${blockName}`] = WagtailBlockTool;

})(
    document.currentScript.getAttribute('data-name'),
    document.currentScript.getAttribute('data-title'),
);