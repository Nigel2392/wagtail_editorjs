
class BaseToolSetting {
    constructor({name, icon, description = null, action = null, initialize = null, isActive = null, getState = null, render = null, onSave = null}) {
        this.tuneName = name;
        this.icon = icon;
        this.description = description;
        this.api = null;
        this.config = null;
        this.tool = null;

        if (action) {
            action = action.bind(this);
            this.onEvent = action;
        }
        if (initialize) {
            initialize = initialize.bind(this);
            this.initialize = initialize;
        }
        if (isActive) {
            isActive = isActive.bind(this);
            this.isActive = isActive;
        }
        if (getState) {
            getState = getState.bind(this);
            this.getState = getState;
        }
        if (render) {
            render = render.bind(this);
            this.render = render;
        }
        if (onSave) {
            onSave = onSave.bind(this);
            this.onSave = onSave;
        }
    }

    setTool(api, config, tool) {
        this.api = api;
        this.config = config;
        this.tool = tool;
    }

    initialize() {

    }


    onEvent(e) {

    }

    isActive() {

    }

    render() {

    }

    getState() {

    }

    onSave() {
        this.tool.block.dispatchChange();
        return this.getState();
    }
}


class BaseButtonSetting extends BaseToolSetting {
    setTool(api, config, tool) {
        super.setTool(api, config, tool);
        console.log('setTool', this.tool);
    }

    isActive() {
        return false;
    }
    
    getState() {
        return undefined;
    }

    render() {
        this.button = document.createElement('div');
        this.button.classList.add('cdx-settings-button');
        this.button.innerHTML = this.icon;
        this.button.onclick = this.onEvent.bind(this);
        return this.button;
    }
}


class BaseToggleSetting extends BaseToolSetting {
    onEvent(e) {
        this.tool.data[this.tuneName] = !this.tool.data[this.tuneName];
        const isActive = this.isActive();
        this.tool.wrapperElement.classList.toggle(this.tuneName, isActive);
        this.tool.refreshActiveTunes();
        super.onEvent(e);
    }

    initialize() {
        this.tool.wrapperElement.classList.toggle(this.tuneName, this.isActive());
        super.initialize();
    }

    render() {
        const button = document.createElement('div');
        button.classList.add('cdx-settings-button');
        button.classList.toggle('cdx-settings-button--active', this.isActive());
        button.innerHTML = this.icon;
        button.addEventListener('click', () => {
            this.onEvent();
            button.classList.toggle('cdx-settings-button--active', this.isActive());
        });
        return button;
    }

    isActive() {
        return !!this.tool.data[this.tuneName] || super.isActive();
    }

    getState() {
        return this.isActive();
    }
}

class BaseInputSetting extends BaseToolSetting {
    constructor(tuneName, iconName, inputType = 'text', onEvent = null, inputAttrs = null) {
        if (!inputAttrs) {
            inputAttrs = {};
        }
        super(tuneName, iconName, onEvent);
        this.inputType = inputType;
    }
    
    onEvent(e) {
        if (e.keyCode === 13) { // Enter key
            this.tool.data[this.tuneName] = e.target.value;
            this.onSave();
        }
    }

    get inputElementTag() {
        return 'input';
    }

    render() {
        const input = document.createElement(this.inputElementTag);
        const keys = Object.keys(this.inputAttrs);
        for (let i = 0; i < keys.length; i++) {
            const key = keys[i];
            input.setAttribute(key, this.inputAttrs[key]);
        }

        input.classList.add('cdx-settings-input');
        input.type = this.inputType;
        input.value = this.tool.data[this.tuneName] || '';

        input.onkeydown = this.onEvent.bind(this);
        
        return input;
    }

    isActive() {
        return (
            this.tool.data[this.tuneName] !== undefined ||
            this.tool.data[this.tuneName] !== null ||
            this.tool.data[this.tuneName] !== ''
        )
    }

    getState() {
        return this.tool.data[this.tuneName];
    }
}


class BaseSelectInputSetting extends BaseInputSetting {
    get options() {
        throw new Error('options must be implemented by subclasses');
    }

    get inputElementTag() {
        return 'select';
    }

    onEvent(e) {
        this.tool.data[this.tuneName] = e.target.value;
        this.onSave();
    }

    render() {
        const select = super.render();
        delete select.onkeydown;
        select.onchange = this.onEvent.bind(this);
        this.options.forEach(option => {
            const optionElement = document.createElement('option');
            optionElement.value = option.value;
            optionElement.text = option.text;
            select.appendChild(optionElement);
        });
        return select;
    }
}



class BaseWagtailEditorJSTool {
    constructor({ data, api, config, block }) {
        this.data = data;
        this.api = api;
        this.block = block;
        this.config = config;
        /** @type {BaseToolSetting[]} */
        this.settings = [];

        if (!"settings" in this.data || !this.data.settings) {
            this.data.settings = {};
        }
    }
    
    static get toolbox() {
        throw new Error('toolbox must be implemented by subclasses');
    }

