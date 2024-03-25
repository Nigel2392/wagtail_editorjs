class BaseWagtailChooserTool {
    constructor({ api, config }) {
        if (!config) {
            config = {
                chooserId: null,
            };
        }

        if (!config.chooserId) {
            console.error('chooserId is required');
            throw new Error('chooserId is required');
        }

        this.button = null;
        this._state = false;
        this.api = api;
        this.tag = 'A';
        this.tagClass = `wagtail-${this.constructor["chooserType"]}-link`;
        this.config = config;
        this.chooser = null;
    }
    
    static get isInline() {
        return true;
    }

    get state() {
        return this._state;
    }

    static get sanitize() {
        return {
            a: true,
        };
    }
    
    set state(state) {
        this._state = state;
        this.button.classList.toggle(this.api.styles.inlineToolButtonActive, state);
    }

    setDataOnWrapper(wrapperTag, data) {
        if (!data) {
            return;
        }
        wrapperTag.href                                     = data.url;
        wrapperTag.dataset[this.constructor["chooserType"]] = true;
    
        for (const key in data) {
            if (data[key]) {
                wrapperTag.dataset[key] = data[key];
            } else {
                delete wrapperTag.dataset[key];
            }
        }
    }

    render() {
        this.button = document.createElement('button');
        this.button.type = 'button';
        this.button.innerHTML = this.iconHTML;
        this.button.dataset.chooserActionChoose = 'true';
        this.button.classList.add(
            this.api.styles.inlineToolButton,
        )

        this.chooser = this.newChooser();

        return this.button;
    }

    surround(range) {
        if (this.state) {
            this.unwrap(range);
            return;
        }

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

        let selectedText = range.extractContents();

        const previousWrapperTag = this.api.selection.findParentTag(this.tag);
        if (previousWrapperTag) {
            previousWrapperTag.remove();
        }

        const wrapperTag = document.createElement(this.tag);

        this.setDataOnWrapper(wrapperTag, state);

        wrapperTag.classList.add(this.tagClass);
        wrapperTag.appendChild(selectedText);
        range.insertNode(wrapperTag);

        this.api.selection.expandToTag(wrapperTag);
    }
    
    unwrap(range) {
        const wrapperTag = this.api.selection.findParentTag(this.tag);
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
}

window.BaseWagtailChooserTool = BaseWagtailChooserTool;