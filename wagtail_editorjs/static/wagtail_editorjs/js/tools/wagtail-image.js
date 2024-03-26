const wagtailImageIcon = `<svg width="16" height="16" viewBox="0 0 17 15" xmlns="http://www.w3.org/2000/svg">
    <use href="#icon-image"></use>
</svg>`;



class Setting {
    constructor(tuneName, iconName, { onClick = null, description = null }) {
        this.tuneName = tuneName;
        this.icon = iconName;
        this.api = null;
        this.config = null;
        this.tool = null;
        this._onClick = onClick;
        this.description = description;
    }

    setTool(api, config, tool) {
        this.api = api;
        this.config = config;
        this.tool = tool;
    }

    initialize() {
        this.tool.imageWrapper.classList.toggle(this.tuneName, this.isActive());
    }

    render() {
        const button = document.createElement('div');
        button.classList.add('cdx-settings-button');
        button.classList.toggle('cdx-settings-button--active', this.isActive());
        button.innerHTML = this.icon;
        button.addEventListener('click', () => {
            this.onClick();
            button.classList.toggle('cdx-settings-button--active', this.isActive());
        });
        return button;
    }

    isActive() {
        return false;
    }

    onClick() {
        if (this._onClick) {
            this._onClick(this.isActive());
        }
    }

    onSave() {
        this.tool.data[this.tuneName] = this.isActive();
    }
}

class SimpleToggleSetting extends Setting {
    onClick() {
        this.tool.data[this.tuneName] = !this.tool.data[this.tuneName];
        const isActive = this.isActive();
        this.tool.imageWrapper.classList.toggle(this.tuneName, isActive);
        this.tool.refreshActiveTunes();
        if (this._onClick) {
            this._onClick(isActive);
        }
    }

    initialize() {
        if (this.tool.data[this.tuneName] === undefined) {
            this.tool.data[this.tuneName] = false;
        }

        if (this.isActive()) {
            this.tool.imageWrapper.classList.toggle(this.tuneName, true);
            this.tool.refreshActiveTunes();
            if (this._onClick) {
                this._onClick(true);
            }
        }
    }

    isActive() {
        return !!this.tool.data[this.tuneName];
    }
}

class BackgroundColorSetting extends Setting {
    constructor(tuneName, iconName, description) {
        super(tuneName, iconName, { description });
        this.currentColor = null;
    }

    setTool(api, config, tool) {
        super.setTool(api, config, tool);
        this.currentColor = tool.data[this.tuneName];
    }

    initialize() {
        if (this.currentColor) {
            this.tool.imageWrapper.style.backgroundColor = this.currentColor;
        }
    }

    render() {
        const inputWrapper = document.createElement('div');
        inputWrapper.classList.add('wagtail-image-button');

        const input = document.createElement('input');
        input.classList.add(
            'cdx-settings-button',
            'wagtail-image-button__color-picker'
        );
        input.type = 'color';
        input.value = '#000000';
        input.hidden = true;

        input.addEventListener('input', () => {
            this.tool.imageWrapper.style.backgroundColor = input.value;
            this.currentColor = input.value;
        });
        input.addEventListener('blur', () => {
            input.hidden = true;
            clearButton.hidden = false;
        });

        const clearButton = document.createElement('button');
        clearButton.innerHTML = this.icon;
        clearButton.type = 'button';
        clearButton.classList.add('cdx-settings-button');
        clearButton.addEventListener('click', () => {
            this.tool.imageWrapper.style.backgroundColor = '';
            this.currentColor = null;
            input.hidden = false;
            clearButton.hidden = true;
        });

        inputWrapper.appendChild(input);
        inputWrapper.appendChild(clearButton);

        input.hidden = this.isActive();
        clearButton.hidden = !this.isActive();

        return inputWrapper;
    }

    onSave() {
        this.tool.data[this.tuneName] = this.currentColor;
    }

    isActive() {
        return !!this.currentColor;
    }
}

class TitleToggleSetting extends SimpleToggleSetting {
    onClick() {
        super.onClick();
        this.tool.titleInput.hidden = !this.isActive();
    }

    isActive() {
        return !!this.tool.data[this.tuneName];
    }
}


