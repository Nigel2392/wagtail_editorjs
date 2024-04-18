const wagtailLinkIcon = `<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-link-45deg" viewBox="0 0 16 16">
    <!-- The MIT License (MIT) -->
    <!-- Copyright (c) 2011-2024 The Bootstrap Authors -->
    <path d="M4.715 6.542 3.343 7.914a3 3 0 1 0 4.243 4.243l1.828-1.829A3 3 0 0 0 8.586 5.5L8 6.086a1 1 0 0 0-.154.199 2 2 0 0 1 .861 3.337L6.88 11.45a2 2 0 1 1-2.83-2.83l.793-.792a4 4 0 0 1-.128-1.287z"/>
    <path d="M6.586 4.672A3 3 0 0 0 7.414 9.5l.775-.776a2 2 0 0 1-.896-3.346L9.12 3.55a2 2 0 1 1 2.83 2.83l-.793.792c.112.42.155.855.128 1.287l1.372-1.372a3 3 0 1 0-4.243-4.243z"/>
</svg>`;



class WagtailLinkTool extends window.BaseWagtailChooserTool {
    constructor({ api, config }) {
        super({ api, config })
        this.colorPicker = null;
    }

    get iconHTML() {
        return wagtailLinkIcon;
    }

    static get chooserType() {
        return 'page';
    }

    newChooser() {
        let urlParams = {
            page_type:           this.config.page_type || 'wagtailcore.page',
            allow_external_link: this.config.allow_external_link || true,
            allow_email_link:    this.config.allow_email_link || true,
            allow_phone_link:    this.config.allow_phone_link || true,
            allow_anchor_link:   this.config.allow_anchor_link || true,
        };

        const cfg = {
            url: this.config.chooserUrls.pageChooser,
            urlParams: urlParams,
            onload: window.PAGE_CHOOSER_MODAL_ONLOAD_HANDLERS,
            modelNames: ['wagtailcore.page'],
        };

        return new window.PageChooser(this.config.chooserId, cfg);
    }

    showActions(wrapperTag) {
        this.pageURLInput.value = wrapperTag.href;

        let chooseNewPageFunc = null;
        chooseNewPageFunc = (e) => {
            const data = this.chooser.state;
            this.setDataOnWrapper(wrapperTag, data);
            this.pageURLInput.value = data.url;
            this.chooser.input.removeEventListener('change', chooseNewPageFunc);
        };

        this.chooseNewPageButton.onclick = (() => {
            this.chooser.openChooserModal();
            this.chooser.input.addEventListener('change', chooseNewPageFunc);
        });

        this.api.tooltip.onHover(this.chooseNewPageButton, this.api.i18n.t('Choose new ' + this.constructor["chooserType"]), {
            placement: 'top',
            hidingDelay: 200,
        });

        this.targetSelect.onchange = (e) => {
            this.pageURLInput.target = e.target.value;
        };

        this.relSelect.onchange = (e) => {
            if (!e.target.value && this.pageURLInput.rel) {
                this.pageURLInput.removeAttribute('rel');
            } else {
                this.pageURLInput.rel = e.target.value;
            }
        }

        this.container.hidden = false;


    }
    
    hideActions() {
        this.container.hidden = true;
        this.pageURLInput.value = '';
        this.chooseNewPageButton.onclick = null;
        this.pageURLInput.onchange = null;
        this.targetSelect.onchange = null;
        this.relSelect.onchange = null;
        this.chooseNewPageButton.classList.remove(
            this.api.styles.inlineToolButtonActive
        );
    }
    
    renderActions() {
        this.container = document.createElement('div');
        this.container.classList.add("wagtail-link-tool-actions", "column");
        this.container.hidden = true;

        const btnContainer = document.createElement('div');
        btnContainer.classList.add("wagtail-link-tool-actions");

        this.chooseNewPageButton = document.createElement('button');
        this.chooseNewPageButton.type = 'button';
        this.chooseNewPageButton.innerHTML = wagtailLinkIcon;
        this.chooseNewPageButton.dataset.chooserActionChoose = 'true';
        this.chooseNewPageButton.classList.add(
            this.api.styles.inlineToolButton,
        )

        const selectContainer = document.createElement('div');
        selectContainer.classList.add("wagtail-link-tool-actions");

        this.targetSelect = document.createElement('select');
        this.targetSelect.innerHTML = `
            <option value="">-- ${this.api.i18n.t('Target')} --</option>
            <option value="_self">${this.api.i18n.t('Open in this window')}</option>
            <option value="_blank">${this.api.i18n.t('Open in new window')}</option>
        `;

        this.relSelect = document.createElement('select');
        this.relSelect.innerHTML = `
            <option value="">-- ${this.api.i18n.t('Rel')} --</option>
            <option value="nofollow">${this.api.i18n.t('No follow')}</option>
            <option value="noopener">${this.api.i18n.t('No opener')}</option>
            <option value="noreferrer">${this.api.i18n.t('No referrer')}</option>
        `;

        this.pageURLInput = document.createElement('input');
        this.pageURLInput.type = 'text';
        this.pageURLInput.disabled = true;
        this.pageURLInput.placeholder = this.api.i18n.t('URL');
        this.pageURLInput.classList.add(
            this.api.styles.input,
            this.api.styles.inputUrl,
        );


        selectContainer.appendChild(this.targetSelect);
        selectContainer.appendChild(this.relSelect);

        btnContainer.appendChild(this.pageURLInput);
        btnContainer.appendChild(this.chooseNewPageButton);

        this.container.appendChild(btnContainer);
        this.container.appendChild(selectContainer);

        return this.container;
    }
}

window.WagtailLinkTool = WagtailLinkTool;