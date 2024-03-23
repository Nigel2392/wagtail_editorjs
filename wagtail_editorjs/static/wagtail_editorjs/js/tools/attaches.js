class CSRFAttachesTool extends window.AttachesTool {
    constructor({ data, config, api, readOnly }) {
        config['additionalRequestHeaders'] = {
            'X-CSRFToken': document.querySelector('input[name="csrfmiddlewaretoken"]').value
        };
        super({ data, config, api, readOnly });
    }
}

window.CSRFAttachesTool = CSRFAttachesTool;