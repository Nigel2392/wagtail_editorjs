class EditorJSWidgetController extends window.StimulusModule.Controller {
    static values = { 
        
    };

    connect() {

        const wrapper = document.querySelector(`#${this.element.id}-wagtail-editorjs-widget-wrapper`);
        const configElem = wrapper.querySelector(`#wagtail-editorjs-config`);
        const config = JSON.parse(configElem.textContent);
        const keys = Object.keys(config.tools);
        for (let i = 0; i < keys.length; i++) {
            const key = keys[i];
            const toolConfig = config.tools[key];
            const toolClass = window[toolConfig.class];
            toolConfig.class = toolClass;
            config.tools[key] = toolConfig;
        }

        this.widget = new EditorJSWidget(
            wrapper,
            this.element,
            config,
        );

        wrapper.widget = this.widget;
        wrapper.widgetConfig = config;
        wrapper.widgetElement = this.element;
    }

    disconnect() {
        this.widget.disconnect();
        this.widget = null;
    }
}

window.wagtail.app.register('editorjs-widget', EditorJSWidgetController);
