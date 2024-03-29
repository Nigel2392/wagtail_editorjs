class EditorJSBlock extends window.wagtailStreamField.blocks.FieldBlock {
    getTextLabel(opts) {
        const rawValue = this.widget.getState();
        const value = JSON.parse(rawValue);
        const blocks = value.blocks;
        const text = [];
        const maxLength = opts.maxLength || 100;
        let currentLength = 0;

        for (let i = 0; i < blocks.length; i++) {
            const block = blocks[i];
            const data = block.data;
            if ("text" in data && data.text) {
                currentLength += data.text.length;
                text.push(data.text);
            }
            if (currentLength >= maxLength) {
                break;
            }
        }

        let fakeElement = document.createElement('div');
        fakeElement.innerHTML = text.join(' ');
        return fakeElement.textContent;
    }
}


class EditorJSBlockDefinition extends window.wagtailStreamField.blocks.FieldBlockDefinition {
    render(placeholder, prefix, initialState, initialError, parentCapabilities) {
        return new EditorJSBlock(
            this,
            placeholder,
            prefix,
            initialState,
            initialError,
            parentCapabilities,
        );
    }
}


window.telepath.register("wagtail_editorjs.blocks.EditorJSBlock", EditorJSBlockDefinition);
