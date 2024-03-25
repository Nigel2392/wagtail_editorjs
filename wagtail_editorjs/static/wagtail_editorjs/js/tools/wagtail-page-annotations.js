// BaseToolSetting
// SimpleToggleSetting
// InputSetting
// SelectInputSetting
// BaseWagtailEditorJSTool
// makeElement




class PageAnnotationTool extends window.BaseWagtailEditorJSTool {
    constructor({ data, api, config, block }) {
        super({ data, api, config, block });

        if (!config.iframeURL) {
            console.error('iframeURL is highly recommended');
            const previewSidePanel = document.querySelector(
                '[data-side-panel="preview"]',
            );
    
            // Preview side panel is not shown if the object does not have any preview modes
            if (!previewSidePanel) return;
    
            const previewPanel = previewSidePanel.querySelector('[data-preview-panel]');
            const previewUrl = previewPanel.dataset.action;
                
            config.iframeURL = previewUrl;
        }

        this.html2canvasConfig = {
        }
    }

    static get toolbox() {
        return {
            title: 'Page Annotation',
            icon: '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="feather feather-edit-3"><path d="M12 20h9"></path><path d="M16 4l4 4-4 4"></path><path d="M8 14L4 10l4-4"></path><path d="M4 10h12"></path></svg>',
        };
    }

    render() {
        this.wrapperElement = window.makeElement('div', {
            className: 'wagtail-page-annotation-wrapper',
        });

        this.iFrameWrapperElement = this.wrapperElement.addElement('div', {
            className: 'wagtail-page-annotation-iframe-wrapper',
        });

        const mouseCoords = { 
            x: 0, y: 0, r: 0,
            moving: false,

            xPerc: 0,
            yPerc: 0,
            rPerc: 0,
        };

        const noSelectCss = `.wagtail-page-annotation-iframe-body {
            box-sizing: border-box;
        }
        .wagtail-page-annotation-iframe-body *:not(.wagtail-page-annotation-iframe-clicked, :has(*:hover)):is(:hover),
        .wagtail-page-annotation-iframe-body .wagtail-page-annotation-iframe-clicked {
            box-shadow: 0 0 3px 3px rgba(255, 0, 0, 0.5);
        }`;

        this.iFrameElement = this.iFrameWrapperElement.addElement('iframe', {
            className: 'wagtail-page-annotation-iframe',
            src: this.config.iframeURL,
            width: '100%',
            height: '100%',
            events: {
                load: (e) => {
                    const iFrame = e.target;
                    const iFrameDocument = iFrame.contentWindow.document;

                    const style = iFrameDocument.createElement('style');
                    style.textContent = noSelectCss;
                    iFrameDocument.head.appendChild(style);
                    iFrameDocument.body.classList.add('wagtail-page-annotation-iframe-body');

                    iFrameDocument.body.addEventListener('click', (e) => {
                        e.preventDefault();
                        e.stopPropagation();
                        let chosenElement = e.target;
                        if (chosenElement.classList.contains('wagtail-page-annotation-iframe-clicked')) {
                            chosenElement.classList.remove('wagtail-page-annotation-iframe-clicked');
                            chosenElement.style.border = '';
                            chosenElement.style.borderRadius = '';
                            chosenElement.contentEditable = false;
                        } else {
                            chosenElement.classList.add('wagtail-page-annotation-iframe-clicked');
                            chosenElement.style.border = '3px solid red';
                            chosenElement.style.borderRadius = '5px';
                            chosenElement.contentEditable = true;
                            chosenElement.focus();
                        }
                    });

                }
            }
        });

        const scale = 0.75;
        this.iFrameElement.style.transform = `scale(${scale})`;
        this.iFrameElement.style.transformOrigin = '0 0';
        this.iFrameElement.style.width = `${100 / scale}%`;
        this.iFrameElement.style.height = '500px';
        this.iFrameElement.style.marginBottom = `-${500 * (1 - scale)}px`;
        // this.iFrameElement.style.marginBottom = `-${100 * (1 - scale)}%`

        super.render();

        this.iFrameWrapperElement.addElement('div', {
            className: 'wagtail-page-annotation-iframe-buttons',
        })

        this.screenShotButton = this.wrapperElement.addElement('button', {
            textContent: this.api.i18n.t('Take Screenshot'),
            type: 'button',
            events: {
                click: (e) => {
                    e.preventDefault();
                    e.stopPropagation();
                    e.target.disabled = true;
                    const iframeBody = this.iFrameElement.contentWindow.document.body;
                    const backgroundColor = window.getComputedStyle(iframeBody).backgroundColor;

                    this.html2canvasConfig = {
                        scale: scale,
                        useCORS: true,
                        allowTaint: true,
                        logging: false,
                        scrollX: -this.iFrameElement.contentWindow.scrollX,
                        scrollY: -this.iFrameElement.contentWindow.scrollY,

                        windowWidth: this.iFrameElement.contentWindow.innerWidth,
                        windowHeight: this.iFrameElement.contentWindow.innerHeight,

                        x: 0,
                        y: 0,
                        width: this.iFrameElement.contentWindow.innerWidth,
                        height: this.iFrameElement.contentWindow.innerHeight,
                        backgroundColor: backgroundColor,

                        onclone: (doc) => {
                            const style = doc.createElement('style');
                            style.textContent = noSelectCss;
                            doc.head.appendChild(style);
                            doc.body.classList.add(
                                'wagtail-page-annotation-iframe-body',
                                'wagtail-page-annotation-iframe-processed'
                            );
                        }
                    };

                    this.iFrameWrapperElement.classList.add(
                        'loading',
                        'loading-mask',
                    )
                    
                    html2canvas(this.iFrameElement.contentWindow.document.body, this.html2canvasConfig).then(canvas => {
                        const img = document.createElement('img');
                        img.src = canvas.toDataURL();
                        img.style.width = '0';
                        img.style.height = '0';
                        img.onload = () => {
                            e.target.style.display = 'none';
                            this.RetakeScreenshotButton.style.display = '';
                            this.iFrameElement.dataset.scrollX = this.iFrameElement.contentWindow.scrollX;
                            this.iFrameElement.dataset.scrollY = this.iFrameElement.contentWindow.scrollY;
                            this.iFrameElement.style.display = 'none';
                            this.iFrameWrapperElement.classList.remove(
                                'loading-mask',
                            );
                            img.style.width = '100%';
                            img.style.height = 'auto';

                        };
                        this.iFrameWrapperElement.appendChild(img);
                    });
                }
            }
        });

        this.RetakeScreenshotButton = this.wrapperElement.addElement('button', {
            textContent: this.api.i18n.t('Retake Screenshot'),
            type: 'button',
            style: 'display: none',
            events: {
                click: (e) => {
                    e.preventDefault();
                    e.stopPropagation();
                    this.iFrameElement.style.display = '';
                    this.screenShotButton.disabled = false;
                    this.screenShotButton.style.display = '';
                    this.RetakeScreenshotButton.style.display = 'none';
                    this.iFrameWrapperElement.querySelector('img').remove();
                    this.iFrameElement.contentWindow.scrollTo(
                        this.iFrameElement.dataset.scrollX,
                        this.iFrameElement.dataset.scrollY,
                    );
                }
            }
        });

        return this.wrapperElement;
    }

    save(blockContent) {
        return {
            text: blockContent.innerHTML,
        };
    }
}

window.PageAnnotationTool = PageAnnotationTool;