    get wrapperElement() {
        if (!this._wrapperElement) {
            throw new Error('wrapperElement must be set by subclasses before calling `super.render()`!');
        }

        return this._wrapperElement;
    }

    set wrapperElement(wrapperElement) {
        this._wrapperElement = wrapperElement;
    }

    initSettings() {
        for (let i = 0; i < this.settings.length; i++) {
            this.settings[i].setTool(this.api, this.config, this);
        }
    }

    render(){
        setTimeout(() => {
            this.settings.forEach( tune => {
                if (tune.initialize) {
                    tune.initialize();
                }
            });
        }, 0);

        this.refreshActiveTunes();

        return this.wrapperElement;
    }
  
    save(blockContent){
        const data = {
            ...this.data,
            settings: {},
        };

        for (let i = 0; i < this.settings.length; i++) {
            const tune = this.settings[i];
            const tuneState = tune.onSave();
            if (tuneState !== undefined) {
                data["settings"][tune.tuneName] = tuneState;
            }
        }

        return data;

    }

    renderSettings(){
        const wrapper = document.createElement('div');

        this.settings.forEach( tune => {
            const rendered = tune.render();

            if (rendered) {
                let description = tune.description;
                if (!description) {
                    description = tune.tuneName;
                }
                this.api.tooltip.onHover(rendered, description, {
                    placement: 'top',
                    offset: 5,
                    hidingDelay: 200,
                });
                wrapper.appendChild(rendered);
            }
        });
    
        return wrapper;
    }

    refreshActiveTunes() {
        for (let i = 0; i < this.settings.length; i++) {
            const tune = this.settings[i];
            this.wrapperElement.classList.toggle(tune.name, tune.isActive());
        }
    }
}


class _ElementType extends HTMLElement {
    /**
     * @param {Union<string, HTMLElement, NodeList>} child
     * @returns {HTMLElement}
     */
    addChild(child) {}

    /**
     * @param {String} tag
     * @param {Object} attributes
     * @param {Union<string, HTMLElement, NodeList>} children
     * @returns {_ElementType}
     */
    addElement(tag, attributes = {}, ...children) {}
}


/**
* @param {String} tag
* @param {Object} attributes
* @param {Union<string, HTMLElement, NodeList>} children
* @returns {_ElementType}
*/
function makeElement(tag, attributes = {}, ...children) {
    let element = document.createElement(tag);
    element = addAttributeData(element, attributes);
    element = makeElementType(element);
    
    for (let i = 0; i < children.length; i++) {
        element.addChild(children[i]);
    }

    return element
}

/**
 * @param {HTMLElement} element
 * @returns {_ElementType}
 */
function makeElementType(element) {

    const addChild = (child) => {
        let childElement;
        if (typeof child === 'string') {
            childElement = document.createTextNode(child);
        } else if (child instanceof HTMLElement) {
            childElement = child;
        } else if ("render" in child) {
            childElement = child.render();
        }

        element.appendChild(
            makeElementType(childElement)
        )

        return childElement
    };

    const addElement = (tag, attributes = {}, ...children) => {
        let child = makeElement(tag, attributes, ...children);
        return element.addChild(child)
    };

    element.addElement = addElement;
    element.addChild = addChild;

    return element
}

/**
 * @param {HTMLElement} element
 * @param {Object} attributes
 * @returns {HTMLElement}
 */
function addAttributeData(element, attributes) {
    const {
        classes = [],
        id = null,
        style = null,
        data = {},
        events = {},
    } = attributes;

    attributes = Object.assign({}, attributes);
    if ("classes" in attributes) {
        delete attributes.classes;
    }
    if ("id" in attributes) {
        delete attributes.id;
    }
    if ("style" in attributes) {
        delete attributes.style;
    }
    if ("data" in attributes) {
        delete attributes.data;
    }
    if ("events" in attributes) {
        delete attributes.events;
    }

    
    if (classes && !Array.isArray(classes)) {
        classes = [classes];
    };

    element.classList.add(...classes);

    if (id) {
        element.id = id;
    }

    if (style) {
        element.style = style;
    }


    const dataKeys = Object.keys(data);
    const eventKeys = Object.keys(events);
    const attrKeys = Object.keys(attributes);

    for (let i = 0; i < dataKeys.length; i++) {
        const key = dataKeys[i];
        element.dataset[key] = data[key];
    }

    for (let i = 0; i < eventKeys.length; i++) {
        const key = eventKeys[i];
        element.addEventListener(key, events[key].bind(element));
    }

    for (let i = 0; i < attrKeys.length; i++) {
        const key = attrKeys[i];
        element[key] = attributes[key];
    }

    return element;
}

window.BaseWagtailEditorJSTool = BaseWagtailEditorJSTool;
window.BaseToggleSetting = BaseToggleSetting;
window.BaseButtonSetting = BaseButtonSetting;
window.BaseInputSetting = BaseInputSetting;
window.BaseSelectInputSetting = BaseSelectInputSetting;
window.BaseToolSetting = BaseToolSetting;
window.makeElement = makeElement;
window._ElementType = _ElementType;
window.addAttributeData = addAttributeData;
window.makeElementType = makeElementType;

