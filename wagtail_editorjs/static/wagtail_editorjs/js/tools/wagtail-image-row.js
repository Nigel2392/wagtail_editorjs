const wagtailImageRowToolIcon = `<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-images" viewBox="0 0 16 16">
    <!-- The MIT License (MIT) -->
    <!-- Copyright (c) 2011-2024 The Bootstrap Authors -->
    <path d="M4.502 9a1.5 1.5 0 1 0 0-3 1.5 1.5 0 0 0 0 3"/>
    <path d="M14.002 13a2 2 0 0 1-2 2h-10a2 2 0 0 1-2-2V5A2 2 0 0 1 2 3a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2v8a2 2 0 0 1-1.998 2M14 2H4a1 1 0 0 0-1 1h9.002a2 2 0 0 1 2 2v7A1 1 0 0 0 15 11V3a1 1 0 0 0-1-1M2.002 4a1 1 0 0 0-1 1v8l2.646-2.354a.5.5 0 0 1 .63-.062l2.66 1.773 3.71-3.71a.5.5 0 0 1 .577-.094l1.777 1.947V5a1 1 0 0 0-1-1z"/>
</svg>`;

const wagtailImageRowToolAddIcon = `<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-node-plus" viewBox="0 0 16 16">
    <!-- The MIT License (MIT) -->
    <!-- Copyright (c) 2011-2024 The Bootstrap Authors -->
    <path fill-rule="evenodd" d="M11 4a4 4 0 1 0 0 8 4 4 0 0 0 0-8M6.025 7.5a5 5 0 1 1 0 1H4A1.5 1.5 0 0 1 2.5 10h-1A1.5 1.5 0 0 1 0 8.5v-1A1.5 1.5 0 0 1 1.5 6h1A1.5 1.5 0 0 1 4 7.5zM11 5a.5.5 0 0 1 .5.5v2h2a.5.5 0 0 1 0 1h-2v2a.5.5 0 0 1-1 0v-2h-2a.5.5 0 0 1 0-1h2v-2A.5.5 0 0 1 11 5M1.5 7a.5.5 0 0 0-.5.5v1a.5.5 0 0 0 .5.5h1a.5.5 0 0 0 .5-.5v-1a.5.5 0 0 0-.5-.5z"/>
</svg>`


class ImageRowTool extends window.BaseWagtailEditorJSTool {
    constructor({ data, api, config, block }) {
        super({ data, api, config, block });

        if (!("images" in this.data || !Array.isArray(this.data.images)) || !this.data.images) {
            this.data.images = [];
        }

        this.settings = [
            new window.BaseButtonSetting({
                icon: wagtailImageRowToolAddIcon,
                name: 'add-image',
                action: () => {
                    
                    this.addImage();
                }
            }),
            new window.BaseToggleSetting({
                name: 'stretched',
                icon: `<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-arrows-fullscreen" viewBox="0 0 16 16">
                    <path fill-rule="evenodd" d="M5.828 10.172a.5.5 0 0 0-.707 0l-4.096 4.096V11.5a.5.5 0 0 0-1 0v3.975a.5.5 0 0 0 .5.5H4.5a.5.5 0 0 0 0-1H1.732l4.096-4.096a.5.5 0 0 0 0-.707m4.344 0a.5.5 0 0 1 .707 0l4.096 4.096V11.5a.5.5 0 1 1 1 0v3.975a.5.5 0 0 1-.5.5H11.5a.5.5 0 0 1 0-1h2.768l-4.096-4.096a.5.5 0 0 1 0-.707m0-4.344a.5.5 0 0 0 .707 0l4.096-4.096V4.5a.5.5 0 1 0 1 0V.525a.5.5 0 0 0-.5-.5H11.5a.5.5 0 0 0 0 1h2.768l-4.096 4.096a.5.5 0 0 0 0 .707m-4.344 0a.5.5 0 0 1-.707 0L1.025 1.732V4.5a.5.5 0 0 1-1 0V.525a.5.5 0 0 1 .5-.5H4.5a.5.5 0 0 1 0 1H1.732l4.096 4.096a.5.5 0 0 1 0 .707"/>
                </svg>`,
                action: function() {
                    this.tool.data.settings.stretched = !this.tool.data.settings.stretched;
                    this.tool.block.stretched = this.tool.data.settings.stretched;
                },
                isActive: function() {
                    return this.tool.data.settings.stretched;
                },
                initialize: function() {
                    if (this.tool.block.stretched !== this.tool.data.settings.stretched) {
                        this.tool.block.stretched = !!this.tool.data.settings.stretched;
                    }
                },
                getState: function() {
                    return this.tool.data.settings.stretched;
                },
            }),
        ];
        this.initSettings();
        this.imageChooser = new window.ImageChooser(config.imageChooserId);
        this.images = this.data.images;
    }

    static get toolbox() {
        return {
            title: 'Image Row',
            icon: wagtailImageRowToolIcon,
        };
    }

    addImage() {
        this.imageChooser.openChooserModal();


        let changeEventFunc;
        changeEventFunc = () => {
            const data = this.imageChooser.getState();
            this._createImage(data);
            this.imageChooser.input.removeEventListener('change', changeEventFunc);
        };

        this.imageChooser.input.addEventListener('change', changeEventFunc);
    }

    _createImage(imageData) {
        const imageWrapper = this.imageRow.addElement('div', {
            className: 'wagtail-image-row-image-wrapper',
        });

        const image = imageWrapper.addElement('img', {
            className: 'wagtail-image-row-image',
        });

        image.src = `${this.config.getImageUrl}${imageData.id}/`;
        image.alt = imageData.title;
        image.dataset.imageId = imageData.id;
        image.dataset.editUrl = imageData.edit_url;
    }

    render() {
        this.wrapperElement = window.makeElement('div', {
            className: 'wagtail-image-row-wrapper',
        });

        this.imageRow = this.wrapperElement.addElement('div', {
            className: 'wagtail-image-row',
        });

        if (this.images && this.images.length > 0) {
            this.images.forEach((imageData) => {
                this._createImage(imageData);
            });
        } else {
            this.settings[0].onEvent();
        }

        new window.Sortable(this.imageRow, {
            handle: '.wagtail-image-row-image-wrapper',
            animation: 150,
            easing: 'cubic-bezier(1, 0, 0, 1)',
            dragClass: 'wagtail-image-row-image-dragging',
        });

        return super.render();
    }

    save(blockContent) {
        this.data = super.save(blockContent);
        this.data.images = [];
        const images = blockContent.querySelectorAll('.wagtail-image-row-image');
        images.forEach((image) => {
            this.data.images.push({
                id: image.dataset.imageId,
                title: image.alt,
            });
        });
        return this.data;
    }
}

window.ImageRowTool = ImageRowTool;