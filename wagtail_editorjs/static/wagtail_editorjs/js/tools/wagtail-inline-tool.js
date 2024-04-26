/**
 * @typedef {Object} TagObject
 * @property {string} name
 * @property {string} class
 * 
 * @typedef {Object} EditorActionObject
 * @property {Function} renderActions
 * @property {Function} showActions
 * @property {Function} hideActions
 */


class BaseWagtailInlineTool {
    /**
     * Provides a simple way to create an EditorJS inline tool.
     * 
     * Must be extended by a class that implements the following:
     * 
     * Attributes:
     * 
     * - iconHTML: string
     * - tag: object
     * 
     * Methods:
     * 
     * - showActions(wrapperTag: HTMLElement): void
     * - hideActions(): void
     * - setDataOnWrapper(wrapperTag: HTMLElement): void
     * - renderTag(range: Range, selectedText: DocumentFragment): HTMLElement
     */
    constructor({ api, config }) {
        if (!config) {
            config = {};
        }

        this.button = null;
        this._state = false;
        this.api = api;
        this.config = config;

        this.tag = {
            name: '',
            class: '',
        };
    }
    
    static get isInline() {
        return true;
    }

    set state(state) {
        this._state = state;
        this.button.classList.toggle(this.api.styles.inlineToolButtonActive, state);
    }

    get state() {
        return this._state;
    }

    /**
     * @returns {string}
     * @readonly
     * @abstract
     * @throws {Error} if not implemented
     * @description
     * Returns the HTML for the icon of the inline tool.
     */
    get iconHTML() {
        throw new Error('iconHTML not implemented');
    }

    /**
     * @returns {TagObject}
     * @throws {Error} if tag name or class is not defined
     * @readonly
     */
    get _tag() {
        if (!this.tag.name) {
            throw new Error('Tag name is not defined');
        }
        if (!this.tag.class) {
            throw new Error('Tag class is not defined');
        }
        return this.tag;
    }

    /**
     * @returns {HTMLElement}
     */
    render() {
        this.button = document.createElement('button');
        this.button.type = 'button';
        this.button.innerHTML = this.iconHTML;
        this.button.classList.add(
            this.api.styles.inlineToolButton,
        )

        return this.button;
    }

    /**
     * @param {Range} range
     */
    surround(range) {
        if (this.state) {
            this.unwrap(range);
            return;
        }
        this.wrap(range);
    }
    
    /**
     * @param {Range} range
     */
    wrap(range) {
        let selectedText = range.extractContents();
        const wrapperTag = this.renderTag(range, selectedText);

        range.insertNode(wrapperTag);

        this.api.selection.expandToTag(wrapperTag);
    }

    /**
     * @param {Range} range
     */
    unwrap(range) {
        const wrapperTag = this.api.selection.findParentTag(this._tag.name, this._tag.class);

        // Extract the text from the wrapper tag
        const text = range.extractContents();

        // Remove the wrapper tag
        wrapperTag.remove();

        // Re-insert the old text
        range.insertNode(text);

        // wrapperTag.replaceWith(...wrapperTag.childNodes);
    }
    
    checkState() {
        const wrapperTag = this.api.selection.findParentTag(
            this._tag.name, this._tag.class,
        );

        this.state = !!wrapperTag;
    }

    /**
     * @param {Range} range
     * @param {DocumentFragment} selectedText
     * @returns {HTMLElement}
     */
    renderTag(range, selectedText) {
        const wrapperTag = document.createElement(this._tag.name);
        this.wrapperTag = wrapperTag;
        wrapperTag.classList.add(this._tag.class);
        wrapperTag.appendChild(selectedText);
        this.setDataOnWrapper(range, wrapperTag);
        return wrapperTag;
    }

    /**
     * @param {Range} range
     * @param {HTMLElement} wrapperTag
     */
    setDataOnWrapper(range, wrapperTag) {
        
    }

}

window.BaseWagtailInlineTool = BaseWagtailInlineTool;
