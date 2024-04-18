const wagtailButtonIcon = `<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-link-45deg" viewBox="0 0 16 16">
    <!-- The MIT License (MIT) -->
    <!-- Copyright (c) 2011-2024 The Bootstrap Authors -->
    <path d="M4.715 6.542 3.343 7.914a3 3 0 1 0 4.243 4.243l1.828-1.829A3 3 0 0 0 8.586 5.5L8 6.086a1 1 0 0 0-.154.199 2 2 0 0 1 .861 3.337L6.88 11.45a2 2 0 1 1-2.83-2.83l.793-.792a4 4 0 0 1-.128-1.287z"/>
    <path d="M6.586 4.672A3 3 0 0 0 7.414 9.5l.775-.776a2 2 0 0 1-.896-3.346L9.12 3.55a2 2 0 1 1 2.83 2.83l-.793.792c.112.42.155.855.128 1.287l1.372-1.372a3 3 0 1 0-4.243-4.243z"/>
</svg>`;

const wagtailButtonEditIcon = `<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-pencil-square" viewBox="0 0 16 16">
    <!-- The MIT License (MIT) -->
    <!-- Copyright (c) 2011-2024 The Bootstrap Authors -->
    <path d="M15.502 1.94a.5.5 0 0 1 0 .706L14.459 3.69l-2-2L13.502.646a.5.5 0 0 1 .707 0l1.293 1.293zm-1.75 2.456-2-2L4.939 9.21a.5.5 0 0 0-.121.196l-.805 2.414a.25.25 0 0 0 .316.316l2.414-.805a.5.5 0 0 0 .196-.12l6.813-6.814z"/>
    <path fill-rule="evenodd" d="M1 13.5A1.5 1.5 0 0 0 2.5 15h11a1.5 1.5 0 0 0 1.5-1.5v-6a.5.5 0 0 0-1 0v6a.5.5 0 0 1-.5.5h-11a.5.5 0 0 1-.5-.5v-11a.5.5 0 0 1 .5-.5H9a.5.5 0 0 0 0-1H2.5A1.5 1.5 0 0 0 1 2.5z"/>
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
        this.wrapperElement.dataset.url          = data.url;
        this.wrapperElement.dataset.pageId       = data.id;
        this.wrapperElement.dataset.parentPageId = data.parentId;
        this.buttonLinkElement.href              = data.url;
        this.buttonElement.innerText             = data.title;
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
            className: 'wagtail-button-wrapper button button-secondary',
        });

        this.buttonElement = window.makeElement('div', {
            className: 'wagtail-button',
            contentEditable: true,
        });

        this.buttonLinkElement = window.makeElement('a', {
            "innerHTML": wagtailButtonIcon,
            "className": "wagtail-button-icon",
            "target":    "_blank",
        });

        this.chooseNewPageButton = window.makeElement('button', {
            "innerHTML": wagtailButtonEditIcon,
            "className": "wagtail-button-icon wagtail-button-edit",
        });

        this.wrapperElement.appendChild(this.buttonElement);
        this.wrapperElement.appendChild(this.buttonLinkElement);
        this.wrapperElement.appendChild(this.chooseNewPageButton);

        if (this.data && this.data.url) {
            this.wrapperElement.dataset.url          = this.data.url;
            this.wrapperElement.dataset.pageId       = this.data.pageId;
            this.wrapperElement.dataset.parentPageId = this.data.parentId;
            this.buttonLinkElement.href              = this.data.url;
            this.buttonElement.innerText             = this.data.text;
        } else {
            window.openChooserModal(this.pageChooser, this.setData.bind(this));
        }

        this.chooseNewPageButton.addEventListener('click', () => {
            window.openChooserModal(this.pageChooser, this.setData.bind(this));
        });

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
        // this.data.text     = button.innerText;
        // this.data.url     = button.dataset.url;
        // this.data.pageId   = button.dataset.pageId;
        // this.data.parentId = button.dataset.parentPageId;
        this.data.text = this.buttonElement.innerText;
        this.data.url = this.wrapperElement.dataset.url;
        this.data.pageId = this.wrapperElement.dataset.pageId;
        this.data.parentId = this.wrapperElement.dataset.parentPageId;
        return this.data;
    }
}

window.PageButtonTool = PageButtonTool;