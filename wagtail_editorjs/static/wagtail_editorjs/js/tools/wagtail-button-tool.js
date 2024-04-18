const wagtailButtonIcon = `<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-link-45deg" viewBox="0 0 16 16">
    <!-- The MIT License (MIT) -->
    <!-- Copyright (c) 2011-2024 The Bootstrap Authors -->
    <path d="M4.715 6.542 3.343 7.914a3 3 0 1 0 4.243 4.243l1.828-1.829A3 3 0 0 0 8.586 5.5L8 6.086a1 1 0 0 0-.154.199 2 2 0 0 1 .861 3.337L6.88 11.45a2 2 0 1 1-2.83-2.83l.793-.792a4 4 0 0 1-.128-1.287z"/>
    <path d="M6.586 4.672A3 3 0 0 0 7.414 9.5l.775-.776a2 2 0 0 1-.896-3.346L9.12 3.55a2 2 0 1 1 2.83 2.83l-.793.792c.112.42.155.855.128 1.287l1.372-1.372a3 3 0 1 0-4.243-4.243z"/>
</svg>`;




class PageButtonTool extends window.BaseWagtailEditorJSTool {
    constructor({ data, api, config, block }) {
        super({ data, api, config, block });

        this.settings = [
            new window.BaseButtonSetting({
                icon: wagtailButtonIcon,
                name: 'change-url',
                description: this.api.i18n.t('Change URL'),
                action: () => {
                    window.openChooserModal(
                        this.pageChooser, this.setData.bind(this),
                    )
                },
            }),
        ];
        this.initSettings();
        this.pageChooser = this.newChooser();
    }

    setData(data) {
        this.buttonElement.innerText            = data.title;
        this.buttonElement.dataset.url          = data.url;
        this.buttonElement.dataset.pageId       = data.id;
        this.buttonElement.dataset.parentPageId = data.parentId;
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
            url: window.chooserUrls.pageChooser,
            urlParams: urlParams,
            onload: window.PAGE_CHOOSER_MODAL_ONLOAD_HANDLERS,
            modelNames: ['wagtailcore.page'],
        };

        return new window.PageChooser(this.config.chooserId, cfg);
    }

    static get toolbox() {
        return {
            title: 'Page Button',
            icon: wagtailButtonIcon,
        };
    }

    render() {
        this.wrapperElement = window.makeElement('div', {
            className: 'wagtail-button-wrapper',
        });


        this.buttonElement = window.makeElement('button', {
            className: 'wagtail-button button button-secondary',
        });

        this.wrapperElement.appendChild(this.buttonElement);

       this.buttonElement.addEventListener('click', (event) => {
            event.preventDefault();
            if (event.ctrlKey) {
                window.openChooserModal(this.pageChooser, this.setData.bind(this));
            } else {
                window.open(
                    this.buttonElement.dataset.url,
                    '_blank',
                );
            }
        });

        if (this.data && this.data.url) {
            this.buttonElement.innerText            = this.data.text;
            this.buttonElement.dataset.url          = this.data.url;
            this.buttonElement.dataset.pageId       = this.data.pageId;
            this.buttonElement.dataset.parentPageId = this.data.parentId;
        } else {
            window.openChooserModal(this.pageChooser, this.setData.bind(this));
        }

        return super.render();
    }

    validate(savedData) {
        if (!("pageId" in savedData) || !("text" in savedData)) {
            return false;
        }

        return true;
    }

    save(blockContent) {
        this.data = super.save(blockContent);
        const button = blockContent.querySelector('.wagtail-button');
        this.data.text     = button.innerText;
        this.data.url     = button.dataset.url;
        this.data.pageId   = button.dataset.pageId;
        this.data.parentId = button.dataset.parentPageId;
        return this.data;
    }
}

window.PageButtonTool = PageButtonTool;