window.RegisteredEditorJSInitializers = window.RegisteredEditorJSInitializers || [];

function registerInitializer(initializer) {
    window.RegisteredEditorJSInitializers.push(initializer);
};

window.registerInitializer = registerInitializer;

function newEvent(eventName, data) {
    return new CustomEvent(`editorjs:${eventName}`, {detail: data});
}

class EditorJSWidget {
    constructor(elementWrapper, hiddenInput, config) {
        this.element = hiddenInput;
        this.id = elementWrapper.id;
        this.config = config;

        hiddenInput.CurrentWidget = this;
        elementWrapper.CurrentWidget = this;

        this.initEditor();
    }

    initEditor() {
        this.editorConfig = {
            ...this.config,
            onReady: async () => {
                const editorData = await this.editor.save();
                this.element.value = JSON.stringify(editorData);

                this.dispatchEvent('ready', {
                    data: editorData,
                });

                for (let i = 0; i < window.RegisteredEditorJSInitializers.length; i++) {

                    console.log(this.editor, window.RegisteredEditorJSInitializers[i]);

                    const initializer = window.RegisteredEditorJSInitializers[i];
                    try {
                        initializer(this);
                    } catch (e) {
                        console.error(`Failed to initialize EditorJS widget (${i}): ${e}`);
                    }
                }
            },
            onChange: async () => {
                const editorData = await this.editor.save();
                this.element.value = JSON.stringify(editorData);

                this.dispatchEvent('change', {
                    data: editorData,
                });
            },
        };

        if (this.element.value) {
            this.editorConfig.data = JSON.parse(this.element.value);
        }

        if (!window.editors){
            window.editors = [];
        }
        window.editors.push(this);

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
                e.currentTarget.click();
            }).catch((reason) => {
                alert(`Failed to save EditorJS data: ${reason}`);
            });
        });

        this.editor = new EditorJS(this.editorConfig);
        this.element.setAttribute('data-editorjs-initialized', 'true');
        this.element.CurrentEditor = this.editor;

        this.editor.isReady.then(() => {}).catch((reason) => {

            this.dispatchEvent('error', {reason: reason});
            console.error(`Editor.js failed to initialize: ${reason}`);
            console.log(this.editorConfig)
        
        });
    }

    dispatchEvent(eventName, data = null) {
        if (!data) {
            data = {};
        };

        data.editor = this.editor;
        data.widget = this;

        const event = new CustomEvent(
            `editorjs:${eventName}`,
            {detail: data},
        );

        this.element.dispatchEvent(event);
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

window.EditorJSWidget = EditorJSWidget;