const wagtailFileIcon = `<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-file-earmark-arrow-down" viewBox="0 0 16 16">
    <!-- The MIT License (MIT) -->
    <!-- Copyright (c) 2011-2024 The Bootstrap Authors -->
    <path d="M8.5 6.5a.5.5 0 0 0-1 0v3.793L6.354 9.146a.5.5 0 1 0-.708.708l2 2a.5.5 0 0 0 .708 0l2-2a.5.5 0 0 0-.708-.708L8.5 10.293z"/>
    <path d="M14 14V4.5L9.5 0H4a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h8a2 2 0 0 0 2-2M9.5 3A1.5 1.5 0 0 0 11 4.5h2V14a1 1 0 0 1-1 1H4a1 1 0 0 1-1-1V2a1 1 0 0 1 1-1h5.5z"/>
</svg>`;



class WagtailDocumentTool extends window.BaseWagtailChooserTool {
    get iconHTML() {
        return wagtailFileIcon;
    }

    static get chooserType() {
        return 'document';
    }

    newChooser() {
        return new window.DocumentChooser(this.config.chooserId)
    }

    showActions(wrapperTag) {
        this.URLInput.value = wrapperTag.href;

        let chooseNewFunc = null;
        chooseNewFunc = (e) => {
            const data = this.chooser.state;
            this.setDataOnWrapper(wrapperTag, data);
            this.URLInput.value = data.url;
            this.chooser.input.removeEventListener('change', chooseNewFunc);
        };

        this.chooseNewButton.onclick = (() => {
            this.chooser.openChooserModal();
            this.chooser.input.addEventListener('change', chooseNewFunc);
        });
        
        this.api.tooltip.onHover(this.chooseNewButton, this.api.i18n.t('Choose new ' + this.constructor["chooserType"]), {
            placement: 'top',
            hidingDelay: 200,
        });


        this.container.hidden = false;


    }
    
    hideActions() {
        this.container.hidden = true;
        this.URLInput.value = '';
        this.URLInput.onchange = null;
        this.chooseNewButton.onclick = null;
        this.chooseNewButton.classList.remove(
            this.api.styles.inlineToolButtonActive
        );
    }
    
    renderActions() {
        this.container = document.createElement('div');
        this.container.classList.add("wagtail-link-tool-actions", "column");
        this.container.hidden = true;

        const btnContainer = document.createElement('div');
        btnContainer.classList.add("wagtail-link-tool-actions");

        this.chooseNewButton = document.createElement('button');
        this.chooseNewButton.type = 'button';
        this.chooseNewButton.innerHTML = wagtailFileIcon;
        this.chooseNewButton.dataset.chooserActionChoose = 'true';
        this.chooseNewButton.classList.add(
            this.api.styles.inlineToolButton,
        )

        this.URLInput = document.createElement('input');
        this.URLInput.type = 'text';
        this.URLInput.disabled = true;
        this.URLInput.placeholder = this.api.i18n.t('URL');
        this.URLInput.classList.add(
            this.api.styles.input,
            this.api.styles.inputUrl,
        );

        btnContainer.appendChild(this.URLInput);
        btnContainer.appendChild(this.chooseNewButton);

        this.container.appendChild(btnContainer);

        return this.container;
    }
}

window.WagtailDocumentTool = WagtailDocumentTool;