

class EditorJSWidget {
    constructor(elementWrapper, hiddenInput, config) {
        this.element = hiddenInput;
        this.id = elementWrapper.id;
        this.config = config;
        this.initEditor();
    }

    initEditor() {
        this.editorConfig = {
            ...this.config,
            onReady: async () => {
                this.element.value = JSON.stringify(await this.editor.save());
            },
            onChange: async () => {
                this.element.value = JSON.stringify(await this.editor.save());
            },
        };

        if (this.element.value) {
            this.editorConfig.data = JSON.parse(this.element.value);
        }

        const formButtons = $('[data-edit-form] :submit');
        let clickedFormSaveButton = false;
        formButtons.on('click', (e) => {
            if (clickedFormSaveButton) {
                return;
            }

            e.preventDefault();
            e.stopPropagation();

            this.editor.save().then((outputData) => {
                this.element.value = JSON.stringify(outputData);
                clickedFormSaveButton = true;
                e.target.click();
            });
        });

        this.editor = new EditorJS(this.editorConfig);

        this.editor.isReady.then(() => {
            // Initialized
        }).catch((reason) => {
            console.error(`Editor.js failed to initialize: ${reason}`);
            console.log(this.editorConfig)
        });
    }

    async getState() {
        return await this.editor.save();
    }

    setState(data) {
        this.editor.render(data);
    }
    
    getValue() {
        return this.element.value;
    }

    focus() {
        this.editor.focus();
    }

    blur() {
        this.editor.blur();
    }

    disconnect() {
        this.editor.destroy();
    }
}
