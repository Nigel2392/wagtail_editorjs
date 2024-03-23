const wagtailLinkIcon = `<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-link-45deg" viewBox="0 0 16 16">
    <!-- The MIT License (MIT) -->
    <!-- Copyright (c) 2011-2024 The Bootstrap Authors -->
    <path d="M4.715 6.542 3.343 7.914a3 3 0 1 0 4.243 4.243l1.828-1.829A3 3 0 0 0 8.586 5.5L8 6.086a1 1 0 0 0-.154.199 2 2 0 0 1 .861 3.337L6.88 11.45a2 2 0 1 1-2.83-2.83l.793-.792a4 4 0 0 1-.128-1.287z"/>
    <path d="M6.586 4.672A3 3 0 0 0 7.414 9.5l.775-.776a2 2 0 0 1-.896-3.346L9.12 3.55a2 2 0 1 1 2.83 2.83l-.793.792c.112.42.155.855.128 1.287l1.372-1.372a3 3 0 1 0-4.243-4.243z"/>
</svg>`;

function setDataOnWrapper(wrapperTag, data) {
    if (!data) {
        return;
    }
    wrapperTag.href                   = data.url;
    delete data.url;

    for (const key in data) {
        if (data[key]) {
            wrapperTag.dataset[key] = data[key];
        } else {
            delete wrapperTag.dataset[key];
        }
    }

   //if (!wrapperTag.textContent && data.title) {
   //    wrapperTag.textContent = data.title;
   //}
}


class WagtailLinkTool {
    constructor({ api, config }) {
        if (!config) {
            config = {
                pageChooserId: null,
            };
        }

        if (!config.pageChooserId) {
            console.error('pageChooserId is required');
            throw new Error('pageChooserId is required');
        }

        this.button = null;
        this._state = false;
        this.api = api;
        this.tag = 'A';
        this.tagClass = 'wagtail-link';
        this.config = config;
        this.chooser = null;
        this.urlParams = {
            page_type:           config.page_type || 'wagtailcore.page',
            allow_external_link: config.allow_external_link || true,
            allow_email_link:    config.allow_email_link || true,
            allow_phone_link:    config.allow_phone_link || true,
            allow_anchor_link:   config.allow_anchor_link || true,
        };
        this.colorPicker = null;
    }
    
    static get isInline() {
        return true;
    }

    get state() {
        return this._state;
    }

    static get sanitize() {
        return {
            a: {
                "href": true,
                "class": true,
                "data-id": true,
                "data-title": true,
                "data-admin-title": true,
                "data-edit-url": true,
                "data-parent-id": true,
            },
        };
    }
    
    set state(state) {
        this._state = state;
        this.button.classList.toggle(this.api.styles.inlineToolButtonActive, state);
    }

    render() {
        this.button = document.createElement('button');
        this.button.type = 'button';
        this.button.innerHTML = wagtailLinkIcon;
        this.button.dataset.chooserActionChoose = 'true';
        this.button.classList.add(
            this.api.styles.inlineToolButton,
        )

        // const selectedText = range.extractContents();
        const chooserUrls = {
            /** @deprecated RemovedInWagtail70 - Remove global.chooserUrls usage  */
            ...window.chooserUrls,
        };
        let url = chooserUrls.pageChooser;
      
        const cfg = {
            url: url,
            urlParams: this.urlParams,
            onload: window.PAGE_CHOOSER_MODAL_ONLOAD_HANDLERS,
            modelNames: ['wagtailcore.page'],
        };

        this.chooser = new window.PageChooser(this.config.pageChooserId, cfg);

        return this.button;
    }

    surround(range) {
        if (this.state) {
            this.unwrap(range);
            return;
        }

        // this.button.addEventListener('click', () => {
        // });
        let chooserEventListener = null;
        chooserEventListener = (e) => {
            const data = this.chooser.state;
            this.wrap(range, data);
            this.chooser.input.removeEventListener('change', chooserEventListener);
        };
        this.chooser.openChooserModal();
        this.chooser.input.addEventListener('change', chooserEventListener);
    }
    
    wrap(range, state) {
        const selectedText = range.extractContents();
        const wrapperTag = document.createElement(this.tag);

        setDataOnWrapper(wrapperTag, state);

        wrapperTag.classList.add(this.tagClass);
        wrapperTag.appendChild(selectedText);
        range.insertNode(wrapperTag);

        this.api.selection.expandToTag(wrapperTag);
    }
    
    unwrap(range) {
        const wrapperTag = this.api.selection.findParentTag(this.tag, this.tagClass);
        const text = range.extractContents();
        wrapperTag.remove();
        range.insertNode(text);
    }
    
    
    checkState() {
        const wrapperTag = this.api.selection.findParentTag(this.tag, this.tagClass);
        if (!wrapperTag) {
            return
        }
        

        this.state = !!wrapperTag;

        if (this.state) {
            this.showActions(wrapperTag);
        } else {
            this.hideActions();
        }

    }

    showActions(wrapperTag) {
        this.pageURLInput.value = wrapperTag.href;

        let chooseNewPageFunc = null;
        chooseNewPageFunc = (e) => {
            const data = this.chooser.state;
            setDataOnWrapper(wrapperTag, data);
            this.pageURLInput.value = data.url;
            this.chooser.input.removeEventListener('change', chooseNewPageFunc);
        };

        this.chooseNewPageButton.onclick = (() => {
            this.chooser.openChooserModal();
            this.chooser.input.addEventListener('change', chooseNewPageFunc);
        });

        this.pageURLInput.onchange = (() => {
            setDataOnWrapper(wrapperTag, {
                url:        this.pageURLInput.value,
                id:         null,
                title:      null,
                adminTitle: null,
                editUrl:    null,
                parentId:   null,
            });
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