class ChangeImageSetting extends Setting {
    onClick() {
        this.tool.imageChooser.openChooserModal();
        this.tool.imageChooser.input.addEventListener('change', () => {
            const data = this.tool.imageChooser.getState();
            this.tool.image.src = `${this.config.getImageUrl}${data.id}/`
            this.tool.image.alt = data.title;
            this.tool.imageWrapper.style.filter = 'blur(5px)';
            this.tool.image.onload = () => {
                this.tool.imageWrapper.style.filter = 'blur(0px)';
                this.tool.image.onload = null;
            }
            this.tool.image.dataset.imageId = data.id;
            this.tool.image.dataset.editUrl = data.edit_url;
            this.tool.titleInput.value = data.title;
        });
    }
}


class WagtailImageTool {
    constructor({ data, api, config, block }) {
        if (!config) {
            config = {
                imageChooserId: null,
            };
        }

        if (!config.imageChooserId) {
            console.error('pageChooserId is required');
            throw new Error('pageChooserId is required');
        }

        this.data = data;
        this.api = api;
        this.block = block;
        this.config = config;
        this.imageChooser = new window.ImageChooser(config.imageChooserId);
        this.imageWrapper = null;
        /*
        Icons provided by bootstrap icons.
        <!-- The MIT License (MIT) -->
        <!-- Copyright (c) 2011-2024 The Bootstrap Authors -->
        */
        this.settings = [
            new SimpleToggleSetting(
                'withBorder', 
                `<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-border" viewBox="0 0 16 16">
                    <path d="M0 0h.969v.5H1v.469H.969V1H.5V.969H0zm2.844 1h-.938V0h.938zm1.875 0H3.78V0h.938v1zm1.875 0h-.938V0h.938zm.937 0V.969H7.5V.5h.031V0h.938v.5H8.5v.469h-.031V1zm2.813 0h-.938V0h.938zm1.875 0h-.938V0h.938zm1.875 0h-.938V0h.938zM15.5 1h-.469V.969H15V.5h.031V0H16v.969h-.5zM1 1.906v.938H0v-.938zm6.5.938v-.938h1v.938zm7.5 0v-.938h1v.938zM1 3.78v.938H0V3.78zm6.5.938V3.78h1v.938zm7.5 0V3.78h1v.938zM1 5.656v.938H0v-.938zm6.5.938v-.938h1v.938zm7.5 0v-.938h1v.938zM.969 8.5H.5v-.031H0V7.53h.5V7.5h.469v.031H1v.938H.969zm1.875 0h-.938v-1h.938zm1.875 0H3.78v-1h.938v1zm1.875 0h-.938v-1h.938zm1.875-.031V8.5H7.53v-.031H7.5V7.53h.031V7.5h.938v.031H8.5v.938zm1.875.031h-.938v-1h.938zm1.875 0h-.938v-1h.938zm1.875 0h-.938v-1h.938zm1.406 0h-.469v-.031H15V7.53h.031V7.5h.469v.031h.5v.938h-.5zM0 10.344v-.938h1v.938zm7.5 0v-.938h1v.938zm8.5-.938v.938h-1v-.938zM0 12.22v-.938h1v.938zm7.5 0v-.938h1v.938zm8.5-.938v.938h-1v-.938zM0 14.094v-.938h1v.938zm7.5 0v-.938h1v.938zm8.5-.938v.938h-1v-.938zM.969 16H0v-.969h.5V15h.469v.031H1v.469H.969zm1.875 0h-.938v-1h.938zm1.875 0H3.78v-1h.938v1zm1.875 0h-.938v-1h.938zm.937 0v-.5H7.5v-.469h.031V15h.938v.031H8.5v.469h-.031v.5zm2.813 0h-.938v-1h.938zm1.875 0h-.938v-1h.938zm1.875 0h-.938v-1h.938zm.937 0v-.5H15v-.469h.031V15h.469v.031h.5V16z"/>
                </svg>`,
                {
                    description: this.api.i18n.t('Border'),
                }
            ),
            new SimpleToggleSetting(
                'stretched',
                `<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-arrows-fullscreen" viewBox="0 0 16 16">
                    <path fill-rule="evenodd" d="M5.828 10.172a.5.5 0 0 0-.707 0l-4.096 4.096V11.5a.5.5 0 0 0-1 0v3.975a.5.5 0 0 0 .5.5H4.5a.5.5 0 0 0 0-1H1.732l4.096-4.096a.5.5 0 0 0 0-.707m4.344 0a.5.5 0 0 1 .707 0l4.096 4.096V11.5a.5.5 0 1 1 1 0v3.975a.5.5 0 0 1-.5.5H11.5a.5.5 0 0 1 0-1h2.768l-4.096-4.096a.5.5 0 0 1 0-.707m0-4.344a.5.5 0 0 0 .707 0l4.096-4.096V4.5a.5.5 0 1 0 1 0V.525a.5.5 0 0 0-.5-.5H11.5a.5.5 0 0 0 0 1h2.768l-4.096 4.096a.5.5 0 0 0 0 .707m-4.344 0a.5.5 0 0 1-.707 0L1.025 1.732V4.5a.5.5 0 0 1-1 0V.525a.5.5 0 0 1 .5-.5H4.5a.5.5 0 0 1 0 1H1.732l4.096 4.096a.5.5 0 0 1 0 .707"/>
                </svg>`,
                {
                    description: this.api.i18n.t('Stretched'),
                    onClick: (isActive) => {
                        this.block.stretched = isActive;
                    }
                }
            ),
            new BackgroundColorSetting(
                'backgroundColor',
                `<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-paint-bucket" viewBox="0 0 16 16">
                    <path d="M6.192 2.78c-.458-.677-.927-1.248-1.35-1.643a3 3 0 0 0-.71-.515c-.217-.104-.56-.205-.882-.02-.367.213-.427.63-.43.896-.003.304.064.664.173 1.044.196.687.556 1.528 1.035 2.402L.752 8.22c-.277.277-.269.656-.218.918.055.283.187.593.36.903.348.627.92 1.361 1.626 2.068.707.707 1.441 1.278 2.068 1.626.31.173.62.305.903.36.262.05.64.059.918-.218l5.615-5.615c.118.257.092.512.05.939-.03.292-.068.665-.073 1.176v.123h.003a1 1 0 0 0 1.993 0H14v-.057a1 1 0 0 0-.004-.117c-.055-1.25-.7-2.738-1.86-3.494a4 4 0 0 0-.211-.434c-.349-.626-.92-1.36-1.627-2.067S8.857 3.052 8.23 2.704c-.31-.172-.62-.304-.903-.36-.262-.05-.64-.058-.918.219zM4.16 1.867c.381.356.844.922 1.311 1.632l-.704.705c-.382-.727-.66-1.402-.813-1.938a3.3 3.3 0 0 1-.131-.673q.137.09.337.274m.394 3.965c.54.852 1.107 1.567 1.607 2.033a.5.5 0 1 0 .682-.732c-.453-.422-1.017-1.136-1.564-2.027l1.088-1.088q.081.181.183.365c.349.627.92 1.361 1.627 2.068.706.707 1.44 1.278 2.068 1.626q.183.103.365.183l-4.861 4.862-.068-.01c-.137-.027-.342-.104-.608-.252-.524-.292-1.186-.8-1.846-1.46s-1.168-1.32-1.46-1.846c-.147-.265-.225-.47-.251-.607l-.01-.068zm2.87-1.935a2.4 2.4 0 0 1-.241-.561c.135.033.324.11.562.241.524.292 1.186.8 1.846 1.46.45.45.83.901 1.118 1.31a3.5 3.5 0 0 0-1.066.091 11 11 0 0 1-.76-.694c-.66-.66-1.167-1.322-1.458-1.847z"/>
                </svg>`,
                this.api.i18n.t('Background Color'),
            ),
            new TitleToggleSetting(
                'usingCaption',
                `<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-clipboard-x" viewBox="0 0 16 16">
                    <path fill-rule="evenodd" d="M6.146 7.146a.5.5 0 0 1 .708 0L8 8.293l1.146-1.147a.5.5 0 1 1 .708.708L8.707 9l1.147 1.146a.5.5 0 0 1-.708.708L8 9.707l-1.146 1.147a.5.5 0 0 1-.708-.708L7.293 9 6.146 7.854a.5.5 0 0 1 0-.708"/>
                    <path d="M4 1.5H3a2 2 0 0 0-2 2V14a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V3.5a2 2 0 0 0-2-2h-1v1h1a1 1 0 0 1 1 1V14a1 1 0 0 1-1 1H3a1 1 0 0 1-1-1V3.5a1 1 0 0 1 1-1h1z"/>
                    <path d="M9.5 1a.5.5 0 0 1 .5.5v1a.5.5 0 0 1-.5.5h-3a.5.5 0 0 1-.5-.5v-1a.5.5 0 0 1 .5-.5zm-3-1A1.5 1.5 0 0 0 5 1.5v1A1.5 1.5 0 0 0 6.5 4h3A1.5 1.5 0 0 0 11 2.5v-1A1.5 1.5 0 0 0 9.5 0z"/>
                </svg>`,
                {
                    description: this.api.i18n.t('Using Caption'),
                }
            ),
            new ChangeImageSetting(
                'changeImage',
                wagtailImageIcon,
                {
                    description: this.api.i18n.t('Change Image'),
                }
            )
        ];

        this.settings.forEach( tune => {
            tune.setTool(this.api, this.config, this);
        });
    }


    static get toolbox() {
      return {
            title: 'Image',
            icon: wagtailImageIcon,
        };
    }

    validate(savedData) {
        return !!savedData.imageId;
    }
  
    render(){
        this.imageWrapper = document.createElement('div');
        this.imageWrapper.classList.add('wagtail-image-tool');

        this.image = document.createElement('img');
        this.titleInput = document.createElement('input');
        this.titleInput.hidden = !this.data.usingCaption;

        let chooserModalFunc = null;
        chooserModalFunc = () => {
            this.imageChooser.input.removeEventListener('change', chooserModalFunc);
            const data = this.imageChooser.getState();
            this.image.src = `${this.config.getImageUrl}${data.id}/`
            this.image.alt = data.title;
            this.image.dataset.imageId = data.id;
            this.image.dataset.editUrl = data.edit_url;
            this.titleInput.value = data.title;
        }

        if (this.data.imageId) {
            this.image.src = `${this.config.getImageUrl}${this.data.imageId}/`
            this.image.alt = this.data.alt;
            this.titleInput.value = this.data.alt;
            this.image.dataset.imageId = this.data.imageId;
            this.image.dataset.editUrl = this.data.editUrl;
        } else {
            this.imageChooser.openChooserModal()
            this.imageChooser.input.addEventListener('change', chooserModalFunc);
        }

        this.image.style.cursor = 'pointer';
        this.image.title = this.api.i18n.t('CTRL + Click to change image');
        this.image.addEventListener('click', (e) => {
            if (e.ctrlKey) {
                this.imageChooser.openChooserModal()
                this.imageChooser.input.addEventListener('change', chooserModalFunc);
            } else {
                window.open(this.data.editUrl, '_blank');
            }
        });

        this.titleInput.placeholder = this.api.i18n.t('Text when image is not available');
        this.titleInput.classList.add('cdx-input');
        this.titleInput.value = this.image.alt;
        this.titleInput.addEventListener('input', () => {
            this.data.alt = this.titleInput.value;
        });

        this.imageWrapper.appendChild(this.image);
        this.imageWrapper.appendChild(this.titleInput);

        setTimeout(() => {
            this.settings.forEach( tune => {
                if (tune.initialize) {
                    tune.initialize();
                }
            });
        }, 0);

        this.refreshActiveTunes();

        return this.imageWrapper;
    }
  
    save(blockContent){
        const image = blockContent.querySelector('img');
        const titleInput = blockContent.querySelector('input');

        for (let i = 0; i < this.settings.length; i++) {
            const tune = this.settings[i];
            if (tune.onSave) {
                tune.onSave();
            }
        }

        return Object.assign(this.data, {
            imageId: image.dataset.imageId,
            editUrl: image.dataset.editUrl,
            alt: titleInput.value,
        });
    }

    renderSettings(){
        const wrapper = document.createElement('div');

        this.settings.forEach( tune => {
            const setting = tune.render();
            let description = tune.description;
            if (!tune.description) {
                description = tune.tuneName;
            }
            this.api.tooltip.onHover(setting, description, {
                placement: 'top',
                hidingDelay: 200,
            });
            wrapper.appendChild(setting);
        });
    
        return wrapper;
    }

    refreshActiveTunes() {
        this.settings.forEach( tune => {
            this.imageWrapper.classList.toggle(tune.name, tune.isActive());
        });
    }
}


window.WagtailImageTool = WagtailImageTool;
